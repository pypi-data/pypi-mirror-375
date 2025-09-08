# AFADS — Advanced Face Age Detection System

Local, on-device face age estimation using InsightFace. Includes demos for webcam (Tkinter), Pygame UI, and a REST API.

## Install

```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
# or, after you publish:
# pip install advanced-face-age-recognition-module
```

## Quick Start

```python
from afads import AFADS
engine = AFADS()
print(engine.assess("selfie.jpg", return_dict=True))
```

## Demos

- `python -m afads.extras.afads_webcam_consent` — webcam with consent popup + live overlay
- `python -m afads.extras.pygame_webcam` — Pygame viewer with keys to toggle rules
- `uvicorn afads.extras.afads_server:app --reload` — REST server + simple HTML form

## Rules

- If any age detected → allow
- If age ≥ 18 → require `prob_over_18 ≥ 0.85` (or 0.90 for stricter)

## Privacy

This library runs fully on-device. Ask for consent before using the camera. Do not store images by default.
