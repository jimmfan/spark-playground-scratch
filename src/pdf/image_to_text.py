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


import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def pdf_to_text_from_bytearray_update(pdf_bytearray):
    # Ensure the input is in bytes format
    pdf_bytes = bytes(pdf_bytearray)
    
    # Create a BytesIO object from the PDF bytes
    pdf_stream = io.BytesIO(pdf_bytes)
    
    # Open the PDF from the BytesIO object
    doc = fitz.open("pdf", pdf_stream.read())  # Adjusting based on the version compatibility

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

def save_pdf_to_file(pdf_bytes, file_path='output.pdf'):
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"PDF saved to {file_path}. Please try opening it with a PDF reader.")


save_pdf_to_file(pdf_bytes)



from pyspark.sql.functions import udf, col, when, lit
from pyspark.sql.types import StringType, MapType

# Adjust your UDF to only take the necessary parameters
process_pdf_udf_type1 = udf(lambda pdf_bytes, content_type: process_pdf_column(pdf_bytes, content_type, "type1"), MapType(StringType(), StringType()))
process_pdf_udf_type2 = udf(lambda pdf_bytes, content_type: process_pdf_column(pdf_bytes, content_type, "type2"), MapType(StringType(), StringType()))

# Apply the UDF conditionally based on the document type
df = df.withColumn("parsed_data",
                   when(col("documenttype") == "type1", process_pdf_udf_type1(col("pdf_data"), lit("pdf")))
                   .otherwise(when(col("documenttype") == "type2", process_pdf_udf_type2(col("pdf_data"), lit("pdf")))
                   ))

# Further processing to split "parsed_data" into separate columns as needed
