import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.style_base_layout import style_base_layout,style_background_dashboard,style_background_home

def home_screen():

    header_home()   
    style_background_home()
    style_base_layout()

    col1,col2=st.columns(2,gap="large")

    with col1:
        st.header("I'm Teacher")
        st.image("https://classplusapp.com/growth/wp-content/uploads/2023/02/Top-Qualities-Of-A-Good-Teacher.jpg",width=205)
        if st.button('Teacher Portal',type='primary',icon=':material/arrow_outward:'):
            st.session_state['login_type']='teacher'
            st.rerun()
    with col2:
        st.header("I'm Student")
        st.image("https://static.vecteezy.com/system/resources/previews/008/846/239/original/illustration-student-with-question-mark-png.png",width=120)
        if st.button('Student Portal',type='primary',icon=':material/arrow_outward:'):
            st.session_state['login_type']='student'
            st.rerun()

    footer_home()