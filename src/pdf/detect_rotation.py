import cv2
import numpy as np

im = cv2.imread("skewed.png")  # Read image
imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

# Corrected thresholding
imOTSU = cv2.threshold(imGray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Get coordinates of positive pixels (text)
coords = np.column_stack(np.where(imOTSU > 0))

# Get a minAreaRect angle
angle = cv2.minAreaRect(coords)[-1]

# Correct angle adjustment
if angle < -45:
    angle = 90 + angle
else:
    angle = angle

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # Compute the rotation matrix
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # Compute new bounding dimensions
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # Adjust the rotation matrix
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # Perform rotation
    return cv2.warpAffine(image, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# Rotate the image
rotated = rotate_image(im, angle)

# Save or display the rotated image
cv2.imwrite("deskewed.png", rotated)
