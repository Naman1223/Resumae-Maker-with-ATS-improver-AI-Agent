import fitz  

def extract_text_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = ""
    for page in doc:
        text_content += page.get_text()
    return text_content

m=(extract_text_fitz(r"C:\Projects\Resumae Maker with ATS improver AI Agent\Resume-Nitin.pdf"))
print(m)