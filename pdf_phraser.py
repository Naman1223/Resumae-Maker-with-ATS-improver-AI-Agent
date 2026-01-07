## This part Takes the PDF and converts it into JSON format
from dotenv import load_dotenv
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
import pymupdf4llm
import os
def extract_text(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path) 
    return md_text

pdf_path = r"C:\Projects\Resumae Maker with ATS improver AI Agent\Resume-Nitin.pdf"
md_text = extract_text(pdf_path)
api_key = os.getenv("GEMINI_API_KEY")
model= ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0,api_key="AIzaSyCcVfz1oeYBgb8Rd4ZNpt5gvD4Mpx2EfrQ")
messages=[
    {"role":"system","content":"You are a text extractor. Extract the text from the given markdown text and convert it into clean markdown format with proper spacing and formatting."},
    {"role":"user","content":md_text}
]
response=model.invoke(messages)

## This part takes the JOB description as user input and comparest it with the Resume and gives the score based on a scale of 1 to 100
model= ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0,api_key="AIzaSyCcVfz1oeYBgb8Rd4ZNpt5gvD4Mpx2EfrQ")

print("Enter text (Ctrl+D or Ctrl+Z to save):")
job_description = sys.stdin.read()

messages=[
    {"role":"system","content":"You are a resume scorer. Score the resume based on the job description and give the score based on a scale of 1 to 100." + job_description},
    {"role":"user","content":md_text}
]
response_ats=model.invoke(messages)
print(response_ats.content)

