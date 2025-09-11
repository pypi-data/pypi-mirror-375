#!/usr/bin/env python3
"""
Setup script for Shift - Universal Document Converter
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "Universal document format converter"

setup(
    name="shift-cli",
    version="1.0.5",
    description="Universal document and PDF toolkit - Convert, compress, edit, and process documents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Adam N.",
    author_email="anoah1225@gmail.com",
    url="https://github.com/adamn1225/shift",
    packages=[],  # No packages - we use py_modules instead
    py_modules=[
        "shift_converter",
        "pdf_compressor", 
        "pdf_editor",
        "pdf_page_manager",
        "pdf_ocr",
        "shift_cloud_cli",
        "main"
    ],
    install_requires=[
        "pypdf>=5.9.0",
        "fpdf2>=2.8.0", 
        "markdown>=3.8.0",
        "beautifulsoup4>=4.13.0",
        "python-docx>=1.2.0",
        "docx2python>=3.5.0",
        "pdfkit>=1.0.0",
        "html2text>=2025.4.0",
        "Pillow>=11.0.0",
        "pymupdf>=1.23.0",
        "pytesseract>=0.3.10",
    ],
    entry_points={
        'console_scripts': [
            'shift-convert=shift_converter:main',
            'shift=shift_converter:main',  # Keep both for compatibility
            'shift-compress=pdf_compressor:main',
            'shift-pages=pdf_page_manager:main', 
            'shift-edit=pdf_editor:main',
            'shift-ocr=pdf_ocr:main',
            'shift-cloud=shift_cloud_cli:main',
            'shift-web=main:app',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    package_data={
        '': ['*.css'],
    },
    include_package_data=True,
)
