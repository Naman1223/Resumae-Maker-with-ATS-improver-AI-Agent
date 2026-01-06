from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class ResumeScorer(BaseModel):
    score: int = Field(description="A score from 1 to 100 based on the resume's ATS compatibility and relevance to the job description.")
    missing_keywords: List[str] = Field(description="List of specific technical keywords found in JD but missing in Resume.")
    formatting_issues: List[str] = Field(description="List of structural or formatting issues (e.g., 'Summary too long').")
    critique: str = Field(description="A brief overall summary of what needs to change.")

llm = ChatGoogleGenerativeAI(model_name="gemini-2.0-flash", api_key="YOUR_API_KEY", temperature=0)