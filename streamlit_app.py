import streamlit as st
import graphviz
import pandas as pd

class FamilyMember:
    def __init__(self, name, gender, parent_name=None, spouse_name=None):
        self.name = name
        self.gender = gender
        self.parent_name = parent_name
        self.spouse_name = spouse_name
        self.children = []

def get_family_title(member, target, family_members):
    """두 구성원 사이의 호칭을 계산합니다."""
    
    def get_gender_specific_title(base_title, gender):
        """성별에 따른 호칭을 반환합니다."""
        gender_titles = {
            '할아버지': {'남성': '할아버지', '여성': '할머니'},
            '아버지': {'남성': '아버지', '여성': '어머니'},
            '아들': {'남성': '아들', '여성': '딸'},
            '손자': {'남성': '손자', '여성': '손녀'},
            '형제': {'남성': '형', '여성': '누나'},
            '동생': {'남성': '남동생', '여성': '여동생'},
            '조카': {'남성': '조카', '여성': '조카딸'},
            '삼촌': {'남성': '삼촌', '여성': '고모'},
        }
        
        for base, variants in gender_titles.items():
            if base_title.startswith(base):
                return base_title.replace(base, variants[gender])
        return base_title

    def find_path_to_root(name, family_members, path=None):
        """루트까지의 경로를 찾습니다."""
        if path is None:
            path = []
        if name not in family_members:
            return None
        current = family_members[name]
        path.append(name)
        if not current.parent_name:
            return path
        return find_path_to_root(current.parent_name, family_members, path)

    # 동일 인물
    if member == target:
        return "본인"

    # 배우자 관계
    if family_members[member].spouse_name == target:
        return "배우자"

    # 부모-자식 관계
    if family_members[target].parent_name == member:
        return get_gender_specific_title("아들", family_members[target].gender)
    if family_members[member].parent_name == target:
        return get_gender_specific_title("아버지", family_members[target].gender)

    # 각각의 루트까지 경로 찾기
    member_path = find_path_to_root(member, family_members, [])
    target_path = find_path_to_root(target, family_members, [])
    
    if not member_path or not target_path:
        return "관계확인불가"

    # 공통 조상 찾기
    common_ancestor = None
    min_length = min(len(member_path), len(target_path))
    for i in range(min_length):
        if member_path[i] != target_path[i]:
            if i > 0:
                common_ancestor = member_path[i-1]
            break
        if i == min_length - 1:
            common_ancestor = member_path[i]

    if not common_ancestor:
        return "관계확인불가"

    # 세대 차이 계산
    member_gen = member_path.index(common_ancestor)
    target_gen = target_path.index(common_ancestor)
    gen_diff = target_gen - member_gen

    # 호칭 결정
    if gen_diff > 0:
        if gen_diff == 1:
            return get_gender_specific_title("형제", family_members[target].gender)
        elif gen_diff == 2:
            return get_gender_specific_title("조카", family_members[target].gender)
        else:
            return f"{gen_diff}촌 조카"
    elif gen_diff < 0:
        if abs(gen_diff) == 1:
            return get_gender_specific_title("삼촌", family_members[target].gender)
        elif abs(gen_diff) == 2:
            return get_gender_specific_title("할아버지", family_members[target].gender)
        else:
            return f"{abs(gen_diff)}촌 조상"
    else:
        return "사촌" if member_path.index(common_ancestor) > 0 else "형제"

def create_enhanced_family_tree():
    st.title('가계도 생성기 (호칭 포함)')
    
    tab1, tab2 = st.tabs(["가계도", "구성원 관리"])
    
    with tab1:
        if 'family_members' in st.session_state and st.session_state.family_members:
            st.subheader('가계도')
            graph = graphviz.Digraph('family_tree')
            graph.attr(rankdir='TB')
            
            # 기준 구성원 선택
            reference_member = st.selectbox(
                '기준 구성원 선택 (이 사람을 기준으로 호칭이 표시됩니다)',
                list(st.session_state.family_members.keys())
            )
            
            # 노드 추가
            for member_name, member in st.session_state.family_members.items():
                node_color = 'lightblue' if member.gender == '남성' else 'pink'
                
                # 호칭 계산
                title = get_family_title(reference_member, member_name, st.session_state.family_members)
                
                label = f"{member_name}\n({member.gender})\n{title}"
                if member.spouse_name:
                    label += f"\n배우자: {member.spouse_name}"
                
                graph.node(member_name, 
                         label=label,
                         style='filled',
                         fillcolor=node_color)
            
            # 관계선 추가
            for member_name, member in st.session_state.family_members.items():
                if member.parent_name:
                    graph.edge(member.parent_name, member_name)
                
                if member.spouse_name and member_name < member.spouse_name:  # 중복 방지
                    graph.edge(member_name, member.spouse_name, 
                             style='dashed',
                             dir='none',
                             color='red')
            
            st.graphviz_chart(graph)
    
    with tab2:
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
                
                st.session_state.family_members[name] = FamilyMember(
                    name=name,
                    gender=gender,
                    parent_name=parent_name,
                    spouse_name=spouse_name
                )
                st.success(f'{name} 추가됨!')
        
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
        
        if st.button('가계도 초기화'):
            st.session_state.family_members = {}
            st.success('가계도가 초기화되었습니다.')

if __name__ == '__main__':
    create_enhanced_family_tree()
