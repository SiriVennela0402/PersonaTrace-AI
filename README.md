# PersonaTrace AI

AI-Based Deepfake Interview Risk Detection System

PersonaTrace AI is a computer vision and cybersecurity project for remote hiring safety. It analyzes a short interview video and generates an explainable risk score using face consistency, blink and motion behavior, speech-mouth timing, and video quality signals.

This is not a forensic deepfake detector. It is a practical interview risk-screening prototype that flags suspicious signals for manual review.

## Problem

Remote interviews can be manipulated with deepfake faces, virtual cameras, proxy speakers, stolen identities, and voice/video mismatch tools. That creates hiring risk, identity risk, and potential company security exposure.

PersonaTrace AI helps screen interview clips before trust is granted.

## Features

- Dark animated product-style Streamlit interface
- Separate intro, upload, and trace report flow
- Video metadata extraction
- Sampled evidence frame extraction
- Face detection and face consistency scoring
- Multiple-face and missing-face warnings
- Blink/eye signal and frozen face behavior analysis
- Audio extraction and speech activity detection
- Mouth movement and speech-mouth mismatch scoring
- Video sharpness, lighting variation, and frame glitch checks
- Combined explainable interview risk score

## Example Output

```text
Trace Analysis Report

Interview Risk Score: 78%
Risk Level: High

Key Findings:
- Face missing in several sampled frames
- Low blink variation in sampled frames
- Speech activity appears without matching mouth movement
- Possible frame glitch or abrupt visual jump detected
```

## Tech Stack

- Python
- Streamlit
- OpenCV
- NumPy
- imageio-ffmpeg

## How to Run

```powershell
cd C:\Users\siriv\OneDrive\Documents\cs
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Test Video

A UI test clip is included at:

```text
samples/personatrace_ui_test.avi
```

This clip is useful for testing upload, metadata extraction, frame extraction, and report flow. For face, blink, and lip-sync testing, use a short 5-10 second selfie video with visible face and speech.

## Resume Line

Built PersonaTrace AI, an AI-based deepfake interview risk detection system that analyzes remote interview videos for face consistency, blink and motion behavior, speech-mouth mismatch, and video artifact signals, producing an explainable risk score for hiring security review.

## Disclaimer

PersonaTrace AI is a student-level screening prototype. It should not be used as the sole basis for hiring, identity verification, or fraud decisions.



