from dotenv import load_dotenv
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
import pymupdf4llm
import os
from rich.console import Console
from rich.markdown import Markdown
import subprocess
import sys
from Score import job_description
from Correction import ats_corrected
load_dotenv()

result = subprocess.run(
    [sys.executable, "Correction.py"], 
    capture_output=True, 
    text=True
)
output = result.stdout

job_content = job_description()
console = Console()
job_description = Markdown(job_content)



api_key = os.getenv("GEMINI_API_KEY")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0,api_key=api_key)
messages=[{"role":"system","content":"You are a resume ATS Checker based on a job description and check the resume and give the score based on a scale of 1 to 100.Do not include any thing other than the score if the score is more than 90." + job_description},
{"role":"user","content":output}
]
response_ats=model.invoke(messages)
console = Console()
md = Markdown(response_ats)
console.print(md)
