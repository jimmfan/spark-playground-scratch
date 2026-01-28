import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import io

def preprocess_image(image):
    image_cv = np.array(image)
    if image_cv.shape[2] == 4:
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        gray_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2)
    # Remove small noise (tiny black dots)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    return binary

def crop_margins(binary_image, original_image):
    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return original_image
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    content_contour = contours[0]
    x, y, w, h = cv2.boundingRect(content_contour)
    cropped_image = original_image.crop((x, y, x + w, y + h))
    return cropped_image

def deskew_image(image):
    image_cv = np.array(image)
    if image_cv.ndim == 2:
        gray = image_cv
    else:
        gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    gray_inv = cv2.bitwise_not(gray)
    _, binary = cv2.threshold(
        gray_inv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    else:
        angle = angle
    (h, w) = image_cv.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_cv = cv2.warpAffine(
        image_cv, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE)
    if rotated_cv.ndim == 2:
        rotated = Image.fromarray(rotated_cv)
    else:
        rotated = Image.fromarray(cv2.cvtColor(rotated_cv, cv2.COLOR_BGR2RGB))
    return rotated

def main():
    doc = fitz.open('input.pdf')
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        images.append(img)

    processed_images = []

    for img in images:
        binary = preprocess_image(img)
        cropped_img = crop_margins(binary, img)
        deskewed_img = deskew_image(cropped_img)
        processed_images.append(deskewed_img)

    new_doc = fitz.open()

    for img in processed_images:
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_data = img_buffer.read()
        rect = fitz.Rect(0, 0, img.width, img.height)
        page = new_doc.new_page(width=img.width, height=img.height)
        page.insert_image(rect, stream=img_data)

    new_doc.save('output.pdf')
    new_doc.close()

if __name__ == '__main__':
    main()
