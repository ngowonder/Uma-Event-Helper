import pytesseract
from PIL import Image
import numpy as np
import cv2
import os

# Configure Tesseract to use the custom trained data
tessdata_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tessdata')
os.environ['TESSDATA_PREFIX'] = tessdata_dir

def extract_event_name_text(pil_img: Image.Image) -> str:
    """Extract event name text from image using Tesseract OCR, trying multiple PSMs for best result."""
    try:
        if isinstance(pil_img, Image.Image):
            img_np = np.array(pil_img)
        else:
            img_np = pil_img

        # Apply preprocessing like event_ocr.py
        # Scale image 2x using high-quality interpolation
        height, width = img_np.shape[:2]
        new_width = int(width * 2.0)
        new_height = int(height * 2.0)
        scaled_img = cv2.resize(img_np, (new_width, new_height), 
                              interpolation=cv2.INTER_CUBIC)
        # Convert to grayscale if needed
        if len(scaled_img.shape) == 3:
            gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = scaled_img
        # Create binary image based on brightness threshold (200)
        # Invert so that dark text becomes black (0) and light background becomes white (255)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        # Invert back to get black text on white background
        processed = cv2.bitwise_not(binary)
        # Use processed image for OCR
        img_np = processed

        configs = [
            '--oem 3 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz \'!,♪☆():.-?!" -c user_defined_dpi=300',
            '--oem 3 --psm 8 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz \'!,♪☆():.-?!" -c user_defined_dpi=300',
            '--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz \'!,♪☆():.-?!" -c user_defined_dpi=300',
        ]
        for config in configs:
            data = pytesseract.image_to_data(img_np, config=config, lang='eng', output_type=pytesseract.Output.DICT)
            text_parts = []
            for i, word in enumerate(data['text']):
                if word.strip() and data['conf'][i] >= 60:
                    text_parts.append(word.strip())
            text = ' '.join(text_parts).strip()
            # Post-processing: Handle common OCR mistakes with special characters
            import re
            text = re.sub(r'\b(Star|star)\b', '☆', text)
            text = re.sub(r'\b(star)\b', '☆', text)
            text = re.sub(r'\b(Star)\b', '☆', text)
            if 'Escape' in text and not text.endswith('!'):
                text += '!'
            # Remove everything before first uppercase letter
            match = re.search(r'[A-Z]', text)
            if match:
                text = text[match.start():]
            # Insert spaces before uppercase letters that follow lowercase letters
            if text:
                text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
            if text:
                return text
        return ""
    except Exception as e:
        print(f"[WARNING] Event name OCR extraction failed: {e}")
        return ""
