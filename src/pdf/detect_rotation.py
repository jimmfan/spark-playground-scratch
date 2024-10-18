import fitz  # PyMuPDF
import cv2
import numpy as np

def preprocess_image(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply a binary threshold to get a binary image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Define a horizontal kernel for morphological operations
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    # Apply morphological operations to remove horizontal lines
    detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Subtract the detected lines from the binary image
    processed = cv2.subtract(binary, detected_lines)
    
    return processed

def detect_and_correct_rotation(pdf_path, page_number, crop_ratio=0.1):
    # Open the PDF and load the specified page
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    
    # Convert the page to an image
    pix = page.get_pixmap(dpi=300)
    img = cv2.imdecode(np.frombuffer(pix.tobytes(), np.uint8), cv2.IMREAD_COLOR)

    # Get the dimensions of the image
    (h, w) = img.shape[:2]

    # Crop the top and bottom of the image to remove header/footer lines
    crop_height = int(h * crop_ratio)  # Crop a certain percentage of height from the top and bottom
    cropped_img = img[crop_height:h-crop_height, :]

    # Preprocess the cropped image to remove any remaining horizontal lines
    processed_img = preprocess_image(cropped_img)
    
    # Use edge detection on the preprocessed image
    edges = cv2.Canny(processed_img, 50, 150, apertureSize=3)

    # Find lines using the Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

    # Compute the angle of the lines
    angles = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)

    # Find the median angle
    if len(angles) > 0:
        median_angle = np.median(angles)
    else:
        median_angle = 0

    # Correct the rotation if the angle is significant
    if abs(median_angle) > 0.1:
        (h_cropped, w_cropped) = cropped_img.shape[:2]
        center = (w_cropped // 2, h_cropped // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -median_angle, 1.0)
        rotated_cropped = cv2.warpAffine(cropped_img, rotation_matrix, (w_cropped, h_cropped), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    else:
        rotated_cropped = cropped_img

    # Merge the corrected cropped section back with the original top and bottom sections
    corrected_img = np.vstack((img[:crop_height, :], rotated_cropped, img[h-crop_height:, :]))

    # Close the document
    doc.close()

    # Save or return the rotated image as needed
    return corrected_img

# Usage
pdf_path = "input.pdf"
page_number = 0  # Zero-based index for the first page
corrected_image = detect_and_correct_rotation(pdf_path, page_number, crop_ratio=0.1)

# Save the corrected image to check the output
cv2.imwrite("corrected_page.jpg", corrected_image)
