# Shift - Universal Document and PDF Toolkit

A comprehensive command-line toolkit for document conversion, PDF compression, page management, OCR text extraction, and more.

## 🚀 Quick Start

**Install the package:**
```bash
git clone https://github.com/adamn1225/shift.git
cd shift
pip install -e .
```

**Use anywhere:**
```bash
shift-convert document.docx --to pdf            # Recommended (avoids bash builtin)
shift-compress large_file.pdf                   # Compress PDFs for email
shift-pages document.pdf                        # Interactive page removal  
shift-edit document.pdf --pages                 # Advanced PDF editing
shift-ocr scanned.pdf --extract-text            # Extract text from scanned PDFs
```

> **Important:** Use `shift-convert` instead of `shift` to avoid conflicts with the bash builtin command. Alternatively, use the full path: `/home/bender/.local/bin/shift`

## 📦 What's Included

| Command | Description | Main Use Case |
|---------|-------------|---------------|
| `shift` | Universal document converter | Convert between PDF, Word, HTML, Markdown, Text |
| `shift-compress` | PDF compression tool | Make PDFs small enough for email attachments |
| `shift-pages` | PDF page manager | Remove pages interactively to reduce file size |
| `shift-edit` | Advanced PDF editor | Complex PDF editing with GUI interface |
| `shift-ocr` | OCR text extraction | Extract text from scanned PDFs and images |

## 🔧 Features

- **Global commands:** Work from any directory after installation
- **Auto-detection:** File formats detected from extensions  
- **Batch processing:** Handle entire folders with single commands
- **Quality options:** Multiple compression and conversion levels
- **External tools:** Integrates with Pandoc, LibreOffice, Ghostscript when available
- **Interactive modes:** GUI and command-line interfaces
- **Comprehensive help:** Each tool provides detailed `--help`

---

## 📄 Document Conversion (`shift`)

Convert between various document formats with intelligent format detection.

### Supported Formats
- **PDF** ↔ Text, HTML, Markdown
- **Word (DOCX)** ↔ PDF, HTML, Text, Markdown  
- **HTML** ↔ PDF, Text, Markdown
- **Markdown** ↔ HTML, PDF, Word
- **Text** ↔ PDF, HTML, Markdown

### Examples
```bash
# Basic conversion
shift document.docx --to pdf
shift report.md --to html --css professional.css
shift presentation.html --to pdf

# Batch conversion
shift documents/ --batch --from docx --to pdf --output converted/

# Advanced options
shift file.pdf --to text --output extracted.txt
shift *.md --to html --css bootstrap.min.css
```

---

## 🗜️ PDF Compression (`shift-compress`)

Compress PDFs for email attachments (under 9.5MB) with multiple quality options.

### Basic Compression
```bash
shift-compress document.pdf                 # Compress to under 9.5MB
shift-compress large_file.pdf --output small.pdf
shift-compress --batch folder/              # Process whole folders  
```

### Advanced Compression Options
```bash
# Quality levels (using Ghostscript if available)
shift-compress file.pdf --quality screen    # Smallest size, lowest quality
shift-compress file.pdf --quality ebook     # Good balance (default)
shift-compress file.pdf --quality printer   # High quality

# Custom settings
shift-compress file.pdf --dpi 72 --jpeg-quality 50  # Maximum compression
shift-compress file.pdf --dual              # Create both quality & small versions
```

### Two-Step Approach for Large Files
For very large PDFs (>30MB), combine page removal with compression:
```bash
shift-pages huge_file.pdf                   # Remove unnecessary pages first  
shift-compress huge_file_edited.pdf         # Then compress the result
```

---

## 📖 PDF Page Management (`shift-pages`)

Analyze and remove pages from PDFs to reduce file size.

### Interactive Mode
```bash
shift-pages document.pdf                    # Interactive page selection
```

### Direct Commands  
```bash
shift-pages document.pdf --analyze          # Just show page analysis
shift-pages document.pdf --remove 1,3,5-7   # Remove specific pages
shift-pages document.pdf --split-pages      # Split into individual files
```

### What It Shows
- File size and page count
- Pages with heavy image content  
- Size estimates for each page
- Suggestions for pages to remove

---

## ✏️ Advanced PDF Editor (`shift-edit`)

Comprehensive PDF editing with both command-line and GUI interfaces.

### Interactive Editing
```bash
shift-edit document.pdf --pages             # Interactive page selection
shift-edit document.pdf --images            # Image removal (experimental)
```

### Direct Commands
```bash
shift-edit document.pdf --remove-pages 3,5,7-9
shift-edit document.pdf --keep-pages 1-5,10  
shift-edit document.pdf --split-pages        # Split into individual pages
```

### Analysis Mode
```bash
shift-edit document.pdf --analyze           # Detailed structure analysis
```

---

## 🔍 OCR Text Extraction (`shift-ocr`)

Extract text from scanned PDFs and images using Tesseract OCR.

### Basic OCR
```bash
shift-ocr scanned_document.pdf              # Extract text to console
shift-ocr document.pdf --output text.txt    # Save to file
shift-ocr image.png --lang eng+spa          # Multiple languages
```

### Batch Processing
```bash
shift-ocr folder/ --batch --output results/ # Process entire folders
shift-ocr *.pdf --confidence 70             # Set confidence threshold
```

### Preprocessing Options
```bash
shift-ocr blurry.pdf --denoise --deskew     # Clean up image quality
shift-ocr document.pdf --preprocess aggressive
```

---

## 🛠️ Installation and Dependencies

### Python Package Installation
```bash
git clone https://github.com/adamn1225/shift.git
cd shift  
pip install -e .                            # Editable/development install
# OR
pip install .                               # Standard install
```

### System Dependencies (Optional but Recommended)

For enhanced functionality, install these system tools:

**Ubuntu/Debian:**
```bash
sudo apt-get install ghostscript pandoc wkhtmltopdf tesseract-ocr qpdf
sudo apt-get install libreoffice-writer    # For advanced document conversion
```

**macOS:**
```bash
brew install ghostscript pandoc wkhtmltopdf tesseract qpdf
```

**Windows:**
- Install [Ghostscript](https://www.ghostscript.com/download/gsdnld.html)
- Install [Pandoc](https://pandoc.org/installing.html)  
- Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

### What Each Dependency Enables
- **Ghostscript:** Best PDF compression (essential for large files)
- **Pandoc:** Universal document conversion between many formats
- **wkhtmltopdf:** High-quality HTML to PDF conversion  
- **Tesseract:** OCR text extraction from scanned documents
- **qpdf:** Additional PDF optimization options
- **LibreOffice:** Advanced document format support

---

## 📋 Usage Examples

### Common Workflows

**Make a large PDF email-friendly:**
```bash
shift-compress presentation.pdf --quality ebook
```

**Convert and compress a Word document:**  
```bash
shift report.docx --to pdf
shift-compress report.pdf
```

**Clean up a scanned document:**
```bash
shift-ocr scanned.pdf --output clean_text.txt
shift-pages scanned.pdf                     # Remove blank pages
```

**Batch process documents:**
```bash
shift documents/ --batch --from docx --to pdf
shift-compress *.pdf --batch
```

### Real-World Examples

**Research Paper Workflow:**
```bash
# Convert markdown to formatted PDF
shift paper.md --to pdf --css professional.css

# If too large for submission
shift-compress paper.pdf --quality printer
```

**Business Document Processing:**  
```bash
# Convert presentations and compress for email
shift *.pptx --to pdf
shift-compress *.pdf --quality ebook --batch
```

**Legal Document Management:**
```bash
# OCR scanned contracts  
shift-ocr contracts/ --batch --output text_versions/

# Remove sensitive pages
shift-pages contract.pdf --remove 3,7-9
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`  
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🐛 Issues

Report bugs and request features at: https://github.com/adamn1225/shift/issues

---

*Made with ❤️ for document processing efficiency*

1. **First, remove heavy pages:**
```bash
pdf-pages large_file.pdf --analyze          # See page breakdown
pdf-pages large_file.pdf                    # Interactive page removal
```

2. **Then compress the result:**
```bash
pdf-compress edited_file.pdf --dual         # Compress the page-reduced version
```

**Example Results:**
- Original: 47MB → Page-reduced: 32MB → Final: 13MB ✓

---

## PDF Page Management

Analyze PDF structure and remove pages to reduce file size:

```bash
pdf-pages document.pdf --analyze            # Show page breakdown
pdf-pages document.pdf                      # Interactive page removal
pdf-pages document.pdf --remove 1,3,5-7     # Remove specific pages
```

The analyzer shows which pages have the most images and estimated size impact.

---

## Document Conversion

Convert a Word document to PDF:
```bash
doc-convert document.docx --to pdf
```

Convert a Markdown file to HTML with a custom stylesheet:
```bash
doc-convert report.md --to html --css style.css
```

Extract text from a PDF file:
```bash
doc-convert file.pdf --to text --output extracted.txt
```

Batch convert all Word documents in a folder to PDF:
```bash
doc-convert folder/ --batch --from docx --to pdf --output converted/
```

---

## Summary

You now have a complete PDF management toolkit:

1. **For regular PDFs**: Use `pdf-compress --dual` to create both quality and email versions
2. **For large PDFs**: Use `pdf-pages` first to remove heavy pages, then compress
3. **For document conversion**: Use `doc-convert` between formats

All tools work from anywhere in your terminal and provide detailed help with `-h` or `--help`.
