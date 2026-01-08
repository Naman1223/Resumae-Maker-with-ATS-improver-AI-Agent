## This part Takes the PDF and converts it into JSON format
from dotenv import load_dotenv
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
import pymupdf4llm
import os
from rich.console import Console
from rich.markdown import Markdown




def extract_text(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path) 
    return md_text

pdf_path = r"Resume-Nitin.pdf"
md_text = extract_text(pdf_path)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


model= ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0,api_key=api_key)
messages=[
    {"role":"system","content":"You are a text extractor. Extract the text from the given markdown text and convert it into clean markdown format with proper spacing and formatting."},
    {"role":"user","content":md_text}
]
response=model.invoke(messages)

## This part takes the JOB description as user input and comparest it with the Resume and gives the score based on a scale of 1 to 100


def job_description():
    print("Enter Job Description (Ctrl+Z to save):")
    job_description = sys.stdin.read()
    return job_description
job_description = job_description()


messages1=[
    {"role":"system","content":"You are a resume ATS scorer. Score the resume based on the job description and give the score based on a scale of 1 to 100 also give a seprate detailed section on how to fix the ATS score to make it better for the JOB." + job_description},
    {"role":"user","content":response.content}
]
response_ats=model.invoke(messages1)
console = Console()
md = Markdown(response_ats.content)
console.print(md)

## Save the response to a markdown file
output_file = "ats_feedback.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response_ats.content)
