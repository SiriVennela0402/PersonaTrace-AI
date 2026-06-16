# PersonaTrace AI

AI-Based Deepfake Interview Risk Detection System

PersonaTrace AI is a student-level computer vision and cybersecurity project for remote hiring safety. It analyzes a short interview video and produces an explainable deepfake risk score based on face consistency, mouth-speech timing, blink behavior, face movement, and basic video quality clues.

The system is not a forensic or police-level detector. It is a practical risk-screening tool that highlights suspicious signals in online interview videos.

## Problem Statement

Remote hiring has a trust problem. During an online interview, a candidate may use a deepfake face, voice changer, proxy speaker, virtual camera, stolen identity, or face-swap tool. This can lead to wrong hiring decisions, unauthorized access, data exposure, and company security risk.

PersonaTrace AI helps identify suspicious interview recordings by scoring risk indicators and explaining the main reasons behind the score.

## Core Checks

- Face consistency across frames
- Sudden face distortion or missing face
- Lip-sync mismatch between speech and mouth movement
- Blink and face movement pattern
- Frozen or unnatural facial behavior
- Video quality clues such as blur, lighting mismatch, and frame glitches
- Voice-video mismatch where speech exists but mouth movement is weak

## MVP Output

```text
PersonaTrace AI Report

Deepfake Risk Score: 78%
Risk Level: High

Reasons:
- Lip-sync mismatch detected
- Face boundary instability
- Low blink variation
- Speech present with weak mouth movement
```

## Tech Stack

- Python
- Streamlit
- OpenCV
- MediaPipe
- NumPy
- MoviePy
- Librosa



