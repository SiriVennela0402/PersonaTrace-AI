from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from src.personatrace.report import build_placeholder_report


APP_TITLE = "PersonaTrace AI"
APP_SUBTITLE = "AI-Based Deepfake Interview Risk Detection System"


def save_uploaded_video(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="PT",
        layout="wide",
    )

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.subheader("Interview Video")
        uploaded_video = st.file_uploader(
            "Upload a short interview video",
            type=["mp4", "mov", "avi", "mkv"],
        )

        if uploaded_video is not None:
            st.video(uploaded_video)
            video_path = save_uploaded_video(uploaded_video)
            st.success("Video uploaded successfully. Day 2 will add frame extraction and metadata analysis.")
        else:
            video_path = None
            st.info("Upload a short interview clip to begin a PersonaTrace AI risk check.")

    with right:
        st.subheader("Risk Report Preview")
        report = build_placeholder_report(video_path)

        st.metric("Deepfake Risk Score", f"{report.risk_score}%")
        st.write(f"**Risk Level:** {report.risk_level}")

        st.write("**Reasons:**")
        for reason in report.reasons:
            st.write(f"- {reason}")

        st.divider()
        st.write("**Planned Analysis Modules:**")
        for module in report.planned_modules:
            st.write(f"- {module}")


if __name__ == "__main__":
    main()

