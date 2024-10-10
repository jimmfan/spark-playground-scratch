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



import fitz  # PyMuPDF
import pymupdf4llm
from PIL import Image

def extract_and_screenshot(pdf_bytes, target_terms):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)

    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Extract the text in markdown format with words and chunks
        markdown_text = pymupdf4llm.to_markdown(
            doc,
            pages=[page_number],
            page_chunks=True,
            extract_words=True
        )
        
        # Search for target terms in the extracted markdown
        for term in target_terms:
            if term in markdown_text:
                # Get the coordinates of the term using the word list
                word_positions = [word for word in page.get_text("words") if term in word[4]]
                
                # If the term is found, take a screenshot of the relevant area
                if word_positions:
                    x0, y0, x1, y1 = word_positions[0][:4]
                    
                    # Take a screenshot of the entire page for simplicity, or zoom into the coordinates
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    image_path = f"screenshots/page_{page_number}_{term}.png"
                    pix.save(image_path)

                    # Optional: Crop the image based on coordinates if necessary
                    with Image.open(image_path) as img:
                        cropped_img = img.crop((x0, y0, x1, y1))
                        cropped_img.save(image_path)

    doc.close()


# Define the target term to find in the document
target_terms = ["word or phrase list"]    