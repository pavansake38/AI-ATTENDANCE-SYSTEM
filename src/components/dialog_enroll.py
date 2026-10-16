import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.conflict import supabase
import time


@st.dialog("Enroll in Subject")
def enroll_dialog():

    st.write(
        "Enter the subject code provided by your teacher to enroll."
    )

    join_code = st.text_input(
        "Subject code",
        placeholder="e.g. CS01"
    )

    if st.button(
        "Enroll Now",
        type="primary",
        width="stretch"
    ):

        # =============================================
        # CHECK SUBJECT CODE
        # =============================================

        if not join_code:

            st.warning(
                "Please enter subject code"
            )

            return

        # =============================================
        # FIND SUBJECT
        # =============================================

        res = (
            supabase
            .table("subjects")
            .select(
                "subject_id, name, subject_code"
            )
            .eq(
                "subject_code",
                join_code.strip()
            )
            .execute()
        )

        # =============================================
        # SUBJECT NOT FOUND
        # =============================================

        if not res.data:

            st.error(
                "Subject not found. Please check the subject code."
            )

            return

        # =============================================
        # GET SUBJECT
        # =============================================

        subject = res.data[0]

        # =============================================
        # GET LOGGED-IN STUDENT
        # =============================================

        student_data = st.session_state.get(
            "student_data"
        )

        if not student_data:

            st.error(
                "Student session not found. Please login again."
            )

            return

        student_id = student_data["student_id"]

        # =============================================
        # CHECK ALREADY ENROLLED
        # =============================================

        check = (
            supabase
            .table("subject_students")
            .select("*")
            .eq(
                "subject_id",
                subject["subject_id"]
            )
            .eq(
                "student_id",
                student_id
            )
            .execute()
        )

        if check.data:

            st.warning(
                "You are already enrolled in this subject."
            )

            return

        # =============================================
        # ENROLL STUDENT
        # =============================================

        enroll_student_to_subject(
            student_id,
            subject["subject_id"]
        )

        st.success(
            f"Successfully enrolled in {subject['name']}!"
        )

        time.sleep(1)

        st.rerun()