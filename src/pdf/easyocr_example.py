import fitz  # PyMuPDF
import easyocr
from PIL import Image
import io

# Initialize EasyOCR reader for English (you can add more languages if needed)
reader = easyocr.Reader(['en'])

# Function to extract text from an image using EasyOCR
def ocr_from_image(image):
    # Convert the pixmap to a PIL image for OCR processing
    img = Image.open(io.BytesIO(image.tobytes()))
    # Use EasyOCR to extract text from the image
    result = reader.readtext(img, detail=0)
    # Join the extracted text into a single string
    return "\n".join(result)

# Open the PDF using PyMuPDF
pdf_document = fitz.open("example.pdf")

# Variable to store the extracted text from the PDF
full_text = ""

# Iterate through the pages of the PDF
for page_num in range(pdf_document.page_count):
    page = pdf_document.load_page(page_num)
    print(f"Processing page {page_num + 1}/{pdf_document.page_count}")

    # Try to extract text directly from the page
    text = page.get_text("text")

    if text.strip():
        # If text is found, append it to the full_text
        full_text += f"Page {page_num + 1} (Text):\n{text}\n\n"
    else:
        # If no text is found, it could be an image-based page, so process with OCR
        print(f"Page {page_num + 1} seems to contain an image.")
        
        # Extract the image from the page
        pix = page.get_pixmap()

        # Use EasyOCR to extract text from the image
        ocr_text = ocr_from_image(pix)
        full_text += f"Page {page_num + 1} (OCR from Image):\n{ocr_text}\n\n"

# Save the full extracted text to a file
with open("output_extracted_text.txt", "w") as output_file:
    output_file.write(full_text)

pdf_document.close()
