import streamlit as st
import segno
import io


@st.dialog("Create New Subject")
def share_subject_dialog(subject_name, subject_code):

    app_domain = "vericlass-main.streamlit.app"
    join_url = f"{app_domain}/?join_code={subject_code}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind="png", scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Copy Link")

        st.code(join_url, language="text")

        st.code(subject_code, language="text")

        st.info("Copy the link to share on WhatsApp or email")

    with col2:
        st.markdown("### Scan to Join")

        st.image(
            out.getvalue(),
            use_container_width=True,
            caption="QR CODE FOR CLASS Joining"
        )
