import streamlit as st
import graphviz

def create_family_tree():
    # Streamlit 앱 제목 설정
    st.title('가계도 생성기')
    
    # Graphviz 객체 생성
    graph = graphviz.Digraph('family_tree', comment='Family Tree')
    graph.attr(rankdir='TB')
    
    # 노드 스타일 설정
    graph.attr('node', shape='rectangle', style='filled', fillcolor='lightblue')
    
    # 가족 구성원 입력 섹션
    st.subheader('가족 구성원 추가')
    
    # 새로운 가족 구성원 입력
    name = st.text_input('이름')
    parent_name = st.text_input('부모 이름 (없으면 비워두세요)')
    
    if st.button('가족 구성원 추가'):
        if name:
            # 세션 상태에 가족 구성원 저장
            if 'family_members' not in st.session_state:
                st.session_state.family_members = {}
            
            st.session_state.family_members[name] = parent_name
            st.success(f'{name} 추가됨!')
    
    # 가계도 그리기
    if 'family_members' in st.session_state and st.session_state.family_members:
        st.subheader('가계도')
        
        # 모든 노드 추가
        for member in st.session_state.family_members:
            graph.node(member)
        
        # 관계 연결
        for child, parent in st.session_state.family_members.items():
            if parent:  # 부모가 있는 경우에만 연결
                graph.edge(parent, child)
        
        # 그래프 표시
        st.graphviz_chart(graph)
    
    # 초기화 버튼
    if st.button('가계도 초기화'):
        st.session_state.family_members = {}
        st.success('가계도가 초기화되었습니다.')

if __name__ == '__main__':
    create_family_tree()
