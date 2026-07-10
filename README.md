---
title: ATS Fixer - Resume Optimizer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# ATS Fixer - Resume Optimizer

Upload your resume PDF and a job description to get an ATS-optimized version with:
- ATS Score (0-100)
- Improved resume in Markdown
- Compilable LaTeX output
- Downloadable PDF

## Setup

This app requires the following secrets to be configured in your Hugging Face Space settings:

- `GOOGLE_API_KEY` — Your Google Gemini API key
- `MODEL` — The model name (e.g., `gemini-2.5-flash`)
