import fitz  # Import PyMuPDF
import io

def convert_pdf_bytes_to_images(pdf_bytes, image_format='png'):
    """
    Convert PDF bytes to images stored in memory.

    Parameters:
    - pdf_bytes: Bytes object containing the PDF file data.
    - image_format: Format of the output images (e.g., 'png', 'jpeg'). Default is 'png'.

    Returns:
    A list of bytes objects, each representing an image converted from a PDF page.
    """
    images_in_memory = []

    # Open the PDF from the bytes object
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Iterate through each page in the PDF
    for page in doc:
        # Render the page to a pixmap (an image)
        pix = page.get_pixmap()

        # Create a bytes buffer to hold the image data
        img_buffer = io.BytesIO()

        # Save the pixmap (the image) into the bytes buffer
        pix.save(img_buffer, format=image_format)

        # Append the image data to the list
        images_in_memory.append(img_buffer.getvalue())

    return images_in_memory

# Example usage:
# Assuming `pdf_bytes` is your PDF file in bytes
pdf_bytes = b'your PDF data here'  # Replace this with your actual PDF data

# Convert the PDF bytes to images
images = convert_pdf_bytes_to_images(pdf_bytes)

# `images` now contains a list of bytes objects, each representing an image.
# You can process these images further as needed.
