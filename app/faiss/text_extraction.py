import os
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import PyPDF2
import easyocr
from PIL import Image
import io

# Initialize EasyOCR reader (do this once)
reader = easyocr.Reader(['en'])  # For English

def extract_text_from_link(link: str) -> str:
    """Extracts text from a PDF or a web page."""
    try:
        if link.endswith(".pdf"):
            response = requests.get(link)
            temp_pdf_path = "temp_paper.pdf"
            
            with open(temp_pdf_path, "wb") as f:
                f.write(response.content)

            # Use the more comprehensive PDF extraction
            extracted_text = extract_text_from_pdf(temp_pdf_path)
            os.remove(temp_pdf_path)
            
            return extracted_text

        else:
            # Existing web page extraction code
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            extracted_text = "\n".join(tag.get_text().strip() 
                                     for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']) 
                                     if tag.get_text().strip())

        return extracted_text.strip() if extracted_text else "No text extracted."
    
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return f"Error extracting text from {link}: {str(e)}"

def extract_text_from_image(image_data) -> str:
    """Extracts text from image data using EasyOCR."""
    try:
        results = reader.readtext(image_data)
        extracted_text = "\n".join([text[1] for text in results])
        return extracted_text.strip()
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts both regular text and text from images in PDF.
    """
    try:
        doc = fitz.open(file_path)
        full_text = []

        for page in doc:
            # Extract regular text
            text = page.get_text("text").strip()
            if text:
                full_text.append(text)

            # Extract images and their text
            images = page.get_images(full=True)
            for img_index, img_info in enumerate(images):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                
                # Convert image bytes to format suitable for EasyOCR
                image = Image.open(io.BytesIO(image_data))
                image_text = extract_text_from_image(image)
                
                if image_text and not image_text.startswith("Error"):
                    full_text.append(f"Image Text {img_index + 1}: {image_text}")

        combined_text = "\n\n".join(full_text)
        return combined_text if combined_text.strip() else "Error: No text found in PDF."

    except Exception as e:
        return f"Error: Failed to extract text from PDF - {str(e)}"

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text content from PDF, TXT, or image files efficiently.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image(file_path)
                
        else:
            return f"Error: Unsupported file format {file_extension}. Please use PDF, TXT, or image files (PNG, JPG, JPEG)."

    except Exception as e:
        return f"Error: Failed to extract text from file - {str(e)}"
