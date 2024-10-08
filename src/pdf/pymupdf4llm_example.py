import fitz  # PyMuPDF
import pymupdf4llm

def extract_pdf_text_from_bytes(pdf_bytes):
    # Open the PDF from the byte array
    pdf_document = fitz.open("pdf", pdf_bytes)
    
    # Initialize a container for extracted text
    extracted_text = ""
    
    # Iterate over each page
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        
        # Using PyMuPDF4LLM to convert each page into Markdown format for better structure
        markdown_text = pymupdf4llm.to_markdown(pdf_document, pages=[page_number])
        
        # Collect all extracted markdown text
        extracted_text += markdown_text + "\n\n"

    # Close the document after processing
    pdf_document.close()
    
    return extracted_text

# Example usage
with open("example.pdf", "rb") as file:
    pdf_bytes = file.read()

pdf_text = extract_pdf_text_from_bytes(pdf_bytes)
print(pdf_text)
