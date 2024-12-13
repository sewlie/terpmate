import pdfplumber
import os
import shutil
import time
import re

# Path to the folder containing PDFs
PDF_FOLDER = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\TERPbot\terpmate\COAs"
NON_FLOWER_FOLDER = os.path.join(PDF_FOLDER, "NON-FLOWER")

# Ensure the NON-FLOWER folder exists
os.makedirs(NON_FLOWER_FOLDER, exist_ok=True)

def is_flower_product(first_page_text):
    """
    Check if the first page of the PDF contains references to flower products.
    Specifically looks for 'Category/Type' followed by 'flower' or 'Matrix: Flower'.
    """
    if not first_page_text:
        return False

    # Normalize text for matching
    normalized_text = " ".join(first_page_text.lower().split())
    
    # Debug: Log normalized text for analysis
    print(f"Normalized text for detection:\n{normalized_text[:500]}")  # Log first 500 characters
    
    # Check for "Category/Type" followed by "flower" or "Matrix: Flower"
    category_match = re.search(r"category/type:\s?.*flower", normalized_text)
    matrix_match = re.search(r"matrix:\s?flower", normalized_text)
    
    return bool(category_match or matrix_match)

def move_file_with_retry(src, dest):
    """
    Move a file with retries to avoid WinError 32.
    """
    for _ in range(5):  # Retry up to 5 times
        try:
            shutil.move(src, dest)
            return True
        except PermissionError:
            time.sleep(0.5)  # Wait half a second before retrying
    return False

def sort_pdfs(folder_path):
    """
    Sort PDFs into Flower and Non-Flower categories.
    Move Non-Flower PDFs to a separate folder.
    """
    pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                first_page_text = pdf.pages[0].extract_text() if pdf.pages else ""
            
            # Ensure the PDF file is closed before attempting to move it
            if first_page_text and is_flower_product(first_page_text):
                print(f"Kept in COAs: {pdf_file}")
            else:
                # Move to NON-FLOWER folder
                dest_path = os.path.join(NON_FLOWER_FOLDER, os.path.basename(pdf_file))
                if move_file_with_retry(pdf_file, dest_path):
                    print(f"Moved to NON-FLOWER: {pdf_file}")
                else:
                    print(f"Failed to move {pdf_file} after multiple retries.")
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

if __name__ == "__main__":
    sort_pdfs(PDF_FOLDER)
