#!/usr/bin/env python3
"""
Simple PDF Page Manager
Quick tool to analyze and remove pages from PDFs.
"""

import sys
from pathlib import Path
import pymupdf as fitz  # type: ignore # PyMuPDF
import pypdf  # type: ignore

def analyze_pdf(pdf_path):
    """Analyze PDF and show page breakdown."""
    print(f"Analyzing: {pdf_path.name}")
    
    # Use PyMuPDF for analysis
    doc = fitz.open(pdf_path)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    
    print(f"\n=== PDF Analysis ===")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Total pages: {len(doc)}")
    
    print(f"\nPage breakdown:")
    print(f"{'Page':<4} {'Images':<7} {'Text Chars':<10} {'Size Est.':<10}")
    print("-" * 40)
    
    page_sizes = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        images = page.get_images()
        text_len = len(page.get_text())
        
        # Rough size estimation based on images
        est_size = len(images) * 0.5 + (text_len / 1000) * 0.1
        page_sizes.append((i+1, len(images), text_len, est_size))
        
        print(f"{i+1:<4} {len(images):<7} {text_len:<10} {est_size:.1f} MB")
    
    doc.close()
    
    # Find problematic pages
    heavy_pages = [p for p in page_sizes if p[3] > 2 or p[1] >= 3]
    if heavy_pages:
        print(f"\nPages with heavy content:")
        for page_num, images, text, size in heavy_pages:
            print(f"  Page {page_num}: {images} images, ~{size:.1f} MB estimated")
    
    return page_sizes

def remove_pages(input_path, output_path, pages_to_remove):
    """Remove specified pages from PDF."""
    reader = pypdf.PdfReader(input_path)
    writer = pypdf.PdfWriter()
    
    total_pages = len(reader.pages)
    pages_to_keep = [i for i in range(total_pages) if (i + 1) not in pages_to_remove]
    
    print(f"\nRemoving pages: {sorted(pages_to_remove)}")
    print(f"Keeping {len(pages_to_keep)} out of {total_pages} pages")
    
    for page_num in pages_to_keep:
        writer.add_page(reader.pages[page_num])
    
    # Copy metadata
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    return True

def parse_pages(page_input, total_pages):
    """Parse page input like '1,3,5-7' into list of page numbers."""
    pages = []
    
    for part in page_input.split(','):
        part = part.strip()
        
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    
    # Validate
    invalid = [p for p in pages if p < 1 or p > total_pages]
    if invalid:
        raise ValueError(f"Invalid pages: {invalid}. PDF has pages 1-{total_pages}")
    
    return list(set(pages))

def interactive_mode(pdf_path):
    """Interactive page removal."""
    page_info = analyze_pdf(pdf_path)
    total_pages = len(page_info)
    
    print(f"\n=== Interactive Page Removal ===")
    print(f"Current size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")
    
    while True:
        print(f"\nOptions:")
        print(f"1. Remove specific pages (e.g., 1,3,5-7)")
        print(f"2. Remove pages with most images")
        print(f"3. Exit")
        
        choice = input(f"Choice (1-3): ").strip()
        
        if choice == '1':
            pages_input = input(f"Pages to remove (e.g., 1,3,5-7): ").strip()
            try:
                pages = parse_pages(pages_input, total_pages)
                return pages
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            # Find pages with 3+ images
            heavy_pages = [p[0] for p in page_info if p[1] >= 3]
            if heavy_pages:
                print(f"Pages with 3+ images: {heavy_pages}")
                confirm = input(f"Remove these pages? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return heavy_pages
            else:
                print("No pages found with 3+ images")
        
        elif choice == '3':
            return []
        
        else:
            print("Invalid choice")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pdf_page_manager.py file.pdf                    # Interactive mode")
        print("  python pdf_page_manager.py file.pdf --remove 1,3,5-7   # Remove specific pages")
        print("  python pdf_page_manager.py file.pdf --analyze          # Just analyze")
        return
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return
    
    if len(sys.argv) == 2:
        # Interactive mode
        pages_to_remove = interactive_mode(pdf_path)
        
        if pages_to_remove:
            output_path = pdf_path.parent / f"{pdf_path.stem}_edited.pdf"
            
            if remove_pages(pdf_path, output_path, pages_to_remove):
                original_size = pdf_path.stat().st_size / (1024*1024)
                new_size = output_path.stat().st_size / (1024*1024)
                reduction = (1 - new_size/original_size) * 100
                
                print(f"\n✓ Created: {output_path.name}")
                print(f"Original: {original_size:.2f} MB")
                print(f"New: {new_size:.2f} MB (reduced by {reduction:.1f}%)")
        else:
            print("No changes made")
    
    elif '--analyze' in sys.argv:
        analyze_pdf(pdf_path)
    
    elif '--remove' in sys.argv:
        try:
            idx = sys.argv.index('--remove')
            page_input = sys.argv[idx + 1]
            
            # Get total pages first
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            pages_to_remove = parse_pages(page_input, total_pages)
            output_path = pdf_path.parent / f"{pdf_path.stem}_edited.pdf"
            
            if remove_pages(pdf_path, output_path, pages_to_remove):
                original_size = pdf_path.stat().st_size / (1024*1024)
                new_size = output_path.stat().st_size / (1024*1024)
                reduction = (1 - new_size/original_size) * 100
                
                print(f"\n✓ Created: {output_path.name}")
                print(f"Original: {original_size:.2f} MB")
                print(f"New: {new_size:.2f} MB (reduced by {reduction:.1f}%)")
        
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
