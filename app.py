import gradio as gr
import os
import main

def process_resume(uploaded_file, job_description):
    if not uploaded_file or not job_description:
        return "Please upload a resume and provide a job description.", "", "", None
    
    # Gradio uploads files to a temp path accessible via uploaded_file.name
    file_path = uploaded_file.name
    
    try:
        # Invoke the LangGraph pipeline
        result = main.app.invoke({
            "file_path": file_path,
            "resume_md": "",
            "resume_links": "",
            "job_description": job_description,
            "ats_score": 0,
            "improved_resume": "",
            "resume_latex": "",
        })
        
        score_text = f"Processing Complete! Your ATS Score is: {result['ats_score']}/100"
        original_md = result.get("resume_md", "")
        improved_md = result.get("improved_resume", "")
        
        pdf_path = "Documents/Improved_Resume.pdf"
        if os.path.exists(pdf_path):
            return score_text, original_md, improved_md, pdf_path
        else:
            return score_text + " (Warning: PDF generation failed. Check LaTeX logs.)", original_md, improved_md, None
            
    except Exception as e:
        return f"An error occurred: {e}", "", "", None

# Create the Gradio Interface
with gr.Blocks(title="ATS Fixer") as demo:
    gr.Markdown("# ATS Fixer")
    gr.Markdown("Upload your resume and the job description to get an ATS-optimized version!")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload your resume (PDF only)", file_types=[".pdf"])
            jd_input = gr.Textbox(label="Paste Job Description", lines=8, placeholder="Enter job description here...")
            submit_btn = gr.Button("Fix My Resume", variant="primary")
            
        with gr.Column():
            status_output = gr.Textbox(label="Status / Score", interactive=False)
            pdf_output = gr.File(label="Download Improved Resume (PDF)", interactive=False)
            
    with gr.Row():
        with gr.Column():
            original_output = gr.Textbox(label="Original Resume (Markdown)", lines=15, interactive=False)
        with gr.Column():
            improved_output = gr.Textbox(label="Improved Resume (Markdown)", lines=15, interactive=False)
            
    submit_btn.click(
        fn=process_resume,
        inputs=[file_input, jd_input],
        outputs=[status_output, original_output, improved_output, pdf_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
