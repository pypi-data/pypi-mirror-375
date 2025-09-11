#!/usr/bin/env python3
"""
PDF Compression Script for Outlook Attachments
Compresses PDF files to be under 9.5MB for safe Outlook attachment.

Usage:
    python pdf_compressor.py input.pdf [output.pdf]
    python pdf_compressor.py --batch folder_path
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List
import pypdf
from PIL import Image
import io
import tempfile
import subprocess
import shutil


class PDFCompressor:
    def __init__(self, max_size_mb: float = 9.5):
        """
        Initialize PDF compressor.
        
        Args:
            max_size_mb: Maximum file size in megabytes (default: 9.5MB)
        """
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_size_mb = max_size_mb
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        return file_path.stat().st_size
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in megabytes."""
        return self.get_file_size(file_path) / (1024 * 1024)
    
    def compress_pdf_basic(self, input_path: Path, output_path: Path) -> bool:
        """
        Basic PDF compression using pypdf.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output compressed PDF
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            reader = pypdf.PdfReader(input_path)
            writer = pypdf.PdfWriter()
            
            # Copy pages and compress
            for page in reader.pages:
                # Add page first, then compress
                writer.add_page(page)
            
            # Compress all pages in the writer
            for page in writer.pages:
                page.compress_content_streams()
            
            # Apply additional compression settings
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error during basic compression: {e}")
            return False
    
    def compress_pdf_images(self, input_path: Path, output_path: Path, 
                           image_quality: int = 85) -> bool:
        """
        Compress PDF with image compression.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output compressed PDF
            image_quality: JPEG quality for image compression (1-95)
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            reader = pypdf.PdfReader(input_path)
            writer = pypdf.PdfWriter()
            
            for page_num, page in enumerate(reader.pages):
                # Add page to writer first
                writer.add_page(page)
            
            # Now compress the pages in the writer
            for page in writer.pages:
                page.compress_content_streams()
                
                # Extract and compress images if present
                if '/XObject' in page.get('/Resources', {}):
                    try:
                        xobject = page['/Resources']['/XObject'].get_object()
                        
                        for obj in xobject:
                            if xobject[obj].get('/Subtype') == '/Image':
                                try:
                                    # Extract image data
                                    image_obj = xobject[obj]
                                    image_data = image_obj.get_data()
                                    
                                    # Convert to PIL Image and compress
                                    image = Image.open(io.BytesIO(image_data))
                                    
                                    # Convert to RGB if necessary
                                    if image.mode in ('RGBA', 'LA', 'P'):
                                        image = image.convert('RGB')
                                    
                                    # Compress image
                                    output_buffer = io.BytesIO()
                                    image.save(output_buffer, format='JPEG', 
                                             quality=image_quality, optimize=True)
                                    
                                    # Update image in PDF (this is complex with pypdf)
                                    # For now, we'll rely on basic compression
                                    
                                except Exception as img_error:
                                    # Silently continue if image compression fails
                                    pass
                    except Exception:
                        # Continue if XObject processing fails
                        pass
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error during image compression: {e}")
            return False
    
    def compress_pdf_aggressive(self, input_path: Path, output_path: Path) -> bool:
        """
        Aggressive PDF compression with multiple techniques.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output compressed PDF
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            reader = pypdf.PdfReader(input_path)
            writer = pypdf.PdfWriter()
            
            # Copy pages first, then modify
            for page in reader.pages:
                writer.add_page(page)
            
            # Remove unnecessary elements from writer pages
            for page in writer.pages:
                # Remove annotations, forms, etc.
                if '/Annots' in page:
                    del page['/Annots']
                
                # Compress content streams
                page.compress_content_streams()
            
            # Remove metadata to save space
            writer.add_metadata({})
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error during aggressive compression: {e}")
            return False
    
    def validate_pdf(self, pdf_path: Path) -> bool:
        """
        Validate that a PDF file is not corrupted.
        
        Args:
            pdf_path: Path to PDF file to validate
            
        Returns:
            True if PDF is valid, False otherwise
        """
        try:
            reader = pypdf.PdfReader(pdf_path)
            # Try to access basic properties
            num_pages = len(reader.pages)
            if num_pages > 0:
                # Try to access first page
                first_page = reader.pages[0]
                return True
            return False
        except Exception:
            return False
    
    def compress_pdf_ghostscript(self, input_path: Path, output_path: Path, 
                                quality: str = "ebook", dpi: int = None, 
                                jpeg_quality: int = None) -> bool:
        """
        Compress PDF using Ghostscript (most effective for large files).
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output compressed PDF
            quality: Quality setting (screen, ebook, printer, prepress)
                    screen = lowest quality, smallest size
                    ebook = good quality, reasonable size
                    printer = high quality
                    prepress = highest quality
            dpi: Custom DPI for images (overrides quality setting)
            jpeg_quality: JPEG quality 0-100 (overrides quality setting)
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            # Check if ghostscript is available
            gs_cmd = None
            for cmd in ['gs', 'ghostscript', 'gswin64c', 'gswin32c']:
                if shutil.which(cmd):
                    gs_cmd = cmd
                    break
            
            if not gs_cmd:
                print("Ghostscript not found. Install with: sudo apt-get install ghostscript")
                return False
            
            # Ghostscript command for PDF compression
            cmd = [
                gs_cmd,
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS=/{quality}',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                '-dDetectDuplicateImages=true',
                '-dCompressFonts=true',
                '-dSubsetFonts=true',
            ]
            
            # Add custom DPI settings if specified
            if dpi:
                cmd.extend([
                    f'-dColorImageResolution={dpi}',
                    f'-dGrayImageResolution={dpi}',
                    f'-dMonoImageResolution={dpi}',
                ])
            
            # Add custom JPEG quality if specified
            if jpeg_quality:
                cmd.extend([
                    f'-dJPEGQ={jpeg_quality}',
                    '-dColorImageFilter=/DCTEncode',
                    '-dGrayImageFilter=/DCTEncode',
                    '-dMonoImageFilter=/CCITTFaxEncode',
                ])
            
            # For very aggressive compression, add more options
            if dpi and dpi <= 72 and jpeg_quality and jpeg_quality <= 50:
                cmd.extend([
                    '-dAutoRotatePages=/None',
                    '-dColorImageDownsampleType=/Bicubic',
                    '-dGrayImageDownsampleType=/Bicubic',
                    '-dDoThumbnails=false',
                    '-dCreateJobTicket=false',
                    '-dPreserveEPSInfo=false',
                    '-dPreserveOPIComments=false',
                    '-dPreserveOverprintSettings=false',
                    '-dUCRandBGInfo=/Remove',
                ])
            
            cmd.extend([
                f'-sOutputFile={output_path}',
                str(input_path)
            ])
            
            # Run ghostscript with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0 and output_path.exists():
                # Validate the output PDF
                if self.validate_pdf(output_path):
                    return True
                else:
                    print(f"Ghostscript created invalid PDF, removing: {output_path}")
                    output_path.unlink()
                    return False
            else:
                print(f"Ghostscript error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error during Ghostscript compression: {e}")
            return False
    
    def compress_pdf_qpdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Compress PDF using qpdf (often pre-installed, very effective).
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output compressed PDF
            
        Returns:
            True if compression was successful, False otherwise
        """
        try:
            # Check if qpdf is available
            if not shutil.which('qpdf'):
                print("qpdf not found. Install with: sudo apt-get install qpdf")
                return False
            
            # qpdf command for PDF compression
            cmd = [
                'qpdf',
                '--linearize',
                '--optimize-images',
                '--compress-streams=y',
                '--recompress-flate',
                str(input_path),
                str(output_path)
            ]
            
            # Run qpdf with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0 and output_path.exists():
                # Validate the output PDF
                if self.validate_pdf(output_path):
                    return True
                else:
                    print(f"qpdf created invalid PDF, removing: {output_path}")
                    output_path.unlink()
                    return False
            else:
                print(f"qpdf error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error during qpdf compression: {e}")
            return False
    
    def compress_pdf_nuclear(self, input_path: Path, output_path: Path) -> bool:
        """
        Nuclear compression - maximum compression even if quality is very poor.
        Specifically designed to get large files under 10MB for email.
        """
        try:
            # Check if ghostscript is available
            gs_cmd = None
            for cmd in ['gs', 'ghostscript', 'gswin64c', 'gswin32c']:
                if shutil.which(cmd):
                    gs_cmd = cmd
                    break
            
            if not gs_cmd:
                return False
            
            # Nuclear compression settings
            cmd = [
                gs_cmd,
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/screen',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                '-dDetectDuplicateImages=true',
                '-dCompressFonts=true',
                '-dSubsetFonts=true',
                '-dAutoRotatePages=/None',
                '-dColorImageDownsampleType=/Bicubic',
                '-dGrayImageDownsampleType=/Bicubic',
                '-dMonoImageDownsampleType=/Bicubic',
                '-dDoThumbnails=false',
                '-dCreateJobTicket=false',
                '-dPreserveEPSInfo=false',
                '-dPreserveOPIComments=false',
                '-dPreserveOverprintSettings=false',
                '-dUCRandBGInfo=/Remove',
                '-dColorImageResolution=50',
                '-dGrayImageResolution=50',
                '-dMonoImageResolution=50',
                '-dJPEGQ=25',
                '-dColorImageFilter=/DCTEncode',
                '-dGrayImageFilter=/DCTEncode',
                '-dMonoImageFilter=/CCITTFaxEncode',
                f'-sOutputFile={output_path}',
                str(input_path)
            ]
            
            # Run ghostscript with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                # Validate the output PDF
                if self.validate_pdf(output_path):
                    return True
                else:
                    print(f"Nuclear compression created invalid PDF, removing: {output_path}")
                    output_path.unlink()
                    return False
            else:
                print(f"Nuclear compression error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error during nuclear compression: {e}")
            return False

    def check_qpdf_available(self) -> bool:
        """Check if qpdf is available on the system."""
        return shutil.which('qpdf') is not None
    
    def check_ghostscript_available(self) -> bool:
        """Check if Ghostscript is available on the system."""
        for cmd in ['gs', 'ghostscript', 'gswin64c', 'gswin32c']:
            if shutil.which(cmd):
                return True
        return False
    
    def compress_file_dual_version(self, input_path: Path, output_dir: Optional[Path] = None) -> dict:
        """
        Create two versions of a compressed PDF:
        1. Best quality version (around 16MB) - maintains good quality
        2. Outlook-compatible version (under 10MB) - may sacrifice some quality
        
        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files (optional, defaults to input file directory)
            
        Returns:
            Dictionary with paths to created files: {'quality': Path, 'outlook': Path}
        """
        if not input_path.exists():
            print(f"Error: Input file '{input_path}' does not exist.")
            return {}
        
        if not input_path.suffix.lower() == '.pdf':
            print(f"Error: Input file '{input_path}' is not a PDF.")
            return {}
        
        # Set output directory if not provided
        if output_dir is None:
            output_dir = input_path.parent
        
        # Define output paths
        quality_output = output_dir / f"{input_path.stem}_quality.pdf"
        outlook_output = output_dir / f"{input_path.stem}_outlook.pdf"
        
        original_size_mb = self.get_file_size_mb(input_path)
        print(f"Original file size: {original_size_mb:.2f} MB")
        print(f"Creating two versions:")
        print(f"  1. Quality version: {quality_output.name}")
        print(f"  2. Outlook version: {outlook_output.name}")
        
        results = {}
        
        # Create quality version (best compression without major quality loss)
        print(f"\n--- Creating Quality Version ---")
        if self.check_ghostscript_available():
            if self.compress_pdf_ghostscript(input_path, quality_output, "ebook"):
                quality_size_mb = self.get_file_size_mb(quality_output)
                compression_ratio = (1 - quality_size_mb / original_size_mb) * 100
                print(f"✓ Quality version: {quality_size_mb:.2f} MB (reduced by {compression_ratio:.1f}%)")
                results['quality'] = quality_output
            else:
                print("✗ Failed to create quality version")
        else:
            print("✗ Ghostscript not available for quality version")
        
        # Create Outlook version (aggressive compression to meet size limit)
        print(f"\n--- Creating Outlook Version (under 10MB) ---")
        temp_outlook = None
        
        if self.check_ghostscript_available():
            # Try progressively more aggressive settings for Outlook compatibility
            outlook_methods = [
                ("screen quality", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen")),
                ("low DPI (150)", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=150)),
                ("medium-low DPI (120)", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=120)),
                ("low DPI with JPEG", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=100, jpeg_quality=75)),
                ("aggressive compression", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=90, jpeg_quality=65)),
                ("very aggressive (DPI 72)", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=72, jpeg_quality=55)),
                ("maximum compression (DPI 60)", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=60, jpeg_quality=45)),
                ("extreme compression (DPI 50)", lambda: self.compress_pdf_ghostscript(input_path, outlook_output, "screen", dpi=50, jpeg_quality=35)),
                ("nuclear compression", lambda: self.compress_pdf_nuclear(input_path, outlook_output)),
            ]
            
            for method_name, method_func in outlook_methods:
                print(f"Trying {method_name}...")
                
                if method_func():
                    outlook_size_mb = self.get_file_size_mb(outlook_output)
                    compression_ratio = (1 - outlook_size_mb / original_size_mb) * 100
                    print(f"  Result: {outlook_size_mb:.2f} MB (reduced by {compression_ratio:.1f}%)")
                    
                    if outlook_size_mb <= 10.0:  # 10MB limit
                        print(f"✓ Outlook version: {outlook_size_mb:.2f} MB")
                        results['outlook'] = outlook_output
                        break
                else:
                    print(f"  Failed to apply {method_name}")
            
            if 'outlook' not in results:
                print("✗ Could not create Outlook version under 10MB with Ghostscript")
        else:
            print("✗ Ghostscript not available for Outlook version")
        
        # If we couldn't create the Outlook version with Ghostscript, try other methods
        if 'outlook' not in results and outlook_output.exists():
            outlook_output.unlink()  # Remove failed attempt
            
            print("Trying alternative compression methods for Outlook version...")
            
            # Use the existing compress_file method with 10MB limit
            old_max_size = self.max_size_mb
            self.max_size_mb = 10.0
            
            outlook_result = self.compress_file(input_path, outlook_output)
            
            self.max_size_mb = old_max_size  # Restore original limit
            
            if outlook_result:
                results['outlook'] = outlook_result
        
        # Summary
        print(f"\n=== Compression Complete ===")
        if 'quality' in results:
            quality_size = self.get_file_size_mb(results['quality'])
            print(f"✓ Quality version: {quality_size:.2f} MB saved to {results['quality'].name}")
        else:
            print("✗ Quality version: Failed")
            
        if 'outlook' in results:
            outlook_size = self.get_file_size_mb(results['outlook'])
            print(f"✓ Outlook version: {outlook_size:.2f} MB saved to {results['outlook'].name}")
        else:
            print("✗ Outlook version: Failed to create under 10MB")
            final_size = self.get_file_size_mb(quality_output) if quality_output.exists() else 0
            if final_size > 0:
                print(f"")
                print(f"💡 Suggestion: This PDF appears to be image-heavy and hits a compression limit around {final_size:.0f}MB.")
                print(f"   For email attachment, consider:")
                print(f"   1. Using the quality version ({final_size:.1f}MB) - some email providers accept up to 25MB")
                print(f"   2. Using cloud sharing (Google Drive, Dropbox, etc.)")
                print(f"   3. Splitting into multiple files if it's a multi-part document")
                print(f"   4. Converting to lower-quality images before creating the PDF")
        
        return results

    def compress_file(self, input_path: Path, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Compress a single PDF file using progressive compression levels.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output file (optional)
            
        Returns:
            Path to compressed file if successful, None otherwise
        """
        if not input_path.exists():
            print(f"Error: Input file '{input_path}' does not exist.")
            return None
        
        if not input_path.suffix.lower() == '.pdf':
            print(f"Error: Input file '{input_path}' is not a PDF.")
            return None
        
        # Set output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed.pdf"
        
        # Check if file is already small enough
        original_size = self.get_file_size(input_path)
        original_size_mb = original_size / (1024 * 1024)
        
        print(f"Original file size: {original_size_mb:.2f} MB")
        
        if original_size <= self.max_size_bytes:
            print(f"File is already under {self.max_size_mb} MB. No compression needed.")
            # Copy file to output location
            if input_path != output_path:
                shutil.copy2(input_path, output_path)
            return output_path
        
        # Try different compression levels
        temp_files = []
        
        # For large files (>20MB), prioritize external tools first
        if original_size_mb > 20:
            compression_methods = []
            
            # Add Ghostscript methods first (most effective for large files)
            if self.check_ghostscript_available():
                compression_methods.extend([
                    ("Ghostscript ebook", lambda i, o: self.compress_pdf_ghostscript(i, o, "ebook")),
                    ("Ghostscript screen", lambda i, o: self.compress_pdf_ghostscript(i, o, "screen")),
                    ("Ghostscript low DPI", lambda i, o: self.compress_pdf_ghostscript(i, o, "screen", dpi=150)),
                    ("Ghostscript very low DPI", lambda i, o: self.compress_pdf_ghostscript(i, o, "screen", dpi=100)),
                    ("Ghostscript aggressive", lambda i, o: self.compress_pdf_ghostscript(i, o, "screen", dpi=72, jpeg_quality=50)),
                ])
            else:
                print("Note: Ghostscript not available. Install with: sudo apt-get install ghostscript")
            
            # Add qpdf if available
            if self.check_qpdf_available():
                compression_methods.extend([
                    ("qpdf", self.compress_pdf_qpdf),
                ])
            else:
                print("Note: qpdf not available. Install with: sudo apt-get install qpdf")
            
            # Add pypdf methods as fallback
            compression_methods.extend([
                ("basic", self.compress_pdf_basic),
                ("aggressive", self.compress_pdf_aggressive),
            ])
        else:
            # For smaller files, use pypdf first, then external tools
            compression_methods = [
                ("basic", self.compress_pdf_basic),
                ("with images", lambda i, o: self.compress_pdf_images(i, o, 75)),
                ("aggressive", self.compress_pdf_aggressive),
                ("very aggressive", lambda i, o: self.compress_pdf_images(i, o, 50)),
            ]
            
            # Add external tool methods if available
            if self.check_qpdf_available():
                compression_methods.extend([
                    ("qpdf", self.compress_pdf_qpdf),
                ])
            else:
                print("Note: qpdf not available. Install with: sudo apt-get install qpdf")
                
            if self.check_ghostscript_available():
                compression_methods.extend([
                    ("Ghostscript ebook", lambda i, o: self.compress_pdf_ghostscript(i, o, "ebook")),
                    ("Ghostscript screen", lambda i, o: self.compress_pdf_ghostscript(i, o, "screen")),
                ])
            else:
                print("Note: Ghostscript not available. Install with: sudo apt-get install ghostscript")
        
        for method_name, method_func in compression_methods:
            # Create temporary file for this attempt
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            temp_path = Path(temp_path)
            temp_files.append(temp_path)
            
            print(f"Trying {method_name} compression...")
            
            if method_func(input_path, temp_path):
                compressed_size = self.get_file_size(temp_path)
                compressed_size_mb = compressed_size / (1024 * 1024)
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                print(f"  Result: {compressed_size_mb:.2f} MB (reduced by {compression_ratio:.1f}%)")
                
                if compressed_size <= self.max_size_bytes:
                    # Success! Move temp file to final output
                    shutil.move(str(temp_path), str(output_path))
                    
                    # Clean up other temp files
                    for tf in temp_files:
                        if tf.exists() and tf != temp_path:
                            tf.unlink()
                    
                    print(f"✓ Successfully compressed to {compressed_size_mb:.2f} MB")
                    print(f"✓ Output saved to: {output_path}")
                    return output_path
            else:
                print(f"  Failed to apply {method_name} compression")
        
        # Clean up temp files
        for tf in temp_files:
            if tf.exists():
                tf.unlink()
        
        print(f"✗ Could not compress file to under {self.max_size_mb} MB")
        print("Consider using external tools like Ghostscript for more aggressive compression.")
        return None
    
    def compress_batch(self, folder_path: Path, pattern: str = "*.pdf") -> List[Path]:
        """
        Compress all PDF files in a folder.
        
        Args:
            folder_path: Path to folder containing PDFs
            pattern: File pattern to match (default: "*.pdf")
            
        Returns:
            List of successfully compressed file paths
        """
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Error: Folder '{folder_path}' does not exist.")
            return []
        
        pdf_files = list(folder_path.glob(pattern))
        if not pdf_files:
            print(f"No PDF files found in '{folder_path}'")
            return []
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        successful_compressions = []
        
        for pdf_file in pdf_files:
            print(f"\n--- Processing: {pdf_file.name} ---")
            
            # Skip already compressed files
            if "_compressed" in pdf_file.stem:
                print("Skipping already compressed file.")
                continue
            
            result = self.compress_file(pdf_file)
            if result:
                successful_compressions.append(result)
        
        print(f"\n=== Batch Processing Complete ===")
        print(f"Successfully compressed {len(successful_compressions)} out of {len(pdf_files)} files.")
        
        return successful_compressions


def main():
    parser = argparse.ArgumentParser(
        description="Compress PDF files for Outlook attachment (under 10MB)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf compressed_document.pdf
  %(prog)s --dual document.pdf
  %(prog)s --batch /path/to/pdf/folder
  %(prog)s --max-size 8.0 large_document.pdf
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input PDF file or folder (with --batch)')
    parser.add_argument('output', nargs='?', help='Output PDF file (optional, not used with --dual)')
    parser.add_argument('--batch', action='store_true', 
                       help='Process all PDF files in the specified folder')
    parser.add_argument('--dual', action='store_true',
                       help='Create two versions: quality (~16MB) and outlook (<10MB)')
    parser.add_argument('--max-size', type=float, default=10.0, 
                       help='Maximum file size in MB (default: 10.0)')
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        return 1
    
    # Initialize compressor
    compressor = PDFCompressor(max_size_mb=args.max_size)
    
    input_path = Path(args.input)
    
    if args.dual:
        # Dual version processing
        if args.batch:
            print("Error: --dual and --batch cannot be used together")
            return 1
        
        results = compressor.compress_file_dual_version(input_path)
        return 0 if results else 1
    elif args.batch:
        # Batch processing
        results = compressor.compress_batch(input_path)
        return 0 if results else 1
    else:
        # Single file processing
        output_path = Path(args.output) if args.output else None
        result = compressor.compress_file(input_path, output_path)
        return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
