import cv2
import numpy as np

def resizeImgWidth(img: np.ndarray, width: int = 224) -> np.ndarray:
    img2 = img.copy()
    if img2 is None:
        print("Error: Unable to load image.")
        return
    
    (h, w) = img2.shape[:2]
    aspect_ratio = width / float(w)
    new_width = width
    new_height = int(h * aspect_ratio)
    
    return cv2.resize(img2, (new_width, new_height), interpolation=cv2.INTER_AREA)