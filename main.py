from pydantic import Field
import os
import re
import pydantic as pd
import subprocess
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from conversions import Conversion

load_dotenv()


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences (```json ... ```) that LLMs often add."""
    return re.sub(r"^```(?:json)?\s*\n?|\n?```\s*$", "", text.strip()).strip()

class SchemaFeedback(pd.BaseModel):
    ats_score: int = Field(description="ATS score ranging from 0-100")
    improvements: list[dict] = Field(description="List of improvements in the Resume and the suggestion to improve it")

class AgentState(TypedDict):
    file_path: str
    resume_md: str
    resume_links: str
    job_description: str
    improved_resume: str
    resume_latex: str
    ats_score: int
    latex_log: str


def md(state: AgentState):
    file_path = state["file_path"]
    converter = Conversion(file_path)
    state["resume_md"] = converter.to_md()
    
    # Extract embedded links from the PDF
    links = converter.extract_links()
    if links:
        links_text = "\n".join(f'- "{l["text"]}" -> {l["url"]}' for l in links)
    else:
        links_text = "No embedded links found."
    state["resume_links"] = links_text
    print(f"Extracted {len(links)} embedded links from PDF")
    return state


def analyze_and_improve(state: AgentState) -> AgentState:
    """Score, rewrite, and convert to LaTeX in a single LLM call."""

    resume_md       = state.get("resume_md", "")
    resume_links    = state.get("resume_links", "")
    job_description = state.get("job_description", "")

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("MODEL") or "gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
        max_output_tokens=16384,
    )

    print("Processing: Score + Rewrite + LaTeX (single call)...")

    PROMPT = r"""You are a senior ATS expert, resume writer, and LaTeX typesetter.

Do ALL three tasks in one response:

1. Score the resume against the job description (Keywords:/30, Achievements:/20, Headings:/15, Formatting:/15, Verbs:/10, Contact:/5, Grammar:/5).
2. Rewrite the resume in Markdown to maximize ATS score. Do NOT fabricate, invent, or assume any information, dates, companies, project details, metrics, or certifications. You may only rephrase and optimize existing text. Use standard ATS-friendly headings (e.g., CONTACT, SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION, CERTIFICATIONS) but ONLY if the candidate has actual content for them. Do NOT add empty sections or invent details.
3. Convert the improved resume to compilable LaTeX (article 11pt, geometry 0.5in, enumitem, titlesec, hyperref, fontenc, inputenc, xcolor — no exotic packages, must compile with pdflatex).

CRITICAL RULES:
- ANTI-HALLUCINATION: Do NOT invent or estimate any metrics, percentages, numbers, dates, companies, or credentials (degrees/certifications). If the original resume has no metrics (e.g., 'improved page speed'), do NOT invent one (e.g., 'improved page speed by 40%'). Only optimize the vocabulary (e.g., 'Optimized page load speed and backend efficiency').
- DYNAMIC SECTIONS: Do NOT create sections (like PROJECTS or CERTIFICATIONS) if the candidate does not have any in their original resume.
- Preserve ALL original URLs, links, email addresses, phone numbers, and profile links EXACTLY as they appear in the original resume. Do NOT modify, shorten, or fabricate any links.
- In the LaTeX output, ALL URLs must be clickable using \href{URL}{display text}. Use \href{mailto:email}{email} for emails. Use \href{tel:phone}{phone} for phone numbers.
- Configure hyperref with: \usepackage[hidelinks]{hyperref} so links are clickable but not boxed.
- Do NOT use \newpage, \clearpage, or \pagebreak. The resume must fit naturally in 1 page (2 max) with NO blank pages.
- Do NOT add extra \vspace or \vfill that could push content to a new page.

Output EXACTLY in this format:

ATS_SCORE: <number>
---IMPROVED_RESUME---
<improved resume in Markdown>
---LATEX---
<full LaTeX from \documentclass to \end{document}>

--- RESUME ---
__RESUME_MD__

--- EMBEDDED LINKS FROM ORIGINAL PDF ---
Below is the exact mapping of display text to URL extracted from the original PDF. You MUST use these exact URLs in the improved resume and LaTeX output. Match each link to the correct place based on the display text.
__RESUME_LINKS__

--- JOB DESCRIPTION ---
__JOB_DESCRIPTION__"""

    response = llm.invoke([("human", PROMPT.replace("__RESUME_MD__", resume_md).replace("__RESUME_LINKS__", resume_links).replace("__JOB_DESCRIPTION__", job_description))])

    text = response.content
    ats_score = 0
    improved_resume = ""
    resume_latex = ""

    # Parse the three sections
    if "ATS_SCORE:" in text and "---IMPROVED_RESUME---" in text and "---LATEX---" in text:
        score_part, rest = text.split("---IMPROVED_RESUME---", 1)
        md_part, latex_part = rest.split("---LATEX---", 1)

        improved_resume = md_part.strip()
        resume_latex = strip_markdown_fences(latex_part.strip())

        try:
            ats_score = int(re.search(r"ATS_SCORE:\s*(\d+)", score_part).group(1))
        except (AttributeError, ValueError):
            ats_score = 0
    else:
        # Fallback: treat entire response as improved resume
        improved_resume = text

    print(f"ATS Score: {ats_score}")

    state["ats_score"]       = ats_score
    state["improved_resume"] = improved_resume
    state["resume_latex"]    = resume_latex
    return state


def tex_to_pdf(state: AgentState) -> AgentState:
    import shutil
    import os
    
    os.makedirs("Documents", exist_ok=True)
    tex_path = os.path.abspath("Documents/Improved_Resume.tex")
    
    latex_content = state.get("resume_latex", "").strip()
    
    # Trim everything before \documentclass (explanations, backticks, spaces)
    if r"\documentclass" in latex_content:
        latex_content = latex_content[latex_content.find(r"\documentclass"):]
        
    # Post-process: remove blank-page-causing commands
    latex_content = re.sub(r'\\newpage', '', latex_content)
    latex_content = re.sub(r'\\clearpage', '', latex_content)
    latex_content = re.sub(r'\\pagebreak', '', latex_content)
    
    # Ensure hyperref uses hidelinks (no ugly boxes around links)
    latex_content = latex_content.replace(
        r'\usepackage{hyperref}',
        r'\usepackage[hidelinks]{hyperref}'
    )
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)
        
    out_dir  = os.path.abspath("Documents")

    pdflatex_bin = shutil.which("pdflatex")
    if not pdflatex_bin:
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\miktex-pdflatex.exe"),
            r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\Program Files\MiKTeX\miktex\bin\x64\miktex-pdflatex.exe",
            r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64\miktex-pdflatex.exe",
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                pdflatex_bin = candidate
                break

    if not pdflatex_bin:
        pdflatex_bin = "pdflatex"

    state["latex_log"] = ""
    try:
        result = subprocess.run(
            [pdflatex_bin, "-interaction=nonstopmode", "-output-directory", out_dir, tex_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("PDF generated: Documents/Improved_Resume.pdf")
            state["latex_log"] = "Success"
        else:
            log_lines = result.stdout.strip().splitlines()
            last_lines = "\n".join(log_lines[-30:])
            state["latex_log"] = f"pdflatex exited with code {result.returncode}.\nLast 30 lines of log:\n{last_lines}"
            print(state["latex_log"])
    except FileNotFoundError:
        state["latex_log"] = f"ERROR: pdflatex command not found at '{pdflatex_bin}'. Make sure LaTeX (TeX Live/MiKTeX) is installed on the system."
        print(state["latex_log"])
    except subprocess.TimeoutExpired:
        state["latex_log"] = "ERROR: pdflatex compilation timed out after 60 seconds."
        print(state["latex_log"])

    return state


# ── Build and run the LangGraph pipeline ──
graph = StateGraph(AgentState)
graph.add_node("md", md)
graph.add_node("analyze_and_improve", analyze_and_improve)
graph.add_node("tex_to_pdf", tex_to_pdf)

graph.add_edge(START, "md")
graph.add_edge("md", "analyze_and_improve")
graph.add_edge("analyze_and_improve", "tex_to_pdf")
graph.add_edge("tex_to_pdf", END)

app = graph.compile()

if __name__ == "__main__":
    # ── Collect user inputs before running the pipeline ──
    file_path       = "Documents/Resume.pdf"
    job_description = input("Enter the job description: ").strip()

    result = app.invoke({
        "file_path":       file_path,
        "resume_md":       "",
        "job_description": job_description,
        "ats_score":       0,
        "improved_resume": "",
        "resume_latex":    "",
    })

    print(f"\n=== ATS SCORE: {result['ats_score']} / 100 ===")
    print("\n=== IMPROVED RESUME ===")
    print(result["improved_resume"])
    print("\n=== FILES SAVED ===")
    print("LaTeX:    Documents/Improved_Resume.tex")
    print("PDF:      Documents/Improved_Resume.pdf")

