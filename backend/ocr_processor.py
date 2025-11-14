import cv2
import pytesseract
import numpy as np
from PIL import Image
import io
import re

class OCRProcessor:
    def __init__(self):
        # Configure pytesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

        # Configure for Arabic and English text
        self.custom_config = r'--oem 3 --psm 6 -l ara+eng'

    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)

        return processed

    def extract_text(self, image_data):
        """Extract text from image data"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess the image
            processed_image = self.preprocess_image(opencv_image)

            # Extract text using pytesseract
            text = pytesseract.image_to_string(processed_image, config=self.custom_config)

            return text.strip()

        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def extract_antibiogram_data(self, text):
        """Extract antibiogram data from OCR text"""
        data = {
            'bacteria': [],
            'antibiotics': [],
            'results': []
        }

        # Split text into lines
        lines = text.split('\n')

        # Look for bacteria names (common patterns)
        bacteria_patterns = [
            r'E\. coli',
            r'Staphylococcus aureus',
            r'Klebsiella pneumoniae',
            r'Pseudomonas aeruginosa',
            r'Enterococcus faecalis',
            r'Escherichia coli'
        ]

        # Look for antibiotic names
        antibiotic_patterns = [
            r'Amoxicillin',
            r'Ciprofloxacin',
            r'Gentamicin',
            r'Imipenem',
            r'Vancomycin',
            r'Penicillin',
            r'Tetracycline',
            r'Erythromycin'
        ]

        # Look for sensitivity results
        sensitivity_patterns = [
            r'resistant|R',
            r'sensitive|S',
            r'intermediate|I'
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for bacteria
            for pattern in bacteria_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if pattern not in data['bacteria']:
                        data['bacteria'].append(pattern)
                    break

            # Check for antibiotics
            for pattern in antibiotic_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if pattern not in data['antibiotics']:
                        data['antibiotics'].append(pattern)
                    break

            # Check for results
            for pattern in sensitivity_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    result = match.group().lower()
                    if 'resistant' in result or 'r' in result:
                        data['results'].append('resistant')
                    elif 'sensitive' in result or 's' in result:
                        data['results'].append('sensitive')
                    elif 'intermediate' in result or 'i' in result:
                        data['results'].append('intermediate')
                    break

        return data

    def process_image_file(self, file_path):
        """Process an image file and return extracted data"""
        try:
            # Read image file
            with open(file_path, 'rb') as f:
                image_data = f.read()

            # Extract text
            text = self.extract_text(image_data)

            # Extract antibiogram data
            data = self.extract_antibiogram_data(text)

            return {
                'success': True,
                'text': text,
                'data': data
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
