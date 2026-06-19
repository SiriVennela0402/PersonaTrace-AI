from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path("output/pdf/personatrace_ai_full_project_report.pdf")


class SectionRule(Flowable):
    def __init__(self, color=colors.HexColor("#2dd4bf"), width=1.4):
        super().__init__()
        self.color = color
        self.width = width
        self.height = 10

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.width)
        self.canv.line(0, 5, self._width, 5)

    def wrap(self, available_width, available_height):
        self._width = available_width
        return available_width, self.height


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=36,
            textColor=colors.HexColor("#edf6ff"),
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#a9bfd6"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=4,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.8,
            leading=14,
            textColor=colors.HexColor("#263445"),
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.3,
            leading=11,
            textColor=colors.HexColor("#64748b"),
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            backColor=colors.HexColor("#eaf8fb"),
            borderColor=colors.HexColor("#9be8f3"),
            borderWidth=0.6,
            borderPadding=9,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=12,
            textColor=colors.HexColor("#263445"),
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.9,
            leading=9.5,
            textColor=colors.HexColor("#edf6ff"),
        ),
        "table_body": ParagraphStyle(
            "TableBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=9.4,
            textColor=colors.HexColor("#263445"),
        ),
        "table_key": ParagraphStyle(
            "TableKey",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=9.5,
            textColor=colors.HexColor("#263445"),
        ),
        "cover_label": ParagraphStyle(
            "CoverLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#38d5ff"),
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#0b1220"))
    canvas.rect(0, height - 0.38 * inch, width, 0.38 * inch, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#38d5ff"))
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(0.55 * inch, height - 0.24 * inch, "PersonaTrace AI")
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 0.55 * inch, 0.34 * inch, f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#05070d"))
    canvas.rect(0, 0, width, height, stroke=0, fill=1)

    for radius, color, alpha in [
        (260, colors.HexColor("#123c55"), 0.35),
        (170, colors.HexColor("#3b1d65"), 0.28),
        (90, colors.HexColor("#0f766e"), 0.18),
    ]:
        canvas.setFillColor(color)
        canvas.circle(width * 0.72, height * 0.72, radius, stroke=0, fill=1)

    canvas.setStrokeColor(colors.HexColor("#38d5ff"))
    canvas.setLineWidth(1.2)
    canvas.circle(width / 2, height * 0.64, 54, stroke=1, fill=0)
    canvas.rotate(45)
    canvas.rect(width / 2.0 + 80, height * 0.08, 76, 76, stroke=1, fill=0)
    canvas.rotate(-45)
    canvas.setFillColor(colors.HexColor("#edf6ff"))
    canvas.circle(width / 2, height * 0.64, 11, stroke=0, fill=1)
    canvas.restoreState()


def bullet_list(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["bullet"]), bulletColor=colors.HexColor("#0f766e")) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=18,
    )


def section(title, styles):
    return [Paragraph(title, styles["h1"]), SectionRule(), Spacer(1, 6)]


def module_table(rows, styles):
    data = [
        [
            Paragraph("Module", styles["table_header"]),
            Paragraph("What It Checks", styles["table_header"]),
            Paragraph("Output", styles["table_header"]),
        ]
    ]
    for module, checks, output in rows:
        data.append(
            [
                Paragraph(module, styles["table_key"]),
                Paragraph(checks, styles["table_body"]),
                Paragraph(output, styles["table_body"]),
            ]
        )
    table = Table(data, colWidths=[1.25 * inch, 3.15 * inch, 1.45 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b1220")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#edf6ff")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#263445")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.55 * inch,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=frame, onPage=cover_page),
            PageTemplate(id="main", frames=frame, onPage=header_footer),
        ]
    )

    story = []
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("IDENTITY THREAT SCREENING", styles["cover_label"]))
    story.append(Paragraph("PersonaTrace AI", styles["title"]))
    story.append(
        Paragraph(
            "AI-Based Deepfake Interview Risk Detection System for Remote Hiring",
            styles["subtitle"],
        )
    )
    story.append(
        Paragraph(
            "A practical computer vision and cybersecurity project that analyzes interview videos "
            "for face consistency, behavior patterns, speech-mouth timing, and video artifact clues.",
            styles["subtitle"],
        )
    )
    story.append(Spacer(1, 2.4 * inch))
    story.append(Paragraph("Full Project Explanation and Technical Report", styles["cover_label"]))
    story.append(PageBreak())

    story.extend(section("1. Project Overview", styles))
    story.append(
        Paragraph(
            "PersonaTrace AI is a remote interview risk-screening system. A user uploads a short "
            "interview video, and the system analyzes visual, behavioral, audio-video, and quality "
            "signals to produce an explainable interview risk score. The goal is not to prove that "
            "a person is fake, but to identify suspicious evidence that should trigger manual review.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Core idea: remote hiring now has a trust problem. A candidate on camera could be using "
            "a deepfake face, proxy speaker, virtual camera, face-swap tool, or mismatched identity. "
            "PersonaTrace AI gives recruiters or security reviewers a structured way to inspect risk.",
            styles["callout"],
        )
    )

    story.extend(section("2. Problem It Solves", styles))
    story.append(
        Paragraph(
            "Remote interviews are convenient, but they reduce identity assurance. Companies may "
            "make hiring decisions, grant system access, or continue onboarding based on a video call "
            "that could be manipulated. This can lead to wrong hiring, identity fraud, data exposure, "
            "and security risk.",
            styles["body"],
        )
    )
    story.append(
        bullet_list(
            [
                "Detects missing or unstable face presence across the interview clip.",
                "Flags suspicious behavior such as very low blink variation or frozen face motion.",
                "Checks whether speech activity appears without matching mouth movement.",
                "Highlights video quality clues such as blur, unstable lighting, and abrupt frame jumps.",
                "Produces a clear score and reasons instead of a black-box yes/no decision.",
            ],
            styles,
        )
    )

    story.extend(section("3. User Workflow", styles))
    workflow_rows = [
        [
            Paragraph("Opening Screen", styles["table_key"]),
            Paragraph("Animated PersonaTrace AI entry page introduces the identity threat screening workflow.", styles["table_body"]),
        ],
        [
            Paragraph("Evidence Upload", styles["table_key"]),
            Paragraph("User uploads a short interview video in MP4, MOV, AVI, or MKV format.", styles["table_body"]),
        ],
        [
            Paragraph("Signal Extraction", styles["table_key"]),
            Paragraph("The system extracts metadata, sampled frames, audio, face regions, mouth regions, and quality metrics.", styles["table_body"]),
        ],
        [
            Paragraph("Trace Report", styles["table_key"]),
            Paragraph("The app shows an interview risk score, risk level, key findings, and module-level metrics.", styles["table_body"]),
        ],
    ]
    story.append(Table(workflow_rows, colWidths=[1.7 * inch, 4.3 * inch], style=[
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf8fb")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#263445")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(PageBreak())
    story.extend(section("4. System Modules", styles))
    story.append(
        module_table(
            [
                ["Video Intake", "Reads uploaded video, FPS, frame count, duration, resolution, and sampled frames.", "Video metadata and evidence frames"],
                ["Face Consistency", "Detects face presence, multiple faces, face position jitter, and face size jitter.", "Face risk score and reasons"],
                ["Behavior Pattern", "Checks eye signal, blink-like state changes, and frozen/static face motion.", "Behavior risk score"],
                ["Lip-Sync Signal", "Extracts audio, estimates speech activity, checks mouth movement, and scores speech-mouth mismatch.", "Lip-sync risk score"],
                ["Video Quality", "Checks blur, lighting variation, and abrupt frame differences.", "Quality risk score"],
                ["Risk Report", "Combines module scores into a final explainable interview risk score.", "Final score, level, findings"],
            ],
            styles,
        )
    )

    story.extend(section("5. How The Detection Works", styles))
    story.append(Paragraph("Face consistency", styles["h2"]))
    story.append(
        Paragraph(
            "OpenCV face detection is applied to sampled frames. PersonaTrace AI measures whether "
            "a face appears consistently, whether multiple faces appear, and whether face position "
            "or size changes sharply across frames.",
            styles["body"],
        )
    )
    story.append(Paragraph("Blink and frozen face behavior", styles["h2"]))
    story.append(
        Paragraph(
            "The system looks for eye-region signals and face crop changes over time. A face with "
            "very low movement or no blink-like variation can be flagged as suspicious or unnatural, "
            "especially in longer clips.",
            styles["body"],
        )
    )
    story.append(Paragraph("Speech and mouth timing", styles["h2"]))
    story.append(
        Paragraph(
            "Audio is extracted with imageio-ffmpeg. The system estimates speech activity using audio "
            "energy windows and compares it with mouth-region motion between frames. If speech exists "
            "while mouth movement is weak, the lip-sync risk increases.",
            styles["body"],
        )
    )
    story.append(Paragraph("Video quality artifacts", styles["h2"]))
    story.append(
        Paragraph(
            "The quality module calculates frame sharpness using Laplacian variance, lighting variation "
            "using brightness changes, and possible glitches using abrupt frame differences.",
            styles["body"],
        )
    )

    story.append(PageBreak())
    story.extend(section("6. Risk Scoring", styles))
    story.append(
        Paragraph(
            "The final interview risk score is a weighted combination of module scores. If audio is "
            "available, face consistency, behavior, lip-sync, and video quality all contribute. If audio "
            "is unavailable, the system still produces a visual risk score from face, behavior, and quality.",
            styles["body"],
        )
    )
    story.append(
        bullet_list(
            [
                "Low risk: no major warning signals in sampled windows.",
                "Medium risk: one or more signals need human review.",
                "High risk: multiple warning signals suggest possible manipulation or identity risk.",
            ],
            styles,
        )
    )
    story.append(
        Paragraph(
            "Important: the score is a screening signal, not a final identity verdict. High-risk results "
            "should trigger manual verification, additional identity checks, and review by a human.",
            styles["callout"],
        )
    )

    story.extend(section("7. Technology Stack", styles))
    tech_rows = [
        [Paragraph("Python", styles["table_header"]), Paragraph("Core programming language for video processing and scoring logic.", styles["table_body"])],
        [Paragraph("Streamlit", styles["table_header"]), Paragraph("Interactive web app interface with intro, upload, and report pages.", styles["table_body"])],
        [Paragraph("OpenCV", styles["table_header"]), Paragraph("Video reading, frame extraction, face detection, image differences, blur checks.", styles["table_body"])],
        [Paragraph("NumPy", styles["table_header"]), Paragraph("Numerical processing for frame, audio, and scoring calculations.", styles["table_body"])],
        [Paragraph("imageio-ffmpeg", styles["table_header"]), Paragraph("Bundled FFmpeg helper for audio extraction from uploaded video files.", styles["table_body"])],
    ]
    story.append(Table(tech_rows, colWidths=[1.55 * inch, 4.45 * inch], style=[
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0b1220")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#edf6ff")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#263445")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.7),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.extend(section("8. Project File Structure", styles))
    story.append(
        Paragraph(
            "app.py controls the Streamlit UI and app flow. The src/personatrace package contains "
            "separate modules for video analysis, face consistency, behavior analysis, lip-sync analysis, "
            "video quality analysis, and final report scoring.",
            styles["body"],
        )
    )
    story.append(
        bullet_list(
            [
                "app.py - Streamlit interface and user workflow.",
                "video_analysis.py - metadata and frame extraction.",
                "face_analysis.py - face detection and consistency risk.",
                "behavior_analysis.py - blink and frozen face behavior.",
                "lip_sync_analysis.py - audio-video speech-mouth timing.",
                "video_quality_analysis.py - blur, lighting, and glitch checks.",
                "report.py - final risk score and findings.",
            ],
            styles,
        )
    )

    story.extend(section("9. Limitations", styles))
    story.append(
        bullet_list(
            [
                "It is not a forensic-grade detector and should not be treated as proof of fraud.",
                "Accuracy depends on video quality, lighting, camera angle, face visibility, and audio availability.",
                "OpenCV-based face and eye detection can miss faces in difficult angles or low-light scenes.",
                "Lip-sync scoring is approximate because it uses sampled windows rather than a trained lip-reading model.",
                "The best use is screening and explanation, followed by human review.",
            ],
            styles,
        )
    )

    story.extend(section("10. Resume And Demo Value", styles))
    story.append(
        Paragraph(
            "PersonaTrace AI is a strong resume project because it combines AI, computer vision, "
            "cybersecurity, audio-video analysis, and a real remote hiring problem. It is more unique "
            "than a standard chatbot or resume analyzer because it addresses modern identity fraud risk.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Resume line: Built PersonaTrace AI, a Streamlit and OpenCV-based deepfake interview risk "
            "screening system that analyzes face consistency, blink and motion behavior, speech-mouth "
            "timing, and video artifacts to generate an explainable remote hiring risk score.",
            styles["callout"],
        )
    )

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT.resolve())
