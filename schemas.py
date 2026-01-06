from typing import List, Optional
from pydantic import BaseModel, Field

# 1. Contact Information
class ContactInfo(BaseModel):
    full_name: str = Field(description="The candidate's full name")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number")
    linkedin: Optional[str] = Field(description="LinkedIn profile URL")
    github: Optional[str] = Field(description="GitHub or portfolio URL")
    location: Optional[str] = Field(description="City and State/Country only")

# 2. Work Experience (The most important section for ATS)
class WorkExperience(BaseModel):
    job_title: str = Field(description="The exact job title held")
    company: str = Field(description="Name of the company")
    start_date: str = Field(description="Start date (e.g., 'Jan 2022')")
    end_date: str = Field(description="End date or 'Present'")
    # We force the AI to write a list of strings, not a single block of text.
    # This makes it easier to render bullet points later.
    responsibilities: List[str] = Field(
        description="List of 3-5 bullet points describing achievements and responsibilities. Start each with an action verb."
    )

# 3. Education
class Education(BaseModel):
    degree: str = Field(description="Degree name (e.g., B.S. Computer Science)")
    institution: str = Field(description="University or School name")
    graduation_year: str = Field(description="Year of graduation")

# 4. Projects (Critical for tech resumes)
class Project(BaseModel):
    name: str = Field(description="Name of the project")
    description: str = Field(description="Brief description of what the project does")
    tech_stack: List[str] = Field(description="List of technologies used (e.g., ['Python', 'Django'])")
    link: Optional[str] = Field(description="Link to the live project or repo")

# 5. The Main Resume Container
class Resume(BaseModel):
    contact_info: ContactInfo
    summary: str = Field(
        description="A 2-3 sentence professional summary tailored to the job description."
    )
    skills: List[str] = Field(
        description="A list of technical and soft skills relevant to the job."
    )
    work_experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)