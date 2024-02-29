import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def pdf_to_text_from_bytes(pdf_bytes):
    # Open the PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

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
