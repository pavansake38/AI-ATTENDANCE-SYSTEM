import streamlit as st


def header_home():
    logo_url="https://attendanceradar.com/wp-content/uploads/2024/06/DALL%C2%B7E-2024-06-28-19.10.18-A-university-classroom-where-a-teacher-is-taking-attendance.-The-teacher-stands-at-the-front-of-the-class-with-a-clipboard-or-tablet-checking-off-nam-1024x585.webp"
    st.markdown(f"""
        <div style='display:flex;flex-direction:column;align-items:centre;justify-content:centre;margin-bottom:30px'>
            <img src='{logo_url}' style='height:300px;width:300px;border-radius: 20px;'/>
            <h1 style='text-align:centre;color:#E0E3FF'>Snap<br/> Class</h1>

        </div>



""",unsafe_allow_html=True)