import easyocr
import cv2

def detect_rotation_with_easyocr(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path, detail=1)

    rotations = []
    for (bbox, text, _) in result:
        # bbox contains coordinates of the text box: [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = bbox
        width = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        height = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        if height > width:
            rotations.append(90)  # Possible vertical orientation

    # Infer overall rotation based on the detected orientations
    if len(rotations) > len(result) / 2:
        return 90
    else:
        return 0

# Usage
image_path = "scanned_page.jpg"
rotation = detect_rotation_with_easyocr(image_path)
print(f"Detected rotation: {rotation} degrees")
