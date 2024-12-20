import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
import streamlit as st
import asyncio
import httpx
import os

DATA_DIR = "data"  # 데이터 저장 디렉토리


# 비동기 데이터 수집
async def fetch_symbol_list():
    """거래소에서 모든 심볼 목록 가져오기"""
    base_url = "https://api.bithumb.com/public/ticker/ALL_KRW"
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '0000':
                return [f"{symbol}_KRW" for symbol in data['data'].keys() if symbol != 'date']
    return []

async def fetch_symbol_data_async(symbol, timeframe="24h"):
    """비동기로 심볼 데이터 가져오기"""
    base_url = "https://api.bithumb.com/public/candlestick"
    url = f"{base_url}/{symbol}/{timeframe}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '0000':
                df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')

                # 숫자형 변환
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # 결측값 제거
                return df.dropna()
    return None

async def fetch_all_symbols_data(symbols, timeframe="24h"):
    """모든 심볼 데이터를 비동기로 수집"""
    tasks = [fetch_symbol_data_async(symbol, timeframe) for symbol in symbols]
    return await asyncio.gather(*tasks)

def calculate_technical_indicators(df):
    """모든 기술적 지표 계산"""
    df = df.copy()

    # 기본 가격 지표 - 이동평균선
    for period in [5, 10, 20, 50, 200]:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()

    # RSI 계산
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    # MACD 계산
    df['MACD_Line'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
    df['Signal_Line'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()

    # 볼린저 밴드 계산
    df['BB_Middle'] = df['close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['close'].rolling(window=20).std()

    # 스토캐스틱 오실레이터 계산
    low_min = df['low'].rolling(window=14).min()
    high_max = df['high'].rolling(window=14).max()
    df['%K'] = ((df['close'] - low_min) / (high_max - low_min)) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()

    # 거래량 관련 지표
    df['Volume_MA'] = df['volume'].rolling(window=20).mean()
    df['Volume_STD'] = df['volume'].rolling(window=20).std()
    df['Volume_Zscore'] = (df['volume'] - df['Volume_MA']) / df['Volume_STD']
    df['Volume_Momentum'] = df['volume'].pct_change(5)

    # 심리 지표 (임의 값 설정)
    df['Fear_Greed'] = 50 + (df['RSI'] - 50) / 50 * 20  # RSI를 기반으로 계산
    df['Fear_Greed'] = df['Fear_Greed'].clip(0, 100)

    # 모멘텀 지표
    df['Efficiency_Ratio'] = abs(df['close'] - df['close'].shift(14)) / \
                             (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min())

    # 결측값 처리
    df = df.fillna(0)
    return df

class KNNPredictor:
    def __init__(self, n_neighbors=5):
        self.knn = KNeighborsRegressor(n_neighbors=n_neighbors)
        self.scaler = StandardScaler()

    def prepare_features(self, df):
        """KNN용 특징 생성"""
        df = calculate_technical_indicators(df)
        features = df[['RSI', 'MACD_Line', 'Signal_Line', 'BB_Upper', 'BB_Lower', '%K', '%D',
                       'Volume_Momentum', 'Fear_Greed', 'Efficiency_Ratio']].fillna(0)
        return features

    def train(self, df):
        """KNN 모델 학습"""
        features = self.prepare_features(df)
        target = df['close'].pct_change().shift(-1).iloc[:-1]
        features = features.iloc[:-1]

        valid = ~(pd.isna(target) | np.isinf(target))
        features = features[valid]
        target = target[valid]

        if len(features) < 2:
            raise ValueError("학습 데이터가 너무 적습니다.")

        self.knn.n_neighbors = min(self.knn.n_neighbors, len(features))

        self.features = self.scaler.fit_transform(features)
        self.target = target

        if len(self.features) > 0:
            self.knn.fit(self.features, self.target)

    def predict(self, df):
        """KNN 예측"""
        features = self.prepare_features(df)
        features_scaled = self.scaler.transform(features)
        return self.knn.predict(features_scaled[-1:])[0]

def analyze_with_knn(df):
    """KNN 분석 실행"""
    knn_predictor = KNNPredictor(n_neighbors=5)

    try:
        knn_predictor.train(df)
        prediction = knn_predictor.predict(df)

        if prediction > 0.02:
            return "매수 신호", f"예상 상승률: {prediction * 100:.2f}%"
        elif prediction < -0.02:
            return "매도 신호", f"예상 하락률: {prediction * 100:.2f}%"
        else:
            return "중립 신호", f"예상 변동률: {prediction * 100:.2f}%"
    except ValueError as e:
        return "데이터 부족", str(e)
