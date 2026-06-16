from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from src.personatrace.report import build_placeholder_report
from src.personatrace.video_analysis import VideoAnalysisResult, analyze_video


APP_TITLE = "PersonaTrace AI"
APP_SUBTITLE = "AI-Based Deepfake Interview Risk Detection System"


def save_uploaded_video(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def show_video_metadata(analysis: VideoAnalysisResult) -> None:
    metadata = analysis.metadata
    st.subheader("Video Metadata")

    metric_columns = st.columns(4)
    metric_columns[0].metric("Duration", f"{metadata.duration_seconds:.1f}s")
    metric_columns[1].metric("FPS", f"{metadata.fps:.1f}")
    metric_columns[2].metric("Frames", f"{metadata.frame_count}")
    metric_columns[3].metric("Resolution", f"{metadata.width}x{metadata.height}")


def show_sampled_frames(analysis: VideoAnalysisResult) -> None:
    st.subheader("Sampled Frames")

    if not analysis.sampled_frames:
        st.warning("No frames could be extracted from this video.")
        return

    frame_columns = st.columns(3)
    for index, frame in enumerate(analysis.sampled_frames):
        with frame_columns[index % 3]:
            st.image(
                frame.image_rgb,
                caption=f"Frame {frame.frame_index} at {frame.timestamp_seconds:.2f}s",
                use_container_width=True,
            )


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
            st.success("Video uploaded successfully.")
        else:
            video_path = None
            st.info("Upload a short interview clip to begin a PersonaTrace AI risk check.")

        analysis = None
        if video_path is not None:
            try:
                analysis = analyze_video(video_path)
                show_video_metadata(analysis)
                show_sampled_frames(analysis)
            except ValueError as error:
                st.error(str(error))

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
