import streamlit as st
from src.database.conflict import supabase
import bcrypt


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_pass(pwd):
    return bcrypt.hashpw(
        pwd.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def check_pass(pwd, hashed):
    return bcrypt.checkpw(
        pwd.encode("utf-8"),
        hashed.encode("utf-8")
    )


# =========================================================
# TEACHER FUNCTIONS
# =========================================================

def check_teacher_exists(username):
    response = (
        supabase
        .table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )

    return len(response.data) > 0


def create_teacher(username, password, name):
    data = {
        "username": username,
        "password": hash_pass(password),
        "name": name
    }

    response = (
        supabase
        .table("teachers")
        .insert(data)
        .execute()
    )

    return response.data


def teacher_login_d(username, password):
    response = (
        supabase
        .table("teachers")
        .select("*")
        .eq("username", username)
        .execute()
    )

    if not response.data:
        return None

    teacher = response.data[0]

    if check_pass(password, teacher["password"]):
        return teacher

    return None


# =========================================================
# STUDENT FUNCTIONS
# =========================================================

def get_all_students():
    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data


def create_student(
    new_name,
    face_embedding=None,
    voice_embedding=None
):
    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }

    response = (
        supabase
        .table("students")
        .insert(data)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# =========================================================
# SUBJECT FUNCTIONS
# =========================================================

def create_subject(
    subject_code,
    name,
    section,
    teacher_id
):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }

    response = (
        supabase
        .table("subjects")
        .insert(data)
        .execute()
    )

    return response.data


def get_teacher_subject(teacher_id):
    response = (
        supabase
        .table("subjects")
        .select(
            "*, subject_students(count), attendence_logs(timestamp)"
        )
        .eq("teacher_id", teacher_id)
        .execute()
    )

    subjects = response.data

    for sub in subjects:
        # Total enrolled students
        subject_students = sub.get("subject_students", [])

        if subject_students:
            sub["total_students"] = subject_students[0].get(
                "count", 0
            )
        else:
            sub["total_students"] = 0

        # Total classes
        attendance = sub.get("attendence_logs", [])

        unique_sessions = len(
            set(
                log["timestamp"]
                for log in attendance
                if log.get("timestamp")
            )
        )

        sub["total_classes"] = unique_sessions

        # Remove nested data after calculating statistics
        sub.pop("subject_students", None)
        sub.pop("attendence_logs", None)

    return subjects


# =========================================================
# ENROLLMENT FUNCTIONS
# =========================================================

def enroll_student_to_subject(student_id, subject_id):
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }

    response = (
        supabase
        .table("subject_students")
        .insert(data)
        .execute()
    )

    return response.data


def unenroll_student_to_subject(student_id, subject_id):
    response = (
        supabase
        .table("subject_students")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data


def get_student_subjects(student_id):
    response = (
        supabase
        .table("subject_students")
        .select("*, subjects(*)")
        .eq("student_id", student_id)
        .execute()
    )

    return response.data


# =========================================================
# ATTENDANCE FUNCTIONS
# =========================================================

def get_student_attendance(student_id):
    response = (
        supabase
        .table("attendence_logs")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    return response.data


def create_attendance(logs):
    response = (
        supabase
        .table("attendence_logs")
        .insert(logs)
        .execute()
    )

    return response.data


def get_attendance_for_teacher():
    # Retrieve the logged-in teacher's ID
    teacher_id = st.session_state.get("teacher_id")

    if not teacher_id:
        return []

    response = (
        supabase
        .table("attendence_logs")
        .select("*, subjects!inner(*)")
        .eq("subjects.teacher_id", teacher_id)
        .execute()
    )

    return response.data

