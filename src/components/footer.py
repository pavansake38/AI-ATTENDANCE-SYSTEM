import streamlit as st


def footer_home():
    logo_="https://www.cbmphotography.com/img/s/v-10/p1350173912-3.jpg"
    st.markdown(f"""
        <div style="margin-top:2rem;display:flex;gap:6px;justify-content:centre;items-slign:centre>
       <p style="font-weight:bold;color:white;text-align:center;">
    Created with ❤️ by
</p>
        <img src='{logo_}'style='max-height:100px'/>
        </div>



""",unsafe_allow_html=True)