import streamlit as st
import graphviz
import pandas as pd
import numpy as np

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
    
    if (distance_up, distance_down) in relationship_names:
        return relationship_names[(distance_up, distance_down)]
    elif distance_up > 4 or distance_down > 4:
        return f"{distance_up}대 위로 또는 {distance_down}대 아래로의 친족"
    else:
        return "기타 친족"

def create_relationship_table():
    """친족 관계 표를 생성합니다."""
    rows = 5
    cols = 5
    data = []
    
    for i in range(rows):
        row = []
        for j in range(cols):
            relationship = get_relationship_name(i, j)
            row.append(relationship)
        data.append(row)
    
    df = pd.DataFrame(data)
    df.index = [f"{i}촌 위" for i in range(rows)]
    df.columns = [f"{i}촌 아래" for i in range(cols)]
    return df

def create_enhanced_family_tree():
    st.title('확장된 가계도 생성기')
    
    # 탭 생성
    tab1, tab2 = st.tabs(["가계도", "친족 관계표"])
    
    with tab1:
        # Graphviz 객체 생성
        graph = graphviz.Digraph('family_tree')
        graph.attr(rankdir='TB')
        graph.attr('node', shape='rectangle', style='filled', fillcolor='lightblue')
        
        # 가족 구성원 입력
        st.subheader('가족 구성원 추가')
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input('이름')
        with col2:
            parent_name = st.text_input('부모 이름')
            
        if st.button('가족 구성원 추가'):
            if name:
                if 'family_members' not in st.session_state:
                    st.session_state.family_members = {}
                st.session_state.family_members[name] = parent_name
                st.success(f'{name} 추가됨!')
        
        # 가계도 표시
        if 'family_members' in st.session_state and st.session_state.family_members:
            st.subheader('가계도')
            
            for member in st.session_state.family_members:
                tooltip = f"""
                이름: {member}
                관계: {get_relationship_name(1, 0) if st.session_state.family_members[member] else '시작점'}
                """
                graph.node(member, tooltip=tooltip)
            
            for child, parent in st.session_state.family_members.items():
                if parent:
                    graph.edge(parent, child)
            
            st.graphviz_chart(graph)
    
    with tab2:
        st.subheader('친족 관계표')
        df = create_relationship_table()
        
        # 스타일이 적용된 데이터프레임을 HTML로 변환
        html = f"""
        <style>
            .dataframe {{
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 0.9em;
                font-family: sans-serif;
                min-width: 400px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
            .dataframe thead tr {{
                background-color: #009879;
                color: #ffffff;
                text-align: left;
            }}
            .dataframe th,
            .dataframe td {{
                padding: 12px 15px;
                text-align: center;
            }}
            .dataframe tbody tr {{
                border-bottom: 1px solid #dddddd;
            }}
            .dataframe tbody tr:nth-of-type(even) {{
                background-color: #f3f3f3;
            }}
            .dataframe tbody tr:hover {{
                background-color: #f5f5f5;
                cursor: pointer;
            }}
            .tooltip {{
                position: relative;
                display: inline-block;
            }}
            .tooltip .tooltiptext {{
                visibility: hidden;
                width: 120px;
                background-color: black;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 5px 0;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -60px;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            .tooltip:hover .tooltiptext {{
                visibility: visible;
                opacity: 1;
            }}
        </style>
        {df.to_html(classes='dataframe')}
        """
        
        st.markdown(html, unsafe_allow_html=True)
        
        # 초기화 버튼
        if st.button('가계도 초기화'):
            st.session_state.family_members = {}
            st.success('가계도가 초기화되었습니다.')

if __name__ == '__main__':
    create_enhanced_family_tree()
