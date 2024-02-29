import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

import os

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def pdf_to_text(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    text = ""
    for page_num in range(len(doc)):
        # Get the page
        page = doc.load_page(page_num)

        # Get the image of the page
        pix = page.get_pixmap()
        image_bytes = io.BytesIO(pix.tobytes("png"))
        image = Image.open(image_bytes)

        # Use OCR to extract text
        text += pytesseract.image_to_string(image)

    # Close the document
    doc.close()
    return text

# Example usage

pdf_path = 'CCR-HOA.pdf'

extracted_text = pdf_to_text(pdf_path)

# Save the extracted text to a file
with open('output.txt', 'w') as file:
    file.write(extracted_text)
