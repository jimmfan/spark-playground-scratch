import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import io

def deskew_image(image):
    image_cv = np.array(image)
    if image_cv.shape[2] == 4:
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    
    if lines is None:
        return image
    
    angles = []
    for rho, theta in lines[:,0]:
        angle = np.rad2deg(theta)
        # Focus on near-horizontal lines (top and bottom margins)
        if angle < 10 or angle > 170:
            adjusted_angle = angle if angle <= 90 else angle - 180
            angles.append(adjusted_angle)
    
    if not angles:
        return image
    
    median_angle = np.median(angles)
    
    (h, w) = image_cv.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image_cv, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rotated)

def main():
    doc = fitz.open('input.pdf')
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        images.append(img)

    deskewed_images = []
    for img in images:
        deskewed_img = deskew_image(img)
        deskewed_images.append(deskewed_img)

    new_doc = fitz.open()

    for img in deskewed_images:
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
