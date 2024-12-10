import streamlit as st
import graphviz
import pandas as pd

class FamilyMember:
    def __init__(self, name, gender, parent_name=None, spouse_name=None):
        self.name = name
        self.gender = gender
        self.parent_name = parent_name
        self.spouse_name = spouse_name

def get_relationship_name(distance_up, distance_down):
    """친족 관계에 따른 호칭을 반환합니다."""
    relationship_names = {
        (1, 0): "부모",
        (2, 0): "조부모",
        (3, 0): "증조부모",
        (4, 0): "고조부모",
        (0, 1): "자녀",
        (0, 2): "손자녀",
        (0, 3): "증손자녀",
        (0, 4): "고손자녀",
        (1, 1): "형제자매",
        (2, 1): "백부/숙부",
        (1, 2): "조카",
        (2, 2): "사촌",
        (3, 1): "종증조부",
        (1, 3): "종손자",
        (3, 2): "종조카",
        (2, 3): "사촌조카",
        (3, 3): "사촌손자"
    }
    return relationship_names.get((distance_up, distance_down), "기타 친족")

def create_enhanced_family_tree():
    st.title('가계도 생성기 (성별 및 배우자 정보 포함)')
    
    # 탭 생성
    tab1, tab2 = st.tabs(["가계도", "친족 관계표"])
    
    with tab1:
        # Graphviz 객체 생성
        graph = graphviz.Digraph('family_tree')
        graph.attr(rankdir='TB')
        
        # 가족 구성원 입력
        st.subheader('가족 구성원 추가')
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('이름')
            gender = st.selectbox('성별', ['남성', '여성'])
        with col2:
            parent_name = st.text_input('부모 이름 (선택사항)')
            spouse_name = st.text_input('배우자 이름 (선택사항)')
            
        if st.button('가족 구성원 추가'):
            if name:
                if 'family_members' not in st.session_state:
                    st.session_state.family_members = {}
                
                # 새로운 가족 구성원 추가
                st.session_state.family_members[name] = FamilyMember(
                    name=name,
                    gender=gender,
                    parent_name=parent_name,
                    spouse_name=spouse_name
                )
                st.success(f'{name} 추가됨!')
        
        # 가계도 표시
        if 'family_members' in st.session_state and st.session_state.family_members:
            st.subheader('가계도')
            
            # 노드 추가
            for member_name, member in st.session_state.family_members.items():
                # 성별에 따른 노드 색상 설정
                node_color = 'lightblue' if member.gender == '남성' else 'pink'
                
                # 노드 레이블 생성
                label = f"{member_name}\n({member.gender})"
                if member.spouse_name:
                    label += f"\n배우자: {member.spouse_name}"
                
                # 노드 추가
                graph.node(member_name, 
                         label=label,
                         style='filled',
                         fillcolor=node_color)
            
            # 부모-자식 관계 연결
            for member_name, member in st.session_state.family_members.items():
                if member.parent_name:
                    graph.edge(member.parent_name, member_name)
            
            # 배우자 관계 연결 (점선으로 표시)
            added_spouse_edges = set()  # 중복 방지를 위한 집합
            for member_name, member in st.session_state.family_members.items():
                if member.spouse_name and (member_name, member.spouse_name) not in added_spouse_edges:
                    graph.edge(member_name, member.spouse_name, 
                             style='dashed',
                             dir='none',  # 화살표 없음
                             color='red')
                    added_spouse_edges.add((member_name, member.spouse_name))
                    added_spouse_edges.add((member.spouse_name, member_name))
            
            st.graphviz_chart(graph)
        
        # 현재 등록된 가족 구성원 목록
        if 'family_members' in st.session_state and st.session_state.family_members:
            st.subheader('등록된 가족 구성원')
            member_data = []
            for name, member in st.session_state.family_members.items():
                member_data.append({
                    '이름': name,
                    '성별': member.gender,
                    '부모': member.parent_name or '-',
                    '배우자': member.spouse_name or '-'
                })
            
            df_members = pd.DataFrame(member_data)
            st.dataframe(df_members)
        
        # 초기화 버튼
        if st.button('가계도 초기화'):
            st.session_state.family_members = {}
            st.success('가계도가 초기화되었습니다.')
    
    with tab2:
        st.subheader('친족 관계표')
        # 친족 관계표 생성
        relationships = []
        for i in range(5):
            row = []
            for j in range(5):
                row.append(get_relationship_name(i, j))
            relationships.append(row)
        
        df = pd.DataFrame(relationships,
                         index=[f"{i}촌 위" for i in range(5)],
                         columns=[f"{i}촌 아래" for i in range(5)])
        
        st.dataframe(df)

if __name__ == '__main__':
    create_enhanced_family_tree()
