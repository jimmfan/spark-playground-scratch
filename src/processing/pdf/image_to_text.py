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



from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType, MapType

# Define the schema of your dictionary, assuming all possible keys are known
schema = MapType(StringType(), StringType())

# Create a UDF that wraps the process_pdf_column function, including the document type as a parameter
process_pdf_udf = udf(process_pdf_column, schema)

# Apply the UDF to your DataFrame
df = df.withColumn("parsed_data", process_pdf_udf("pdf_data", lit("pdf"), "document_type"))

# Now, assuming your keys are static and known (e.g., 'key1', 'key2'), you can directly expand "parsed_data" into columns
df = df.withColumn("key1", df["parsed_data"]["key1"])
df = df.withColumn("key2", df["parsed_data"]["key2"])
# Repeat for all keys...

# Display the result to verify
df.show()


# Further processing to split "parsed_data" into separate columns as needed
