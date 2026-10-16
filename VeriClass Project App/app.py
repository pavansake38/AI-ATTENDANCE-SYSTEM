import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen


def main():

    st.set_page_config(
        page_title='VERICLASS - Making Attendance faster using AI',
        page_icon= "https://i.ibb.co/YTYGn5qV/logo.png"
    )

    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None


    # =====================================================
    # CHECK JOIN LINK
    # =====================================================

    join_code = st.query_params.get("join-code")

    if join_code:

        # Save join code before student login
        st.session_state["pending_join_code"] = join_code

        # Force student screen
        if st.session_state.get("login_type") != "student":

            st.session_state["login_type"] = "student"

            st.rerun()


    # =====================================================
    # ROUTING
    # =====================================================

    match st.session_state["login_type"]:

        case "teacher":

            teacher_screen()


        case "student":

            student_screen()


        case None:

            home_screen()


if __name__ == "__main__":

    main()