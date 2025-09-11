#!/usr/bin/env python3
"""
PDF OCR Text Extractor
Extract text from scanned PDFs, make PDFs searchable, and convert images to text.

Usage:
    pdf_ocr input.pdf --output text.txt
    pdf_ocr scanned.pdf --make-searchable --output searchable.pdf
    pdf_ocr image.png --output text.txt
    pdf_ocr folder/ --batch --output extracted_texts/
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Union
import tempfile
import shutil

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    import pypdf
    from fpdf import FPDF
    import fitz  # PyMuPDF
except ImportError as e:
    missing_package = str(e).split("'")[1] if "'" in str(e) else str(e)
    print(f"Missing required package: {missing_package}")
    print("Install with: pip install pytesseract pillow pdf2image pypdf2 fpdf2 PyMuPDF")
    sys.exit(1)


class PDFOCRExtractor:
    def __init__(self, language: str = 'eng', dpi: int = 300):
        """
        Initialize PDF OCR extractor.
        
        Args:
            language: OCR language (eng, spa, fra, deu, etc.)
            dpi: DPI for PDF to image conversion (higher = better quality)
        """
        self.language = language
        self.dpi = dpi
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}
        self.supported_pdf_formats = {'.pdf'}
        
        # Check if tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            print("Tesseract OCR not found. Install with:")
            print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("macOS: brew install tesseract")
            print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            sys.exit(1)
    
    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from a single image file."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def extract_text_from_pdf_images(self, pdf_path: Path) -> str:
        """Extract text from PDF by converting pages to images first."""
        try:
            # Convert PDF pages to images
            pages = pdf2image.convert_from_path(pdf_path, dpi=self.dpi)
            
            extracted_texts = []
            for i, page in enumerate(pages):
                print(f"  Processing page {i+1}/{len(pages)}...")
                
                # Save page as temporary image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    page.save(temp_file.name, 'PNG')
                    temp_path = Path(temp_file.name)
                
                # Extract text from image
                text = self.extract_text_from_image(temp_path)
                if text:
                    extracted_texts.append(f"--- Page {i+1} ---\n{text}\n")
                
                # Clean up temp file
                temp_path.unlink()
            
            return '\n'.join(extracted_texts)
            
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def extract_text_from_pdf_direct(self, pdf_path: Path) -> str:
        """Try to extract text directly from PDF (for text-based PDFs)."""
        try:
            text_content = []
            
            # Try with PyMuPDF first (better for complex PDFs)
            try:
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        text_content.append(f"--- Page {page_num+1} ---\n{text}\n")
                doc.close()
                
                if text_content:
                    return '\n'.join(text_content)
            except:
                pass
            
            # Fallback to pypdf
            reader = pypdf.PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {i+1} ---\n{text}\n")
            
            return '\n'.join(text_content) if text_content else ""
            
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def extract_text(self, input_path: Path, force_ocr: bool = False) -> str:
        """
        Extract text from PDF or image file.
        
        Args:
            input_path: Path to PDF or image file
            force_ocr: Force OCR even if PDF has text
            
        Returns:
            Extracted text content
        """
        if not input_path.exists():
            print(f"Error: File '{input_path}' not found.")
            return ""
        
        file_ext = input_path.suffix.lower()
        
        # Handle image files
        if file_ext in self.supported_image_formats:
            print(f"Extracting text from image: {input_path.name}")
            return self.extract_text_from_image(input_path)
        
        # Handle PDF files
        elif file_ext in self.supported_pdf_formats:
            print(f"Processing PDF: {input_path.name}")
            
            # Try direct text extraction first (unless forced OCR)
            if not force_ocr:
                print("  Trying direct text extraction...")
                direct_text = self.extract_text_from_pdf_direct(input_path)
                if direct_text and len(direct_text.strip()) > 50:  # Reasonable amount of text
                    print("  ✓ Found text in PDF")
                    return direct_text
                else:
                    print("  No significant text found, switching to OCR...")
            
            # Use OCR on PDF images
            print("  Converting PDF to images for OCR...")
            return self.extract_text_from_pdf_images(input_path)
        
        else:
            print(f"Error: Unsupported file format '{file_ext}'")
            print(f"Supported formats: {', '.join(self.supported_image_formats | self.supported_pdf_formats)}")
            return ""
    
    def make_searchable_pdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Create a searchable PDF by overlaying OCR text on the original images.
        """
        try:
            print(f"Creating searchable PDF: {output_path.name}")
            
            # Convert PDF pages to images
            pages = pdf2image.convert_from_path(input_path, dpi=self.dpi)
            
            # Create new PDF with text overlay
            doc = fitz.open()
            
            for i, page_image in enumerate(pages):
                print(f"  Processing page {i+1}/{len(pages)}...")
                
                # Save page as temporary image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    page_image.save(temp_file.name, 'PNG')
                    temp_path = Path(temp_file.name)
                
                # Get OCR data with bounding boxes
                ocr_data = pytesseract.image_to_data(page_image, lang=self.language, output_type=pytesseract.Output.DICT)
                
                # Create PDF page with image
                img_doc = fitz.open(temp_path)
                page = doc.new_page(width=img_doc[0].rect.width, height=img_doc[0].rect.height)
                page.insert_image(page.rect, filename=str(temp_path))
                img_doc.close()
                
                # Add invisible text overlay
                for j in range(len(ocr_data['text'])):
                    if int(ocr_data['conf'][j]) > 30:  # Confidence threshold
                        text = ocr_data['text'][j].strip()
                        if text:
                            x = ocr_data['left'][j]
                            y = ocr_data['top'][j]
                            w = ocr_data['width'][j]
                            h = ocr_data['height'][j]
                            
                            # Add invisible text
                            rect = fitz.Rect(x, y, x + w, y + h)
                            page.insert_text((x, y + h), text, fontsize=h, color=(1, 1, 1), overlay=False)
                
                # Clean up temp file
                temp_path.unlink()
            
            # Save the searchable PDF
            doc.save(str(output_path))
            doc.close()
            
            print(f"✓ Created searchable PDF: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating searchable PDF: {e}")
            return False
    
    def batch_extract(self, input_folder: Path, output_folder: Path, 
                     force_ocr: bool = False) -> List[Path]:
        """
        Extract text from all supported files in a folder.
        
        Args:
            input_folder: Folder containing files to process
            output_folder: Folder to save extracted text files
            force_ocr: Force OCR for all PDFs
            
        Returns:
            List of created output files
        """
        if not input_folder.exists() or not input_folder.is_dir():
            print(f"Error: Input folder '{input_folder}' not found.")
            return []
        
        # Create output folder
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Find all supported files
        supported_extensions = self.supported_image_formats | self.supported_pdf_formats
        files_to_process = []
        
        for ext in supported_extensions:
            files_to_process.extend(input_folder.glob(f"*{ext}"))
        
        if not files_to_process:
            print(f"No supported files found in '{input_folder}'")
            return []
        
        print(f"Found {len(files_to_process)} files to process")
        
        created_files = []
        for file_path in files_to_process:
            # Create output filename
            output_file = output_folder / f"{file_path.stem}_extracted.txt"
            
            # Extract text
            text = self.extract_text(file_path, force_ocr)
            
            if text:
                # Save extracted text
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Source: {file_path.name}\n")
                    f.write(f"Extracted on: {Path().cwd()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(text)
                
                created_files.append(output_file)
                print(f"✓ Saved: {output_file.name}")
            else:
                print(f"✗ No text extracted from: {file_path.name}")
        
        return created_files


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs and images using OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf_ocr document.pdf --output text.txt
  pdf_ocr scanned.pdf --make-searchable --output searchable.pdf
  pdf_ocr image.png --output extracted.txt
  pdf_ocr documents/ --batch --output extracted_texts/
  pdf_ocr document.pdf --force-ocr --language spa
        """
    )
    
    parser.add_argument('input', help='Input PDF/image file or folder')
    parser.add_argument('--output', '-o', help='Output file or folder')
    parser.add_argument('--make-searchable', '-s', action='store_true',
                       help='Create searchable PDF instead of text file')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Process all files in input folder')
    parser.add_argument('--force-ocr', '-f', action='store_true',
                       help='Force OCR even if PDF contains text')
    parser.add_argument('--language', '-l', default='eng',
                       help='OCR language (eng, spa, fra, deu, etc.)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI for PDF to image conversion (default: 300)')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = PDFOCRExtractor(language=args.language, dpi=args.dpi)
    
    input_path = Path(args.input).resolve()
    
    # Batch processing
    if args.batch:
        if not args.output:
            output_folder = input_path.parent / f"{input_path.name}_extracted"
        else:
            output_folder = Path(args.output).resolve()
        
        created_files = extractor.batch_extract(input_path, output_folder, args.force_ocr)
        
        if created_files:
            print(f"\n✓ Processed {len(created_files)} files")
            print(f"Output folder: {output_folder}")
        else:
            print("No files were processed successfully")
        return
    
    # Single file processing
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        return
    
    # Set default output path
    if not args.output:
        if args.make_searchable:
            output_path = input_path.parent / f"{input_path.stem}_searchable.pdf"
        else:
            output_path = input_path.parent / f"{input_path.stem}_extracted.txt"
    else:
        output_path = Path(args.output).resolve()
    
    # Create searchable PDF
    if args.make_searchable:
        if input_path.suffix.lower() != '.pdf':
            print("Error: --make-searchable can only be used with PDF files")
            return
        
        success = extractor.make_searchable_pdf(input_path, output_path)
        if not success:
            sys.exit(1)
        return
    
    # Extract text
    text = extractor.extract_text(input_path, args.force_ocr)
    
    if text:
        # Save extracted text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Source: {input_path.name}\n")
            f.write(f"Extracted on: {Path().cwd()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        
        print(f"✓ Text extracted to: {output_path}")
        print(f"Total characters: {len(text)}")
    else:
        print("✗ No text could be extracted")
        sys.exit(1)


if __name__ == "__main__":
    main()
