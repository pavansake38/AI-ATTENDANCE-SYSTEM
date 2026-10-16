import streamlit as st
import time
from PIL import Image
import numpy as np

from src.ui.style_base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard

from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier
)

from src.pipelines.voice_pipeline import get_voice_embedding

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)

from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    # =====================================================
    # GET LOGGED-IN STUDENT
    # =====================================================

    student_data = st.session_state.get("student_data")

    if not student_data:
        st.session_state["login_type"] = None
        st.rerun()
        return

    student_id = student_data.get("student_id")

    if not student_id:

        st.error("Student ID not found. Please login again.")

        if st.button("Back to Login"):

            st.session_state.pop("student_data", None)
            st.session_state["login_type"] = None
            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None

            st.rerun()

        return


    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with c1:

        header_dashboard()


    with c2:

        st.markdown(
            f'<h2 style="color: black;">Welcome, {student_data["name"]}</h2>',
            unsafe_allow_html=True
        )

        if st.button(
            "Logout",
            type="secondary",
            key="logoutbtn"
        ):

            st.session_state.pop("student_data", None)
            st.session_state["login_type"] = None
            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None

            # Clear pending join code
            st.session_state.pop("pending_join_code", None)

            st.rerun()


    st.space()


    # =====================================================
    # ENROLLED SUBJECTS HEADER
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.header("Your Enrolled Subjects")


    with c2:

        if st.button(
            "Enrolled Subject",
            type="primary",
            width="stretch"
        ):

            enroll_dialog()


    st.divider()


    # =====================================================
    # LOAD SUBJECTS AND ATTENDANCE
    # =====================================================

    with st.spinner("Loading your enrolled subjects..."):

        subjects = get_student_subjects(student_id)

        logs = get_student_attendance(student_id)


    # =====================================================
    # ATTENDANCE STATISTICS
    # =====================================================

    stats_map = {}

    for log in logs:

        sid = log["subject_id"]

        if sid not in stats_map:

            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):

            stats_map[sid]["attended"] += 1


    # =====================================================
    # DISPLAY SUBJECTS
    # =====================================================

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):

        sub = sub_node["subjects"]

        sid = sub["subject_id"]

        stats = stats_map.get(
            sid,
            {
                "total": 0,
                "attended": 0
            }
        )


        # -------------------------------------------------
        # UNENROLL BUTTON
        # -------------------------------------------------

        def unenroll_button(
            subject_id=sid,
            subject_name=sub["name"]
        ):

            if st.button(
                "Unenroll from this course",
                type="tertiary",
                width="stretch",
                icon=":material/delete_forever:"
            ):

                unenroll_student_to_subject(
                    student_id,
                    subject_id
                )

                st.toast(
                    f"Unenrolled from {subject_name} successfully!"
                )

                time.sleep(1)

                st.rerun()


        # -------------------------------------------------
        # SUBJECT CARD
        # -------------------------------------------------

        with cols[i % 2]:

            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=[
                    (
                        "📅",
                        "Total",
                        stats["total"]
                    ),
                    (
                        "✅",
                        "Attended",
                        stats["attended"]
                    )
                ],
                footer_callback=unenroll_button
            )


    # =====================================================
    # FOOTER
    # =====================================================

    footer_dashboard()


# =========================================================
# STUDENT SCREEN
# =========================================================

def student_screen():

    show_registration = False


    # =====================================================
    # APPLY UI STYLES
    # =====================================================

    style_background_dashboard()
    style_base_layout()


    # =====================================================
    # GET JOIN CODE FROM URL
    # =====================================================

    join_code = st.query_params.get("join-code")

    if join_code:

        # Save permanently in session
        st.session_state["pending_join_code"] = join_code


    # =====================================================
    # CHECK IF STUDENT IS ALREADY LOGGED IN
    # =====================================================

    if "student_data" in st.session_state:

        # Show dashboard first
        student_dashboard()


        # =================================================
        # QUICK ENROLLMENT POPUP
        # =================================================

        pending_join_code = st.session_state.get(
            "pending_join_code"
        )

        if pending_join_code:

            auto_enroll_dialog(
                pending_join_code
            )


        return


    # =====================================================
    # HEADER + BACK BUTTON
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with c1:

        header_dashboard()


    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbackbtn"
        ):

            st.session_state["login_type"] = None

            st.session_state.pop(
                "pending_join_code",
                None
            )

            st.query_params.clear()

            st.rerun()


    # =====================================================
    # FACE LOGIN
    # =====================================================

    st.header(
        "Login using Face ID",
        text_alignment="center"
    )

    st.space()
    st.space()


    photosource = st.camera_input(
        "Position your face in the center"
    )


    if photosource:

        img = np.array(
            Image.open(photosource)
        )


        with st.spinner("AI is scanning..."):

            detected, all_ids, num_faces = predict_attendance(
                img
            )


        # =================================================
        # NO FACE
        # =================================================

        if num_faces == 0:

            st.warning(
                "Face not found!"
            )


        # =================================================
        # MULTIPLE FACES
        # =================================================

        elif num_faces > 1:

            st.warning(
                "Multiple faces found!"
            )


        # =================================================
        # EXACTLY ONE FACE
        # =================================================

        else:

            # ------------------------------------------------
            # FACE RECOGNIZED
            # ------------------------------------------------

            if detected:

                student_id = list(
                    detected.keys()
                )[0]


                all_students = get_all_students()


                student = next(
                    (
                        s
                        for s in all_students
                        if s["student_id"] == student_id
                    ),
                    None
                )


                # ==========================================
                # STUDENT FOUND
                # ==========================================

                if student:

                    st.session_state.is_logged_in = True
                    st.session_state.user_role = "student"


                    # Make sure complete student data
                    st.session_state.student_data = {

                        "student_id": student["student_id"],

                        "name": student["name"]
                    }


                    st.toast(
                        f"Welcome back, {student['name']}"
                    )

                    time.sleep(1)

                    st.rerun()


                # ==========================================
                # STUDENT NOT FOUND
                # ==========================================

                else:

                    st.error(
                        "Student details not found."
                    )


            # ------------------------------------------------
            # FACE NOT RECOGNIZED
            # ------------------------------------------------

            else:

                st.info(
                    "Face not recognised. "
                    "You might be a new student!"
                )

                show_registration = True


    # =====================================================
    # STUDENT REGISTRATION
    # =====================================================

    if show_registration:

        with st.container(border=True):

            st.header(
                "Register New Profile"
            )


            # ------------------------------------------------
            # NAME
            # ------------------------------------------------

            new_name = st.text_input(
                "Enter your name:",
                placeholder="e.g. Pavan Teja"
            )


            # ------------------------------------------------
            # VOICE ENROLLMENT
            # ------------------------------------------------

            st.subheader(
                "Optional: Voice Enrollment"
            )

            st.info(
                "Enroll your voice for voice-only attendance."
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    "Record a short phrase like "
                    "'I am present' or "
                    "'My name is Pavan'"
                )

            except Exception:

                st.error(
                    "Audio recording failed!"
                )


            # =================================================
            # CREATE ACCOUNT
            # =================================================

            if st.button(
                "Create Account",
                type="primary"
            ):


                # ------------------------------------------------
                # NAME VALIDATION
                # ------------------------------------------------

                if not new_name:

                    st.warning(
                        "Please enter your name!"
                    )


                # ------------------------------------------------
                # CREATE PROFILE
                # ------------------------------------------------

                else:

                    with st.spinner(
                        "Creating profile..."
                    ):


                        # ========================================
                        # FACE EMBEDDING
                        # ========================================

                        img = np.array(
                            Image.open(photosource)
                        )


                        encodings = get_face_embeddings(
                            img
                        )


                        if encodings:

                            face_emb = encodings[0].tolist()


                            # ====================================
                            # VOICE EMBEDDING
                            # ====================================

                            voice_emb = None


                            if audio_data:

                                voice_emb = get_voice_embedding(
                                    audio_data.read()
                                )


                            # ====================================
                            # CREATE STUDENT
                            # ====================================

                            response_data = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )


                            # ====================================
                            # STUDENT CREATED
                            # ====================================

                            if response_data:

                                # --------------------------------
                                # RETRAIN CLASSIFIER
                                # --------------------------------

                                train_classifier()


                                # --------------------------------
                                # BUILD STUDENT DATA
                                # --------------------------------

                                if isinstance(
                                    response_data,
                                    dict
                                ):

                                    student_data = response_data

                                else:

                                    student_data = {

                                        "student_id": response_data,

                                        "name": new_name
                                    }


                                # --------------------------------
                                # SAFETY CHECK
                                # --------------------------------

                                if "student_id" not in student_data:

                                    st.error(
                                        "Student was created, "
                                        "but student ID was not returned."
                                    )

                                    return


                                # --------------------------------
                                # SAVE SESSION
                                # --------------------------------

                                st.session_state.is_logged_in = True

                                st.session_state.user_role = "student"


                                st.session_state.student_data = {

                                    "student_id":
                                        student_data["student_id"],

                                    "name":
                                        student_data.get(
                                            "name",
                                            new_name
                                        )
                                }


                                st.toast(
                                    f"Welcome back, {new_name}"
                                )

                                time.sleep(1)

                                st.rerun()


                            # ====================================
                            # CREATION FAILED
                            # ====================================

                            else:

                                st.error(
                                    "Could not create "
                                    "student profile."
                                )


                        # ========================================
                        # FACE EMBEDDING FAILED
                        # ========================================

                        else:

                            st.error(
                                "Couldn't capture your facial "
                                "features for registration."
                            )


    # =====================================================
    # FOOTER
    # =====================================================

    footer_dashboard()