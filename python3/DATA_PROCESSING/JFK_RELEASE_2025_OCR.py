#########
#            
#    JFK release 2025 downloader and OCR parser. 
#    Not the best, but what really is - 
#    Does a decent job but due to quality, hand writing, redactions, or other errors
#    Can misrepresent what the words and or letters:
#        (Language: [spanish vs englishe], 
#        Characters: [May identify incorrect character set])
#    
##########
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from pdf2image import convert_from_bytes
import pytesseract

# Base URL containing the PDF links
base_url = "https://www.archives.gov/research/jfk/release-2025"

# Directories to store downloaded PDFs and extracted text
PDF_DIR = "pdf_files"
TEXT_DIR = "pdf_contents"

def get_pdf_links(url):
    """
    Fetch the target page and return a list of absolute URLs for PDF files.
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            if not href.startswith('http'):
                href = requests.compat.urljoin(url, href)
            pdf_links.append(href)
    return pdf_links

def download_pdf(pdf_url):
    """
    Download the PDF from the URL and save it locally if not already present.
    Returns the PDF content in bytes.
    """
    file_name = pdf_url.split("/")[-1]
    file_path = os.path.join(PDF_DIR, file_name)
    
    if os.path.exists(file_path):
        print(f"File already exists locally: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()
    else:
        print(f"Downloading PDF: {pdf_url}")
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_bytes = response.content
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        return pdf_bytes

def extract_text_from_pdf(pdf_bytes):
    """
    Extract text using PyPDF2 from the PDF bytes.
    """
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def ocr_pdf(pdf_bytes, poppler_path=None):
    """
    Use OCR to extract text from scanned PDF pages.
    Converts PDF pages to images and applies Tesseract OCR using US English.
    """
    try:
        if poppler_path:
            images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)
        else:
            images = convert_from_bytes(pdf_bytes)
        ocr_text = ""
        for image in images:
            # Use US English ('eng') and additional config for better accuracy
            text = pytesseract.image_to_string(image, lang='eng', config='--oem 1 --psm 3')
            ocr_text += text + "\n"
        return ocr_text
    except Exception as e:
        print("OCR extraction failed:", e)
        return ""

def process_pdf(pdf_url, poppler_path=None):
    """
    Downloads (or loads locally) a PDF, extracts text via PyPDF2 and, if necessary, via OCR.
    Returns the extracted text.
    """
    print(f"\nProcessing PDF: {pdf_url}")
    try:
        pdf_bytes = download_pdf(pdf_url)
        extracted_text = extract_text_from_pdf(pdf_bytes)
        if not extracted_text.strip():
            print("No extractable text found using PyPDF2, attempting OCR...")
            extracted_text = ocr_pdf(pdf_bytes, poppler_path=poppler_path)
        if extracted_text.strip():
            return extracted_text
        else:
            print("No text could be extracted from this PDF.")
            return None
    except Exception as e:
        print(f"Error processing {pdf_url}: {e}")
        return None

def main():
    # Ensure directories exist for PDFs and text outputs
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(TEXT_DIR, exist_ok=True)
    pdf_links = get_pdf_links(base_url)
    print(f"Found {len(pdf_links)} PDF files.")
    # Optional: set the poppler_path if Poppler isn't in your PATH (e.g., on Windows)
    poppler_path = None  # e.g., r'C:\poppler\bin'
    for pdf_url in pdf_links:
        text = process_pdf(pdf_url, poppler_path=poppler_path)
        if text:
            file_name = pdf_url.split("/")[-1]
            text_file_path = os.path.join(TEXT_DIR, file_name + ".txt")
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extracted text saved to: {text_file_path}")
            # Print sample output to terminal (first 300 characters)
            print("Sample OCR output (first 300 characters):")
            print(text[:300])
        else:
            print(f"Skipping saving for {pdf_url} as no text was extracted.")
if __name__ == "__main__":
    main()
