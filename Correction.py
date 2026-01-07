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

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0,api_key=api_key)
messages=[
    {"role":"system","content":"You are a resume ATS correcter. Fix the resume based on the ATS feedback and make it better for the JOB."},
    {"role":"system","content":content},
    {"role":"user","content":"Fix the following resume based on the ATS feedback and make it better for the JOB."},
    {"role":"user","content":resume_text}
]
response_ats=model.invoke(messages)
console = Console()
md = Markdown(response_ats.content)
console.print(md)
