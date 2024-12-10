import streamlit as st
import graphviz

def create_family_tree():
    # 스트림릿 페이지 설정
    st.set_page_config(page_title="한국식 족보 시각화", layout="wide")
    st.title("한국식 가족 관계도")
    
    # 사이드바에서 세대 선택
    st.sidebar.title("세대 선택")
    show_parents = st.sidebar.checkbox("부모님 세대 보기", True)
    show_siblings = st.sidebar.checkbox("형제자매 보기", True)
    show_cousins = st.sidebar.checkbox("사촌 보기", True)
    show_children = st.sidebar.checkbox("자녀 세대 보기", True)

    # 그래프 생성
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB')
    
    # 노드 스타일 설정
    graph.attr('node', shape='box', style='filled', fillcolor='lightblue')
    
    # 부모님 세대
    if show_parents:
        # 조부모
        graph.node('grandfather_f', '할아버지(친가)')
        graph.node('grandmother_f', '할머니(친가)')
        graph.node('grandfather_m', '외할아버지')
        graph.node('grandmother_m', '외할머니')
        
        # 부모님
        graph.node('father', '아버지')
        graph.node('mother', '어머니')
        graph.node('uncle1', '큰아버지')
        graph.node('uncle2', '작은아버지')
        graph.node('aunt1', '고모')
        graph.node('maternal_uncle', '외삼촌')
        graph.node('maternal_aunt', '이모')
        
        # 조부모-부모 관계
        graph.edge('grandfather_f', 'father')
        graph.edge('grandmother_f', 'father')
        graph.edge('grandfather_f', 'uncle1')
        graph.edge('grandmother_f', 'uncle1')
        graph.edge('grandfather_f', 'uncle2')
        graph.edge('grandmother_f', 'uncle2')
        graph.edge('grandfather_f', 'aunt1')
        graph.edge('grandmother_f', 'aunt1')
        
        graph.edge('grandfather_m', 'mother')
        graph.edge('grandmother_m', 'mother')
        graph.edge('grandfather_m', 'maternal_uncle')
        graph.edge('grandmother_m', 'maternal_uncle')
        graph.edge('grandfather_m', 'maternal_aunt')
        graph.edge('grandmother_m', 'maternal_aunt')

    # 자신
    graph.node('me', '나', fillcolor='lightgreen')
    if show_parents:
        graph.edge('father', 'me')
        graph.edge('mother', 'me')

    # 형제자매
    if show_siblings:
        graph.node('older_brother', '형/오빠')
        graph.node('older_sister', '누나/언니')
        graph.node('younger_brother', '남동생')
        graph.node('younger_sister', '여동생')
        
        if show_parents:
            graph.edge('father', 'older_brother')
            graph.edge('mother', 'older_brother')
            graph.edge('father', 'older_sister')
            graph.edge('mother', 'older_sister')
            graph.edge('father', 'younger_brother')
            graph.edge('mother', 'younger_brother')
            graph.edge('father', 'younger_sister')
            graph.edge('mother', 'younger_sister')

    # 사촌
    if show_cousins:
        # 친가 사촌
        graph.node('paternal_cousin1', '친가 사촌(큰집)')
        graph.node('paternal_cousin2', '친가 사촌(작은집)')
        graph.node('cousin_aunt', '고종사촌')
        
        # 외가 사촌
        graph.node('maternal_cousin1', '외사촌(외삼촌)')
        graph.node('maternal_cousin2', '외사촌(이모)')
        
        if show_parents:
            graph.edge('uncle1', 'paternal_cousin1')
            graph.edge('uncle2', 'paternal_cousin2')
            graph.edge('aunt1', 'cousin_aunt')
            graph.edge('maternal_uncle', 'maternal_cousin1')
            graph.edge('maternal_aunt', 'maternal_cousin2')

    # 자녀 세대
    if show_children:
        graph.node('son', '아들')
        graph.node('daughter', '딸')
        graph.edge('me', 'son')
        graph.edge('me', 'daughter')

    # 그래프 렌더링
    st.graphviz_chart(graph)

    # 관계 설명
    st.header("가족 관계 설명")
    st.write("""
    ### 기본 호칭 정리
    - 부모님 호칭: 아버지(아빠), 어머니(엄마)
    - 형제자매 호칭:
        * 남자: 형(친형), 동생(남동생)
        * 여자: 오빠(친오빠), 언니(친언니), 동생(여동생)
    
    ### 친가 호칭
    - 할아버지, 할머니
    - 큰아버지(백부), 작은아버지(숙부)
    - 고모
    - 사촌형제: 친사촌(從姉妹)
    
    ### 외가 호칭
    - 외할아버지, 외할머니
    - 외삼촌(외숙부)
    - 이모
    - 외사촌
    """)

if __name__ == "__main__":
    create_family_tree()
