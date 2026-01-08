from dotenv import load_dotenv
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
import pymupdf4llm
import os
from rich.console import Console
from rich.markdown import Markdown
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def read_md_file_plain(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

content = read_md_file_plain("ats_feedback.md")
console = Console()
feedback_ats = Markdown(content)

def extract_text(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path) 
    return md_text

resume_text = extract_text("Resume-Nitin.pdf")

def ats_corrected():
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0.5,api_key=api_key)
    messages=[
    {"role":"system","content":"You are a resume ATS correcter. Fix the resume based on the ATS feedback provided and make it better for the JOB.Do not return any thing other than the fixed resume.Use Keywords: Mirror the language and keywords from the job description.Simple Formatting: Use clean, standard fonts, clear sections, and bullet points; avoid tables, graphics, or headers/footers for critical info.Standard Sections: Include clear sections for contact info, summary, skills, experience, and education. Reverse-Chronological Order: List experiences from most recent to oldest.Tailor for Each Job: Customize your resume for every application by matching the job's specific requirements."},
    {"role":"system","content":content},
    {"role":"user","content":"Fix this following resume based on the ATS feedback.Do not include any thing other than the fixed resume"},
    {"role":"user","content":resume_text}
    ]
    response_ats=model.invoke(messages)
    return response_ats.content

response_ats = ats_corrected()
console = Console()
md = Markdown(response_ats)
console.print(md)

output_file = "ats_corrected.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response_ats)
print(f"Feedback saved to {output_file}")
