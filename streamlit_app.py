import streamlit as st
import graphviz
import pandas as pd

def create_extended_family_tree():
    st.set_page_config(page_title="한국식 족보 시각화", layout="wide")
    st.title("한국식 가족 관계도 (확장판)")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["관계도 시각화", "촌수별 호칭 편집"])
    
    with tab1:
        # 사이드바 컨트롤
        st.sidebar.title("세대 및 관계 선택")
        show_options = {
            "직계존속": st.sidebar.checkbox("직계존속 보기 (증조/고조까지)", True),
            "방계존속": st.sidebar.checkbox("방계존속 보기 (백부/숙부/고모 등)", True),
            "동세대": st.sidebar.checkbox("동세대 보기 (형제/자매/사촌 등)", True),
            "직계비속": st.sidebar.checkbox("직계비속 보기 (자녀/손자 등)", True),
            "방계비속": st.sidebar.checkbox("방계비속 보기 (조카/종손 등)", True)
        }
        
        # 기본 친족 관계 데이터
        default_relations = {
            "촌수": list(range(1, 11)),
            "부계": [
                "아버지",
                "할아버지",
                "증조할아버지",
                "고조할아버지",
                "5대조할아버지",
                "6대조할아버지",
                "7대조할아버지",
                "8대조할아버지",
                "9대조할아버지",
                "10대조할아버지"
            ],
            "모계": [
                "어머니",
                "외할아버지",
                "외증조할아버지",
                "외고조할아버지",
                "외5대조할아버지",
                "외6대조할아버지",
                "외7대조할아버지",
                "외8대조할아버지",
                "외9대조할아버지",
                "외10대조할아버지"
            ]
        }
        
        # 세션 스테이트에서 관계 데이터 불러오기 또는 초기화
        if 'relations_df' not in st.session_state:
            st.session_state.relations_df = pd.DataFrame(default_relations)
        
        # 그래프 생성
        graph = graphviz.Digraph()
        graph.attr(rankdir='TB')
        graph.attr('node', shape='box', style='filled', fillcolor='lightblue')
        
        # 자신 노드 생성
        graph.node('me', '나', fillcolor='lightgreen')
        
        # 선택된 옵션에 따라 노드와 엣지 생성
        if show_options["직계존속"]:
            for i in range(1, 5):  # 4대까지만 표시
                node_id = f'ancestor_{i}'
                graph.node(node_id, st.session_state.relations_df.loc[i-1, '부계'])
                if i == 1:
                    graph.edge(node_id, 'me')
                else:
                    graph.edge(node_id, f'ancestor_{i-1}')
        
        if show_options["방계존속"]:
            # 백부/숙부/고모 노드
            relations = ['백부', '숙부', '고모']
            for rel in relations:
                graph.node(f'relative_{rel}', rel)
                graph.edge('ancestor_1', f'relative_{rel}')
        
        if show_options["동세대"]:
            # 형제/자매/사촌 노드
            siblings = ['형', '누나', '동생']
            for sib in siblings:
                graph.node(f'sibling_{sib}', sib)
                graph.edge('ancestor_1', f'sibling_{sib}')
        
        # 그래프 표시
        st.graphviz_chart(graph)
    
    with tab2:
        st.header("촌수별 호칭 편집")
        
        # 데이터프레임 편집 기능
        edited_df = st.data_editor(
            st.session_state.relations_df,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # 변경사항 저장
        if st.button("변경사항 저장"):
            st.session_state.relations_df = edited_df
            st.success("저장되었습니다!")
        
        # 호칭 설명
        st.markdown("""
        ### 촌수 계산 방법
        1. 직계: 자신부터 시작해서 위로 올라가거나 아래로 내려가면서 계산
        2. 방계: 공동 조상까지 올라갔다가 다시 내려오면서 계산
        
        ### 주요 호칭 설명
        - 1촌: 부모, 자녀
        - 2촌: 조부모, 손자녀, 형제자매
        - 3촌: 증조부모, 증손자녀, 백부/숙부/고모
        - 4촌: 고조부모, 고손자녀, 사촌
        - 5촌: 5대조부모, 5대손, 오촌
        - 6촌: 6대조부모, 6대손, 육촌
        - 7촌: 7대조부모, 7대손, 칠촌
        - 8촌: 8대조부모, 8대손, 팔촌
        - 9촌: 9대조부모, 9대손, 구촌
        - 10촌: 10대조부모, 10대손, 십촌
        
        ### 참고사항
        - 외가 친족은 호칭 앞에 '외'를 붙임
        - 고모의 자녀는 '고종사촌'
        - 이모의 자녀는 '이종사촌'
        - 외삼촌의 자녀는 '외종사촌'
        """)

if __name__ == "__main__":
    create_extended_family_tree()
