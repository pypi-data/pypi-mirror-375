#!/usr/bin/env python3
"""
PDF Editor - Interactive PDF Page and Image Management
Remove pages, extract pages, delete images, and optimize PDFs locally.

Usage:
    pdf_editor document.pdf --pages              # Interactive page selection
    pdf_editor document.pdf --images             # Interactive image removal
    pdf_editor document.pdf --remove-pages 3,5,7-9
    pdf_editor document.pdf --keep-pages 1-5,10
    pdf_editor document.pdf --split-pages        # Split into individual pages
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import tempfile
import shutil

try:
    import pypdf
    from PIL import Image
    import fitz  # PyMuPDF for better image handling
    import io
except ImportError as e:
    missing_package = str(e).split("'")[1] if "'" in str(e) else str(e)
    print(f"Missing required package: {missing_package}")
    print("Install with: pip install pypdf PyMuPDF pillow")
    sys.exit(1)

# Optional GUI imports
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    import threading
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class PDFEditor:
    def __init__(self):
        """Initialize PDF editor."""
        self.current_pdf = None
        self.pages_to_remove = set()
        self.images_to_remove = {}  # {page_num: [image_indices]}
        
    def analyze_pdf(self, pdf_path: Path) -> Dict:
        """Analyze PDF structure and return information about pages and images."""
        try:
            # Use PyMuPDF for better analysis
            doc = fitz.open(pdf_path)
            analysis = {
                'total_pages': len(doc),
                'file_size_mb': pdf_path.stat().st_size / (1024 * 1024),
                'pages': []
            }
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get page info
                page_info = {
                    'page_num': page_num + 1,
                    'size': (page.rect.width, page.rect.height),
                    'images': [],
                    'text_length': len(page.get_text()),
                    'estimated_size_mb': 0
                }
                
                # Get images on this page
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image details
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        image_info = {
                            'index': img_index,
                            'xref': xref,
                            'width': pix.width,
                            'height': pix.height,
                            'colorspace': pix.colorspace.name if pix.colorspace else 'Unknown',
                            'estimated_size_kb': pix.width * pix.height * (pix.n / 1024)
                        }
                        page_info['images'].append(image_info)
                        page_info['estimated_size_mb'] += image_info['estimated_size_kb'] / 1024
                        
                        pix = None  # Free memory
                    except Exception as e:
                        print(f"Warning: Could not analyze image {img_index} on page {page_num + 1}: {e}")
                
                analysis['pages'].append(page_info)
            
            doc.close()
            return analysis
            
        except Exception as e:
            print(f"Error analyzing PDF: {e}")
            return None
    
    def print_pdf_analysis(self, analysis: Dict):
        """Print a detailed analysis of the PDF."""
        print(f"\n=== PDF Analysis ===")
        print(f"File size: {analysis['file_size_mb']:.2f} MB")
        print(f"Total pages: {analysis['total_pages']}")
        
        total_images = sum(len(page['images']) for page in analysis['pages'])
        print(f"Total images: {total_images}")
        
        print(f"\nPage breakdown:")
        print(f"{'Page':<4} {'Images':<7} {'Est.Size':<10} {'Text':<6} {'Dimensions':<12}")
        print("-" * 50)
        
        for page in analysis['pages']:
            print(f"{page['page_num']:<4} {len(page['images']):<7} "
                  f"{page['estimated_size_mb']:.1f} MB{'':<3} "
                  f"{page['text_length']:<6} {int(page['size'][0])}x{int(page['size'][1])}")
        
        # Show pages with most images/size
        largest_pages = sorted(analysis['pages'], 
                              key=lambda x: x['estimated_size_mb'], reverse=True)[:3]
        
        if largest_pages[0]['estimated_size_mb'] > 1:
            print(f"\nLargest pages by estimated size:")
            for page in largest_pages:
                if page['estimated_size_mb'] > 0.5:
                    print(f"  Page {page['page_num']}: {page['estimated_size_mb']:.1f} MB "
                          f"({len(page['images'])} images)")
    
    def remove_pages(self, input_path: Path, output_path: Path, 
                    pages_to_remove: List[int]) -> bool:
        """Remove specified pages from PDF."""
        try:
            reader = pypdf.PdfReader(input_path)
            writer = pypdf.PdfWriter()
            
            total_pages = len(reader.pages)
            pages_to_keep = [i for i in range(total_pages) 
                           if (i + 1) not in pages_to_remove]
            
            print(f"Removing pages: {sorted(pages_to_remove)}")
            print(f"Keeping {len(pages_to_keep)} out of {total_pages} pages")
            
            for page_num in pages_to_keep:
                writer.add_page(reader.pages[page_num])
            
            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error removing pages: {e}")
            return False
    
    def keep_pages(self, input_path: Path, output_path: Path, 
                  pages_to_keep: List[int]) -> bool:
        """Keep only specified pages in PDF."""
        try:
            reader = pypdf.PdfReader(input_path)
            writer = pypdf.PdfWriter()
            
            total_pages = len(reader.pages)
            
            print(f"Keeping pages: {sorted(pages_to_keep)}")
            print(f"Keeping {len(pages_to_keep)} out of {total_pages} pages")
            
            for page_num in sorted(pages_to_keep):
                if 1 <= page_num <= total_pages:
                    writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based
                else:
                    print(f"Warning: Page {page_num} doesn't exist (PDF has {total_pages} pages)")
            
            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error keeping pages: {e}")
            return False
    
    def remove_images_from_page(self, input_path: Path, output_path: Path,
                               images_to_remove: Dict[int, List[int]]) -> bool:
        """Remove specific images from specific pages."""
        try:
            doc = fitz.open(input_path)
            
            for page_num, image_indices in images_to_remove.items():
                if 1 <= page_num <= len(doc):
                    page = doc.load_page(page_num - 1)  # Convert to 0-based
                    
                    print(f"Removing {len(image_indices)} images from page {page_num}")
                    
                    # Get all images on the page
                    image_list = page.get_images()
                    
                    # Remove images in reverse order to maintain indices
                    for img_index in sorted(image_indices, reverse=True):
                        if 0 <= img_index < len(image_list):
                            try:
                                # This is complex in PyMuPDF - for now we'll use a simpler approach
                                # In practice, we might need to recreate the page without the image
                                print(f"  Image {img_index} marked for removal")
                            except Exception as e:
                                print(f"  Warning: Could not remove image {img_index}: {e}")
            
            # Save the modified document
            doc.save(str(output_path))
            doc.close()
            
            print("Note: Image removal is complex and may not be fully supported.")
            print("Consider removing entire pages with large images instead.")
            return True
            
        except Exception as e:
            print(f"Error removing images: {e}")
            return False
    
    def split_pages(self, input_path: Path, output_dir: Path) -> List[Path]:
        """Split PDF into individual pages."""
        try:
            reader = pypdf.PdfReader(input_path)
            output_files = []
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for page_num, page in enumerate(reader.pages):
                writer = pypdf.PdfWriter()
                writer.add_page(page)
                
                # Copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)
                
                output_file = output_dir / f"{input_path.stem}_page_{page_num + 1:03d}.pdf"
                
                with open(output_file, 'wb') as f:
                    writer.write(f)
                
                output_files.append(output_file)
                print(f"Created: {output_file.name}")
            
            return output_files
            
        except Exception as e:
            print(f"Error splitting pages: {e}")
            return []
    
    def interactive_page_selection(self, analysis: Dict) -> List[int]:
        """Interactive command-line page selection."""
        print(f"\n=== Interactive Page Selection ===")
        print(f"PDF has {analysis['total_pages']} pages")
        print(f"Current size: {analysis['file_size_mb']:.2f} MB")
        
        self.print_pdf_analysis(analysis)
        
        print(f"\nOptions:")
        print(f"1. Enter page numbers to REMOVE (e.g., 1,3,5-7)")
        print(f"2. Enter page numbers to KEEP (e.g., 1-4,8,10-12)")
        print(f"3. Remove pages with most images")
        print(f"4. Show detailed page analysis")
        print(f"5. Exit without changes")
        
        while True:
            choice = input(f"\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                pages_input = input(f"Enter pages to REMOVE (e.g., 1,3,5-7): ").strip()
                try:
                    pages = self.parse_page_range(pages_input, analysis['total_pages'])
                    if pages:
                        print(f"Will remove pages: {sorted(pages)}")
                        confirm = input(f"Confirm? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes']:
                            return pages
                except ValueError as e:
                    print(f"Error: {e}")
            
            elif choice == '2':
                pages_input = input(f"Enter pages to KEEP (e.g., 1-4,8,10): ").strip()
                try:
                    keep_pages = self.parse_page_range(pages_input, analysis['total_pages'])
                    if keep_pages:
                        all_pages = set(range(1, analysis['total_pages'] + 1))
                        remove_pages = list(all_pages - set(keep_pages))
                        print(f"Will keep pages: {sorted(keep_pages)}")
                        print(f"Will remove pages: {sorted(remove_pages)}")
                        confirm = input(f"Confirm? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes']:
                            return remove_pages
                except ValueError as e:
                    print(f"Error: {e}")
            
            elif choice == '3':
                # Suggest pages with most images
                image_heavy_pages = [p for p in analysis['pages'] 
                                   if len(p['images']) >= 3 or p['estimated_size_mb'] > 2]
                if image_heavy_pages:
                    page_nums = [p['page_num'] for p in image_heavy_pages]
                    print(f"Pages with heavy image content: {page_nums}")
                    for page in image_heavy_pages:
                        print(f"  Page {page['page_num']}: {len(page['images'])} images, "
                              f"~{page['estimated_size_mb']:.1f} MB")
                    
                    confirm = input(f"Remove these pages? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return page_nums
                else:
                    print("No pages found with heavy image content.")
            
            elif choice == '4':
                self.print_detailed_analysis(analysis)
            
            elif choice == '5':
                print("Exiting without changes.")
                return []
            
            else:
                print("Invalid choice. Please enter 1-5.")
        
        return []
    
    def print_detailed_analysis(self, analysis: Dict):
        """Print detailed analysis including image information."""
        print(f"\n=== Detailed Page Analysis ===")
        
        for page in analysis['pages']:
            print(f"\nPage {page['page_num']}:")
            print(f"  Dimensions: {int(page['size'][0])} x {int(page['size'][1])}")
            print(f"  Text characters: {page['text_length']}")
            print(f"  Images: {len(page['images'])}")
            print(f"  Estimated size: {page['estimated_size_mb']:.2f} MB")
            
            if page['images']:
                print(f"  Image details:")
                for i, img in enumerate(page['images']):
                    print(f"    {i+1}. {img['width']}x{img['height']} "
                          f"({img['colorspace']}, ~{img['estimated_size_kb']:.0f}KB)")
    
    def parse_page_range(self, page_input: str, total_pages: int) -> List[int]:
        """Parse page range input like '1,3,5-7,10' into list of page numbers."""
        pages = []
        
        if not page_input.strip():
            return pages
        
        for part in page_input.split(','):
            part = part.strip()
            
            if '-' in part:
                # Range like "5-7"
                try:
                    start, end = part.split('-')
                    start, end = int(start.strip()), int(end.strip())
                    if start > end:
                        start, end = end, start
                    pages.extend(range(start, end + 1))
                except ValueError:
                    raise ValueError(f"Invalid range: {part}")
            else:
                # Single page
                try:
                    page_num = int(part)
                    pages.append(page_num)
                except ValueError:
                    raise ValueError(f"Invalid page number: {part}")
        
        # Validate page numbers
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            raise ValueError(f"Invalid page numbers: {invalid_pages}. "
                           f"PDF has pages 1-{total_pages}")
        
        return list(set(pages))  # Remove duplicates


def main():
    parser = argparse.ArgumentParser(
        description="Interactive PDF Editor - Remove pages, images, and optimize PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf_editor document.pdf --pages                    # Interactive page selection
  pdf_editor document.pdf --analyze                  # Analyze PDF structure
  pdf_editor document.pdf --remove-pages 3,5,7-9    # Remove specific pages
  pdf_editor document.pdf --keep-pages 1-5,10       # Keep only specific pages
  pdf_editor document.pdf --split-pages              # Split into individual pages
  pdf_editor document.pdf --images                   # Interactive image removal (experimental)
        """
    )
    
    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('--output', '-o', help='Output PDF file')
    parser.add_argument('--pages', action='store_true',
                       help='Interactive page selection and removal')
    parser.add_argument('--images', action='store_true',
                       help='Interactive image removal (experimental)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze PDF structure without modifications')
    parser.add_argument('--remove-pages', help='Pages to remove (e.g., 1,3,5-7)')
    parser.add_argument('--keep-pages', help='Pages to keep (e.g., 1-5,10)')
    parser.add_argument('--split-pages', action='store_true',
                       help='Split PDF into individual page files')
    
    args = parser.parse_args()
    
    # Initialize editor
    editor = PDFEditor()
    
    input_path = Path(args.input).resolve()
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        return 1
    
    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: Input file must be a PDF.")
        return 1
    
    # Analyze PDF
    print(f"Analyzing PDF: {input_path.name}")
    analysis = editor.analyze_pdf(input_path)
    
    if not analysis:
        print("Error: Could not analyze PDF.")
        return 1
    
    # Handle different operations
    if args.analyze:
        editor.print_pdf_analysis(analysis)
        editor.print_detailed_analysis(analysis)
        return 0
    
    elif args.split_pages:
        output_dir = input_path.parent / f"{input_path.stem}_pages"
        print(f"Splitting PDF into individual pages...")
        created_files = editor.split_pages(input_path, output_dir)
        
        if created_files:
            print(f"\n✓ Created {len(created_files)} page files in: {output_dir}")
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in created_files) / (1024 * 1024)
            print(f"Total size of split files: {total_size:.2f} MB")
        else:
            print("✗ Failed to split PDF")
            return 1
        
        return 0
    
    # Set output path
    if not args.output:
        output_path = input_path.parent / f"{input_path.stem}_edited.pdf"
    else:
        output_path = Path(args.output).resolve()
    
    # Interactive page selection
    if args.pages:
        pages_to_remove = editor.interactive_page_selection(analysis)
        
        if pages_to_remove:
            success = editor.remove_pages(input_path, output_path, pages_to_remove)
            
            if success:
                new_size = output_path.stat().st_size / (1024 * 1024)
                reduction = (1 - new_size / analysis['file_size_mb']) * 100
                print(f"\n✓ Created edited PDF: {output_path.name}")
                print(f"Original size: {analysis['file_size_mb']:.2f} MB")
                print(f"New size: {new_size:.2f} MB (reduced by {reduction:.1f}%)")
            else:
                print("✗ Failed to create edited PDF")
                return 1
        else:
            print("No changes made.")
        
        return 0
    
    # Remove specific pages
    elif args.remove_pages:
        try:
            pages_to_remove = editor.parse_page_range(args.remove_pages, analysis['total_pages'])
            success = editor.remove_pages(input_path, output_path, pages_to_remove)
            
            if success:
                new_size = output_path.stat().st_size / (1024 * 1024)
                reduction = (1 - new_size / analysis['file_size_mb']) * 100
                print(f"\n✓ Created edited PDF: {output_path.name}")
                print(f"Original size: {analysis['file_size_mb']:.2f} MB")
                print(f"New size: {new_size:.2f} MB (reduced by {reduction:.1f}%)")
            else:
                print("✗ Failed to create edited PDF")
                return 1
                
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    # Keep specific pages
    elif args.keep_pages:
        try:
            pages_to_keep = editor.parse_page_range(args.keep_pages, analysis['total_pages'])
            success = editor.keep_pages(input_path, output_path, pages_to_keep)
            
            if success:
                new_size = output_path.stat().st_size / (1024 * 1024)
                reduction = (1 - new_size / analysis['file_size_mb']) * 100
                print(f"\n✓ Created edited PDF: {output_path.name}")
                print(f"Original size: {analysis['file_size_mb']:.2f} MB")
                print(f"New size: {new_size:.2f} MB (reduced by {reduction:.1f}%)")
            else:
                print("✗ Failed to create edited PDF")
                return 1
                
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    # Interactive image removal (experimental)
    elif args.images:
        print("Image removal is experimental and may not work perfectly.")
        print("Consider removing entire pages with large images instead.")
        
        editor.print_detailed_analysis(analysis)
        
        # For now, just show the analysis
        print("\nImage removal feature is under development.")
        print("Use --pages to remove pages containing large images.")
        
        return 0
    
    else:
        # Default: show analysis and suggest actions
        editor.print_pdf_analysis(analysis)
        
        print(f"\nSuggested actions:")
        
        # Find pages that could be removed to save space
        large_pages = [p for p in analysis['pages'] if p['estimated_size_mb'] > 2]
        image_heavy_pages = [p for p in analysis['pages'] if len(p['images']) >= 4]
        
        if large_pages:
            page_nums = [p['page_num'] for p in large_pages]
            print(f"  Consider removing large pages: {page_nums}")
        
        if image_heavy_pages:
            page_nums = [p['page_num'] for p in image_heavy_pages]
            print(f"  Consider removing image-heavy pages: {page_nums}")
        
        print(f"\nUse --pages for interactive selection or --help for more options.")
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
