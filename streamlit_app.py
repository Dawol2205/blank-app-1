import streamlit as st
import graphviz
import pandas as pd

def get_title(from_gender, to_gender, relation_type):
    """기본적인 가족 호칭을 반환합니다."""
    titles = {
        'parent': {
            '남성': '아버지',
            '여성': '어머니'
        },
        'child': {
            '남성': '아들',
            '여성': '딸'
        },
        'spouse': {
            '남성': '남편',
            '여성': '아내'
        },
        'sibling': {
            '남성': '오빠/형',
            '여성': '언니/누나'
        }
    }
    return titles.get(relation_type, {}).get(to_gender, '친척')

def create_family_tree():
    st.title('가계도 생성기')
    
    # 초기 상태 설정
    if 'members' not in st.session_state:
        st.session_state.members = {}

    # 입력 폼
    with st.form("member_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('이름')
            gender = st.selectbox('성별', ['남성', '여성'])
        with col2:
            parent = st.text_input('부모 이름 (선택)')
            spouse = st.text_input('배우자 이름 (선택)')
        
        submitted = st.form_submit_button("추가")
        if submitted and name:
            st.session_state.members[name] = {
                'gender': gender,
                'parent': parent if parent else None,
                'spouse': spouse if spouse else None
            }
            st.success(f'{name} 추가됨!')

    # 가계도 표시
    if st.session_state.members:
        st.subheader('가계도')
        
        # 기준 인물 선택
        reference = st.selectbox(
            '기준 인물 선택',
            list(st.session_state.members.keys())
        )
        
        # 그래프 생성
        dot = graphviz.Digraph()
        dot.attr(rankdir='TB')
        
        # 노드 추가
        for name, info in st.session_state.members.items():
            # 노드 색상 설정
            color = 'lightblue' if info['gender'] == '남성' else 'pink'
            
            # 호칭 계산
            title = ""
            if name == reference:
                title = "본인"
            elif info['parent'] == reference:
                title = get_title('parent', info['gender'], 'child')
            elif st.session_state.members.get(reference, {}).get('parent') == name:
                title = get_title('child', info['gender'], 'parent')
            elif info['spouse'] == reference or st.session_state.members.get(reference, {}).get('spouse') == name:
                title = get_title('spouse', info['gender'], 'spouse')
            
            # 레이블 생성
            label = f"{name}\n({info['gender']})"
            if title:
                label += f"\n{title}"
            
            dot.node(name, label, style='filled', fillcolor=color)
        
        # 관계선 추가
        for name, info in st.session_state.members.items():
            # 부모-자식 관계
            if info['parent'] and info['parent'] in st.session_state.members:
                dot.edge(info['parent'], name)
            
            # 배우자 관계
            if info['spouse'] and info['spouse'] in st.session_state.members:
                if name < info['spouse']:  # 중복 방지
                    dot.edge(name, info['spouse'], dir='none', style='dashed', color='red')
        
        st.graphviz_chart(dot)

        # 구성원 목록 표시
        st.subheader('등록된 구성원')
        df = pd.DataFrame.from_dict(st.session_state.members, orient='index')
        st.dataframe(df)

    # 초기화 버튼
    if st.button('초기화'):
        st.session_state.members = {}
        st.success('가계도가 초기화되었습니다.')

if __name__ == '__main__':
    create_family_tree()
