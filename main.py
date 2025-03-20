"""
fuzzy_edge_detection.py

This script implements edge detection using a Fuzzy Inference System.
It uses the existing FIS implementation to create rules for detecting edges in images.
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
from src.fis import FuzzyInferenceSystem
from src.linguisticVariable import LinguisticVariable
from src.membershipFunction import MembershipFunctionFactory
from utils.image import resizeImgWidth

def create_edge_detection_fis():
    """Create and configure a fuzzy inference system for edge detection"""
    fis = FuzzyInferenceSystem()
    
    # Create input variable: intensity_diff (represents difference in neighboring pixels)
    intensity_diff = LinguisticVariable("intensity_diff", [0, 255])
    intensity_diff.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("small", [0, 0, 10, 30])
    )
    intensity_diff.add_membership_function(
        MembershipFunctionFactory.create_triangular("medium", [20, 50, 80])
    )
    intensity_diff.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("large", [60, 120, 255, 255])
    )
    
    # Create input variable: neighborhood_variance (local variance in a small window)
    neighborhood_variance = LinguisticVariable("neighborhood_variance", [0, 5000])
    neighborhood_variance.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("low", [0, 0, 500, 1000])
    )
    neighborhood_variance.add_membership_function(
        MembershipFunctionFactory.create_triangular("medium", [700, 1500, 2500])
    )
    neighborhood_variance.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("high", [2000, 3500, 5000, 5000])
    )
    
    # Create output variable: edge_strength
    edge_strength = LinguisticVariable("edge_strength", [0, 100])
    edge_strength.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("weak", [0, 0, 20, 40])
    )
    edge_strength.add_membership_function(
        MembershipFunctionFactory.create_triangular("moderate", [30, 50, 70])
    )
    edge_strength.add_membership_function(
        MembershipFunctionFactory.create_trapezoidal("strong", [60, 80, 100, 100])
    )
    
    # Add variables to the fuzzy inference system
    fis.add_input_variable(intensity_diff)
    fis.add_input_variable(neighborhood_variance)
    fis.add_output_variable(edge_strength)
    
    # Add rules
    rules_str = """
    IF intensity_diff is small AND neighborhood_variance is low THEN edge_strength is weak;
    IF intensity_diff is small AND neighborhood_variance is medium THEN edge_strength is weak;
    IF intensity_diff is small AND neighborhood_variance is high THEN edge_strength is moderate;
    IF intensity_diff is medium AND neighborhood_variance is low THEN edge_strength is weak;
    IF intensity_diff is medium AND neighborhood_variance is medium THEN edge_strength is moderate;
    IF intensity_diff is medium AND neighborhood_variance is high THEN edge_strength is strong;
    IF intensity_diff is large AND neighborhood_variance is low THEN edge_strength is moderate;
    IF intensity_diff is large AND neighborhood_variance is medium THEN edge_strength is strong;
    IF intensity_diff is large AND neighborhood_variance is high THEN edge_strength is strong
    """
    
    fis.add_rules_from_string(rules_str)
    
    return fis

def calculate_intensity_difference(img, i, j):
    """Calculate average intensity difference around pixel (i,j)"""
    h, w = img.shape
    
    # Check boundaries
    if i == 0 or i == h-1 or j == 0 or j == w-1:
        return 0
    
    # Calculate differences with neighboring pixels (horizontal and vertical)
    diff_left = abs(int(img[i, j]) - int(img[i, j-1]))
    diff_right = abs(int(img[i, j]) - int(img[i, j+1]))
    diff_up = abs(int(img[i, j]) - int(img[i-1, j]))
    diff_down = abs(int(img[i, j]) - int(img[i+1, j]))
    
    # Return max difference (most significant edge direction)
    return max(diff_left, diff_right, diff_up, diff_down)

def calculate_neighborhood_variance(img, i, j, window_size=3):
    """Calculate variance in a small window around pixel (i,j)"""
    h, w = img.shape
    
    # Check boundaries for window
    half = window_size // 2
    if i < half or i >= h-half or j < half or j >= w-half:
        return 0
    
    # Extract window
    window = img[i-half:i+half+1, j-half:j+half+1]
    return np.var(window)

def detect_edges(image_path, threshold=50):
    """Detect edges in an image using fuzzy inference"""
    # Create fuzzy inference system
    fis = create_edge_detection_fis()
    
    # Read and preprocess image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    img = resizeImgWidth(img)
    # Create edge map (same size as input image)
    h, w = img.shape
    edge_map = np.zeros((h, w), dtype=np.uint8)
    
    # Process each pixel (excluding borders)
    for i in range(1, h-1):
        for j in range(1, w-1):
            # Calculate input features for FIS
            intensity_diff = calculate_intensity_difference(img, i, j)
            neighborhood_var = calculate_neighborhood_variance(img, i, j)
            
            # Skip processing if the inputs are very low (optimization)
            if intensity_diff < 5 and neighborhood_var < 100:
                continue
            
            # Run fuzzy inference
            inputs = {
                "intensity_diff": intensity_diff,
                "neighborhood_variance": neighborhood_var
            }
            
            result = fis.infer(inputs)
            edge_strength = result["edge_strength"]
            
            # Apply threshold to determine edge
            if edge_strength > threshold:
                edge_map[i, j] = 255
    
    return img, edge_map

def main():
    """Main function to run edge detection"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fuzzy_edge_detection.py <image_path> [threshold]")
        print("Example: python fuzzy_edge_detection.py sample.jpg 50")
        sys.exit(1)
    
    image_path = sys.argv[1]
    threshold = 25  # Default threshold
    
    if len(sys.argv) >= 3:
        threshold = int(sys.argv[2])
    
    try:
        print(f"Processing image: {image_path}")
        print(f"Edge threshold: {threshold}")
        
        original, edge_map = detect_edges(image_path, threshold)
        
        # Display results
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.title("Original Image")
        plt.imshow(original, cmap='gray')
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        plt.title("Fuzzy Edge Detection")
        plt.imshow(edge_map, cmap='gray')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # Save output
        output_path = image_path.split('.')[0] + '_edges.png'
        cv2.imwrite(output_path, edge_map)
        print(f"Edge map saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()