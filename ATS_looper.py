from dotenv import load_dotenv
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import os
from rich.console import Console
from rich.markdown import Markdown
import subprocess
import sys
import pymupdf4llm
from Score import job_description
from Correction import ats_corrected
import time
load_dotenv()

def extract_text(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path) 
    return md_text

pdf_path = r"Resume-Nitin.pdf"
md_text = extract_text(pdf_path)

with open("ats_corrected.md", "w", encoding="utf-8") as f:
    f.write(md_text)

def job_description():
    print("Enter Job Description (Ctrl+Z to save):")
    job_description = sys.stdin.read()
    return job_description
job_description = job_description()

output_file_job = "job_description.md"
with open(output_file_job, "w", encoding="utf-8") as f:
    f.write(job_description)
score = 0
while score < 50:
    def extract_numbers_from_file(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    score =extract_numbers_from_file("ats_score.txt")
    Score1 = subprocess.run(
    [sys.executable, "Score.py"], 
    capture_output=True, 
    text=True
    )
    Score_output = Score1.stdout
    time.sleep(5)

    result = subprocess.run(
    [sys.executable, "Correction.py"], 
    capture_output=True, 
    text=True
    )
    output = result.stdout
