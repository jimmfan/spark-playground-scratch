import cv2
import numpy as np

# Define a sharpening kernel
sharpening_kernel = np.array([[-1, -1, -1], 
                              [-1, 9, -1],
                              [-1, -1, -1]])

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

img = cv2.imread('path/to/image.jpg', cv2.IMREAD_GRAYSCALE)
denoised_img = cv2.medianBlur(img, 5)
binarized_img = cv2.adaptiveThreshold(denoised_img, 255,
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
morph_img = cv2.morphologyEx(binarized_img, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
deskewed_img = deskew(morph_img)
sharpened_img = cv2.filter2D(deskewed_img, -1, sharpening_kernel)
final_img = cv2.convertScaleAbs(sharpened_img, alpha=1.5, beta=50)

cv2.imwrite('final_preprocessed_image.jpg', final_img)
