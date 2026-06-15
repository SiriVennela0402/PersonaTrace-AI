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

## 7-Day Build Plan

### Day 1

1. Finalize project idea, problem statement, feature list, and expected output.
2. Create the project structure and basic video upload UI.

### Day 2

1. Extract frames from uploaded video.
2. Display basic video metadata and sampled frames.

### Day 3

1. Add face detection.
2. Track face consistency across sampled frames.

### Day 4

1. Add blink and facial movement analysis.
2. Detect frozen or unnatural face behavior.

### Day 5

1. Extract audio from video.
2. Compare speech activity with mouth movement for lip-sync mismatch.

### Day 6

1. Add video quality checks.
2. Combine all signals into a risk scoring system.

### Day 7

1. Build the final results page.
2. Polish the UI, test sample videos, and prepare resume/GitHub documentation.

