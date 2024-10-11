import fitz  # PyMuPDF

def extract_annotations(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_info = {
                "page": page_number,
                "type": annot.type[0],  # Annotation type (e.g., text, highlight, etc.)
                "rect": annot.rect,  # The rectangle where the annotation is located
                "content": annot.info.get("content", ""),  # Any text content associated with the annotation
                "author": annot.info.get("title", "Unknown"),  # Author of the annotation if available
            }
            
            print(f"Annotation found on page {page_number}: {annot_info}")

    doc.close()

# Example usage
with open("financial_document.pdf", "rb") as file:
    pdf_bytes = file.read()

extract_annotations(pdf_bytes)