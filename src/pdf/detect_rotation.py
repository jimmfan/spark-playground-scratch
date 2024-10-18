import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import io

def deskew_image(image):
    image = np.array(image)
    # Handle RGBA images
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    # If no text is found, return the original image
    if len(coords) == 0:
        return Image.fromarray(image)
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)

def main():
    # Step 1: Read and render PDF pages
    doc = fitz.open('input.pdf')
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        images.append(img)

    # Step 2: Deskew each image
    deskewed_images = []
    for img in images:
        deskewed_img = deskew_image(img)
        deskewed_images.append(deskewed_img)

    # Step 3: Create a new PDF with deskewed images
    new_doc = fitz.open()

    for img in deskewed_images:
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_data = img_buffer.read()
        rect = fitz.Rect(0, 0, img.width, img.height)
        page = new_doc.new_page(width=img.width, height=img.height)
        page.insert_image(rect, stream=img_data)

    # Save the new PDF
    new_doc.save('output.pdf')
    new_doc.close()

if __name__ == '__main__':
    main()
