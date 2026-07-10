import os
import fitz  # PyMuPDF

class Conversion:
    def __init__(self, file_path):
        self.source = file_path

    def to_md(self):
        doc = fitz.open(self.source)
        text = ""
        for page in doc:
            text += page.get_text() + "\n\n"
            
        os.makedirs("Documents", exist_ok=True)
        with open("Documents/Resume_output.md", "w", encoding="utf-8") as f:
            f.write(text)
            
        return text

    def extract_links(self):
        """Extract all embedded hyperlinks from the PDF with their display text."""
        doc = fitz.open(self.source)
        links = []
        seen = set()
        
        for page in doc:
            for link in page.get_links():
                uri = link.get("uri", "")
                if not uri or uri in seen:
                    continue
                seen.add(uri)
                
                # Get the display text at the link's position
                rect = fitz.Rect(link["from"])
                display_text = page.get_text("text", clip=rect).strip()
                
                if display_text:
                    links.append({"text": display_text, "url": uri})
                else:
                    links.append({"text": uri, "url": uri})
        
        return links