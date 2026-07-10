import streamlit as st
import os
import main

st.set_page_config(page_title="ATS Fixer", layout="wide")
st.title("ATS Fixer")
st.write("Upload your resume and the job description to get an ATS-optimized version!")

# 1. PDF Upload
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf")

# 2. Job Description Input (Text Area)
job_description = st.text_area("Paste Job Description", height=200)

# 3. Process Button
if st.button("Fix My Resume", type="primary"):
    if uploaded_file and job_description:
        # Create a temporary path for the PDF
        file_path = "temp_resume.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.status("Processing your resume...", expanded=True) as status:
            try:
                status.write("📄 Extracting text from PDF...")
                result = main.app.invoke({
                    "file_path": file_path,
                    "resume_md": "",
                    "resume_links": "",
                    "job_description": job_description,
                    "ats_score": 0,
                    "improved_resume": "",
                    "resume_latex": "",
                    "latex_log": "",
                })
                status.update(label="✅ Done!", state="complete")

                st.success(f"Processing Complete! ATS Score: {result['ats_score']}/100")

                # 4. Results Display
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Original Resume (Markdown)")
                    st.text(result.get("resume_md", ""))

                with col2:
                    st.subheader("Improved Resume")
                    st.text(result.get("improved_resume", ""))

                # Download button for the generated PDF
                pdf_path = "Documents/Improved_Resume.pdf"
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Download Improved Resume (PDF)",
                            data=pdf_file,
                            file_name="Improved_Resume.pdf",
                            mime="application/pdf",
                        )
                else:
                    st.warning("Could not generate PDF. Check the LaTeX compilation logs below:")
                    if result.get("latex_log"):
                        st.code(result.get("latex_log"), language="text")

            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"An error occurred: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    else:
        st.warning("Please upload both a resume and a job description.")
