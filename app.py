from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from src.personatrace.face_analysis import FaceConsistencyResult, analyze_face_consistency
from src.personatrace.report import build_placeholder_report
from src.personatrace.video_analysis import VideoAnalysisResult, analyze_video


APP_TITLE = "PersonaTrace AI"
APP_SUBTITLE = "AI-Based Deepfake Interview Risk Detection System"


def initialize_state() -> None:
    defaults = {
        "page": "intro",
        "video_path": None,
        "analysis": None,
        "face_result": None,
        "uploaded_name": None,
        "scan_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #05070d;
                --panel: rgba(10, 17, 30, 0.84);
                --panel-strong: rgba(7, 12, 22, 0.94);
                --ink: #edf6ff;
                --muted: #8fa3b8;
                --line: rgba(98, 178, 255, 0.2);
                --cyan: #38d5ff;
                --blue: #3b82f6;
                --violet: #8b5cf6;
                --teal: #2dd4bf;
                --amber: #f59e0b;
                --red: #fb4d5d;
            }

            .stApp {
                background:
                    radial-gradient(circle at 18% 12%, rgba(56, 213, 255, 0.16), transparent 28%),
                    radial-gradient(circle at 82% 18%, rgba(139, 92, 246, 0.16), transparent 26%),
                    radial-gradient(circle at 50% 82%, rgba(251, 77, 93, 0.08), transparent 34%),
                    linear-gradient(135deg, #02040a 0%, #07111f 42%, #02040a 100%);
                color: var(--ink);
            }

            .stApp::before {
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
                background-size: 44px 44px;
                mask-image: linear-gradient(to bottom, rgba(0,0,0,0.72), transparent 78%);
            }

            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stDecoration"],
            #MainMenu,
            footer {
                display: none;
            }

            .block-container {
                max-width: 1200px;
                padding: 2.1rem 2rem 3.2rem;
            }

            h1, h2, h3, p, label, span, div {
                letter-spacing: 0;
            }

            .hero {
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(56, 213, 255, 0.24);
                background:
                    linear-gradient(135deg, rgba(13, 25, 44, 0.96), rgba(5, 9, 18, 0.9)),
                    radial-gradient(circle at 88% 28%, rgba(56, 213, 255, 0.2), transparent 30%);
                padding: 32px 34px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.46), inset 0 1px 0 rgba(255,255,255,0.06);
            }

            .intro-shell {
                min-height: 72vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }

            .intro-card {
                position: relative;
                width: min(780px, 100%);
                border: 1px solid rgba(56, 213, 255, 0.22);
                background:
                    radial-gradient(circle at 50% 0%, rgba(56, 213, 255, 0.14), transparent 42%),
                    linear-gradient(135deg, rgba(9, 15, 29, 0.96), rgba(3, 7, 15, 0.92));
                border-radius: 8px;
                padding: 54px 44px;
                box-shadow: 0 30px 90px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
                overflow: hidden;
            }

            .sigil {
                position: relative;
                width: 132px;
                height: 132px;
                margin: 0 auto 24px;
                border-radius: 50%;
                border: 1px solid rgba(56, 213, 255, 0.46);
                box-shadow: 0 0 44px rgba(56, 213, 255, 0.28), inset 0 0 34px rgba(139, 92, 246, 0.18);
                animation: pulse-sigil 3.4s ease-in-out infinite;
            }

            .sigil::before,
            .sigil::after {
                content: "";
                position: absolute;
                inset: 16px;
                border: 1px solid rgba(139, 92, 246, 0.52);
                transform: rotate(45deg);
                animation: rotate-sigil 9s linear infinite;
            }

            .sigil::after {
                inset: 34px;
                border-color: rgba(45, 212, 191, 0.54);
                animation-direction: reverse;
                animation-duration: 6s;
            }

            .sigil-core {
                position: absolute;
                inset: 45px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(237,246,255,0.96), rgba(56,213,255,0.38) 34%, transparent 70%);
                box-shadow: 0 0 28px rgba(56, 213, 255, 0.8);
            }

            .intro-title {
                font-size: clamp(2.4rem, 6vw, 5.2rem);
                line-height: 0.95;
                margin: 0;
                color: #f3fbff;
                text-shadow: 0 0 18px rgba(56,213,255,0.38), 0 0 54px rgba(139,92,246,0.24);
                animation: reveal-title 1.5s ease-out both;
            }

            .intro-subtitle {
                color: #9bb4cb;
                max-width: 650px;
                margin: 18px auto 0;
                line-height: 1.7;
                font-size: 1.02rem;
            }

            .profile-bar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 14px;
                margin-bottom: 18px;
            }

            .profile-card {
                display: flex;
                align-items: center;
                gap: 12px;
                border: 1px solid rgba(56,213,255,0.2);
                background: rgba(5, 12, 24, 0.76);
                border-radius: 8px;
                padding: 10px 12px;
            }

            .avatar {
                width: 42px;
                height: 42px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                color: #03111c;
                background: linear-gradient(135deg, var(--cyan), var(--teal));
                box-shadow: 0 0 24px rgba(56,213,255,0.28);
                font-weight: 800;
            }

            .profile-name {
                color: var(--ink);
                font-weight: 760;
                font-size: 0.94rem;
            }

            .profile-role {
                color: var(--muted);
                font-size: 0.78rem;
            }

            .flow-tabs {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }

            .flow-tab {
                border: 1px solid rgba(56,213,255,0.18);
                border-radius: 999px;
                color: #9bb4cb;
                background: rgba(5, 12, 24, 0.62);
                padding: 7px 11px;
                font-size: 0.78rem;
                font-weight: 700;
            }

            .flow-tab-active {
                color: #03111c;
                background: linear-gradient(135deg, var(--cyan), var(--teal));
                box-shadow: 0 0 24px rgba(56,213,255,0.2);
            }

            .upload-portal {
                min-height: 370px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid rgba(56,213,255,0.18);
                background:
                    radial-gradient(circle at 50% 0%, rgba(56,213,255,0.1), transparent 34%),
                    rgba(3,8,17,0.56);
                border-radius: 8px;
                padding: 26px;
            }

            @keyframes pulse-sigil {
                0%, 100% { transform: scale(1); filter: brightness(1); }
                50% { transform: scale(1.04); filter: brightness(1.25); }
            }

            @keyframes rotate-sigil {
                from { transform: rotate(45deg); }
                to { transform: rotate(405deg); }
            }

            @keyframes reveal-title {
                from { opacity: 0; transform: translateY(14px); filter: blur(8px); }
                to { opacity: 1; transform: translateY(0); filter: blur(0); }
            }

            .hero::after {
                content: "";
                position: absolute;
                right: -80px;
                top: -120px;
                width: 340px;
                height: 340px;
                border: 1px solid rgba(56, 213, 255, 0.22);
                border-radius: 50%;
                box-shadow: 0 0 70px rgba(56, 213, 255, 0.12);
            }

            .eyebrow {
                color: var(--cyan);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 8px;
            }

            .hero-title {
                color: var(--ink);
                font-size: 2.7rem;
                line-height: 1.05;
                font-weight: 800;
                margin: 0;
                text-shadow: 0 0 34px rgba(56, 213, 255, 0.2);
            }

            .hero-subtitle {
                color: var(--muted);
                font-size: 1.02rem;
                line-height: 1.6;
                max-width: 790px;
                margin: 12px 0 0;
            }

            .panel {
                border: 1px solid var(--line);
                background: var(--panel);
                border-radius: 8px;
                padding: 22px;
                box-shadow: 0 18px 52px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255,255,255,0.05);
                margin-bottom: 18px;
                backdrop-filter: blur(18px);
            }

            .panel-title {
                font-size: 0.98rem;
                font-weight: 780;
                color: var(--ink);
                margin: 0 0 12px;
            }

            .section-kicker {
                color: var(--cyan);
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 8px;
            }

            .risk-score {
                font-size: 4.2rem;
                line-height: 1;
                font-weight: 820;
                margin: 10px 0 14px;
                text-shadow: 0 0 32px currentColor;
            }

            .risk-low { color: var(--teal); }
            .risk-medium { color: var(--amber); }
            .risk-high { color: var(--red); }
            .risk-waiting { color: var(--muted); }

            .status-pill {
                display: inline-flex;
                align-items: center;
                border: 1px solid rgba(56, 213, 255, 0.28);
                border-radius: 999px;
                padding: 6px 11px;
                color: #cde8ff;
                background: rgba(56, 213, 255, 0.08);
                font-size: 0.82rem;
                font-weight: 650;
            }

            .reason-list {
                margin: 10px 0 0;
                padding: 0;
            }

            .reason-list li {
                list-style: none;
                border-top: 1px solid rgba(143, 163, 184, 0.14);
                padding: 11px 0;
                color: #d5e6f7;
                font-size: 0.92rem;
            }

            .module-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 8px;
                margin-top: 10px;
            }

            .module-item {
                border: 1px solid rgba(56, 213, 255, 0.16);
                border-radius: 8px;
                padding: 10px;
                background: rgba(5, 12, 24, 0.72);
                color: #c7d7e8;
                font-size: 0.86rem;
            }

            [data-testid="stFileUploader"] {
                border: 1px dashed rgba(56, 213, 255, 0.42);
                background: rgba(3, 8, 17, 0.78);
                border-radius: 8px;
                padding: 16px;
            }

            [data-testid="stFileUploader"] * {
                color: #d8e8f8;
            }

            [data-testid="stFileUploader"] button {
                border: 1px solid rgba(56, 213, 255, 0.42);
                background: linear-gradient(135deg, rgba(56, 213, 255, 0.16), rgba(59, 130, 246, 0.16));
                color: #edf6ff;
            }

            [data-testid="stMetric"] {
                border: 1px solid rgba(56, 213, 255, 0.16);
                background: rgba(5, 12, 24, 0.74);
                border-radius: 8px;
                padding: 12px;
            }

            [data-testid="stMetricLabel"] {
                color: var(--muted);
                font-size: 0.78rem;
            }

            [data-testid="stMetricValue"] {
                color: var(--ink);
                font-size: 1.35rem;
            }

            .stAlert {
                border-radius: 8px;
                background: rgba(8, 16, 30, 0.9);
                color: #d8e8f8;
            }

            img {
                border-radius: 8px;
                border: 1px solid rgba(56, 213, 255, 0.2);
                box-shadow: 0 12px 32px rgba(0,0,0,0.28);
            }

            video {
                border-radius: 8px;
                border: 1px solid rgba(56, 213, 255, 0.2);
                box-shadow: 0 12px 32px rgba(0,0,0,0.28);
            }

            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, var(--cyan), var(--violet), var(--red));
            }

            .stMarkdown, .stCaption, .stText {
                color: var(--ink);
            }

            small, figcaption {
                color: var(--muted) !important;
            }

            @media (max-width: 760px) {
                .block-container {
                    padding: 1rem;
                }

                .hero {
                    padding: 22px;
                }

                .hero-title {
                    font-size: 2rem;
                }

                .module-grid {
                    grid-template-columns: 1fr;
                }

                .profile-bar {
                    align-items: flex-start;
                    flex-direction: column;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_class(risk_level: str) -> str:
    level = risk_level.lower()
    if "high" in level:
        return "risk-high"
    if "medium" in level:
        return "risk-medium"
    if "low" in level:
        return "risk-low"
    return "risk-waiting"


def save_uploaded_video(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def reset_scan() -> None:
    st.session_state.video_path = None
    st.session_state.analysis = None
    st.session_state.face_result = None
    st.session_state.uploaded_name = None
    st.session_state.scan_error = None
    st.session_state.page = "upload"


def set_page(page: str) -> None:
    st.session_state.page = page


def show_profile_bar(active: str) -> None:
    tabs = [
        ("upload", "Evidence"),
        ("report", "Trace"),
    ]
    tab_html = "".join(
        f'<span class="flow-tab {"flow-tab-active" if key == active else ""}">{label}</span>'
        for key, label in tabs
    )
    st.markdown(
        f"""
        <div class="profile-bar">
            <div class="profile-card">
                <div class="avatar">SV</div>
                <div>
                    <div class="profile-name">Siri Vennela</div>
                    <div class="profile-role">Security Analyst Workspace</div>
                </div>
            </div>
            <div class="flow-tabs">{tab_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_video_metadata(analysis: VideoAnalysisResult) -> None:
    metadata = analysis.metadata
    st.markdown('<div class="section-kicker">Video Intake</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Video Metadata</div>', unsafe_allow_html=True)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Duration", f"{metadata.duration_seconds:.1f}s")
    metric_columns[1].metric("FPS", f"{metadata.fps:.1f}")
    metric_columns[2].metric("Frames", f"{metadata.frame_count}")
    metric_columns[3].metric("Resolution", f"{metadata.width}x{metadata.height}")


def show_sampled_frames(analysis: VideoAnalysisResult) -> None:
    st.markdown('<div class="panel-title">Sampled Evidence Frames</div>', unsafe_allow_html=True)

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


def show_face_consistency(face_result: FaceConsistencyResult) -> None:
    st.markdown('<div class="section-kicker">Identity Signal</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Face Consistency</div>', unsafe_allow_html=True)

    face_columns = st.columns(4)
    face_columns[0].metric("Frames Checked", face_result.total_frames_checked)
    face_columns[1].metric("Face Detection", f"{face_result.detection_rate * 100:.0f}%")
    face_columns[2].metric("Multiple Face Frames", face_result.frames_with_multiple_faces)
    face_columns[3].metric("Face Risk", f"{face_result.risk_score}%")

    st.markdown(
        f'<span class="status-pill">Face Risk Level: {face_result.risk_level}</span>',
        unsafe_allow_html=True,
    )

    reason_items = "".join(f"<li>{reason}</li>" for reason in face_result.reasons)
    st.markdown(f'<ul class="reason-list">{reason_items}</ul>', unsafe_allow_html=True)

    if not face_result.frame_results:
        return

    st.markdown('<div class="panel-title">Annotated Face Detection Frames</div>', unsafe_allow_html=True)
    face_frame_columns = st.columns(3)
    for index, frame in enumerate(face_result.frame_results):
        with face_frame_columns[index % 3]:
            face_count = len(frame.faces)
            label = f"Frame {frame.frame_index} at {frame.timestamp_seconds:.2f}s - {face_count} face(s)"
            st.image(frame.annotated_image_rgb, caption=label, use_container_width=True)


def show_intro_page() -> None:
    st.markdown(
        f"""
        <div class="intro-shell">
            <section class="intro-card">
                <div class="sigil"><div class="sigil-core"></div></div>
                <div class="eyebrow">Identity Threat Screening</div>
                <h1 class="intro-title">{APP_TITLE}</h1>
                <p class="intro-subtitle">
                    A dark-trace interview screening system for remote hiring.
                    Upload a candidate clip, extract evidence frames, and open a trace analysis report.
                </p>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        if st.button("Enter PersonaTrace", use_container_width=True):
            set_page("upload")
            st.rerun()


def show_upload_page() -> None:
    show_profile_bar("upload")
    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">Evidence Intake</div>
            <h1 class="hero-title">Upload Interview Evidence</h1>
            <p class="hero-subtitle">
                Add a short remote interview clip. PersonaTrace AI will extract frames first,
                then move the case into the investigation report.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        st.markdown('<div class="section-kicker">Evidence Intake</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Candidate Interview Clip</div>', unsafe_allow_html=True)
        uploaded_video = st.file_uploader(
            "Upload a short interview video",
            type=["mp4", "mov", "avi", "mkv"],
            label_visibility="collapsed",
        )

        if uploaded_video is not None:
            st.video(uploaded_video)
            video_path = save_uploaded_video(uploaded_video)
            st.session_state.video_path = video_path
            st.session_state.uploaded_name = uploaded_video.name
            st.success("Evidence received. PersonaTrace AI is scanning sampled frames.")
            try:
                analysis = analyze_video(video_path)
                face_result = analyze_face_consistency(analysis.sampled_frames)
                st.session_state.analysis = analysis
                st.session_state.face_result = face_result
                st.session_state.scan_error = None
                if st.button("Open Investigation Report", use_container_width=True):
                    set_page("report")
                    st.rerun()
            except ValueError as error:
                st.session_state.scan_error = str(error)
                st.error(str(error))
        else:
            st.info("Upload a short interview clip to open a risk investigation.")

    with right:
        st.markdown('<div class="section-kicker">Case Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Investigation Queue</div>', unsafe_allow_html=True)
        uploaded_name = st.session_state.uploaded_name or "No clip selected"
        st.markdown(f'<span class="status-pill">{uploaded_name}</span>', unsafe_allow_html=True)
        st.markdown(
            """
            <ul class="reason-list">
                <li>Step 1: Upload candidate interview clip</li>
                <li>Step 2: Extract metadata and evidence frames</li>
                <li>Step 3: Open face consistency report</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.analysis is not None:
            metadata = st.session_state.analysis.metadata
            st.markdown('<div class="panel-title" style="margin-top:18px;">Preview</div>', unsafe_allow_html=True)
            st.metric("Duration", f"{metadata.duration_seconds:.1f}s")
            st.metric("Frames", f"{metadata.frame_count}")
        if st.button("Back to Opening Screen", use_container_width=True):
            set_page("intro")
            st.rerun()


def show_report_page() -> None:
    show_profile_bar("report")

    analysis = st.session_state.analysis
    face_result = st.session_state.face_result
    video_path = st.session_state.video_path

    if analysis is None or video_path is None:
        st.warning("No evidence has been uploaded yet.")
        if st.button("Go to Upload Page"):
            set_page("upload")
            st.rerun()
        return

    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">Trace Investigation</div>
            <h1 class="hero-title">Trace Analysis Report</h1>
            <p class="hero-subtitle">
                PersonaTrace AI has extracted evidence frames and generated the current
                face-consistency risk signal for this interview clip.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 0.8], gap="large")

    with right:
        st.markdown('<div class="section-kicker">Threat Report</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Interview Risk Score</div>', unsafe_allow_html=True)
        report = build_placeholder_report(video_path, face_result)
        score_class = risk_class(report.risk_level)
        st.markdown(
            f'<div class="risk-score {score_class}">{report.risk_score}%</div>',
            unsafe_allow_html=True,
        )
        st.progress(report.risk_score)
        st.markdown(
            f'<span class="status-pill">Risk Level: {report.risk_level}</span>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel-title" style="margin-top:18px;">Key Findings</div>', unsafe_allow_html=True)
        reason_items = "".join(f"<li>{reason}</li>" for reason in report.reasons)
        st.markdown(f'<ul class="reason-list">{reason_items}</ul>', unsafe_allow_html=True)

        st.markdown('<div class="panel-title" style="margin-top:18px;">Analysis Modules</div>', unsafe_allow_html=True)
        module_items = "".join(f'<div class="module-item">{module}</div>' for module in report.planned_modules)
        st.markdown(f'<div class="module-grid">{module_items}</div>', unsafe_allow_html=True)
        if st.button("Scan Another Clip", use_container_width=True):
            reset_scan()
            st.rerun()

    with left:
        show_video_metadata(analysis)
        show_sampled_frames(analysis)
        if face_result is not None:
            show_face_consistency(face_result)


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="PT",
        layout="wide",
    )
    initialize_state()
    apply_theme()

    if st.session_state.page == "intro":
        show_intro_page()
    elif st.session_state.page == "upload":
        show_upload_page()
    else:
        show_report_page()


if __name__ == "__main__":
    main()
