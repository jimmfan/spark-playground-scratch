import fitz  # PyMuPDF
import cv2
import numpy as np

def detect_and_correct_rotation_based_on_lines(pdf_path, page_number):
    # Open the PDF and load the specified page
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    
    # Convert the page to an image
    pix = page.get_pixmap(dpi=300)
    img = cv2.imdecode(np.frombuffer(pix.tobytes(), np.uint8), cv2.IMREAD_COLOR)
    
    # Convert to grayscale and use edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect lines using the Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    
    # Collect angles of the detected lines
    angles = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            # We are interested in lines that are mostly vertical
            if -85 < angle < -5 or 5 < angle < 85:
                angles.append(angle)
    
    # Calculate the median angle
    if len(angles) > 0:
        median_angle = np.median(angles)
    else:
        median_angle = 0

    # Correct the rotation based on the median angle
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, -median_angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    # Close the document
    doc.close()
    
    # Save or return the rotated image as needed
    return rotated

# Usage
pdf_path = "input.pdf"
page_number = 0  # Zero-based index for the first page
corrected_image = detect_and_correct_rotation_based_on_lines(pdf_path, page_number)

# Save the corrected image to verify the output
cv2.imwrite("corrected_page.jpg", corrected_image)
