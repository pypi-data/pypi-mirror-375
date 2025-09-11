from flask import Flask, request, jsonify, send_file, render_template_string
import subprocess
import tempfile
import os
from pathlib import Path
import sys

# Add the current directory to Python path
sys.path.append('.')

# Import your existing modules
from shift_converter import DocumentConverter
from pdf_compressor import PDFCompressor
from pdf_ocr import PDFOCRExtractor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shift - Document Processing API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .tool { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }
            code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            .endpoint { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Shift Document Processing API</h1>
            <p>REST API for document conversion, PDF compression, and OCR text extraction.</p>
            
            <div class="tool">
                <h3>📄 Document Conversion</h3>
                <p><span class="endpoint">POST /convert</span></p>
                <p>Convert between PDF, Word, HTML, Markdown, Text formats</p>
                <p>Form data: <code>file</code>, <code>target_format</code></p>
            </div>
            
            <div class="tool">
                <h3>🗜️ PDF Compression</h3>
                <p><span class="endpoint">POST /compress</span></p>
                <p>Compress PDFs for email attachments</p>
                <p>Form data: <code>file</code>, <code>quality</code> (optional: screen, ebook, printer)</p>
            </div>
            
            <div class="tool">
                <h3>🔍 OCR Text Extraction</h3>
                <p><span class="endpoint">POST /ocr</span></p>
                <p>Extract text from scanned PDFs and images</p>
                <p>Form data: <code>file</code>, <code>language</code> (optional, default: eng)</p>
            </div>
            
            <div class="tool">
                <h3>🪟 Windows PowerShell Installation</h3>
                <p><span class="endpoint">GET /install</span></p>
                <p>PowerShell one-liner: <code>iwr {{ request.host_url }}install | iex</code></p>
            </div>
            
            <div class="tool">
                <h3>📦 PowerShell Module</h3>
                <p><span class="endpoint">GET /Shift.psm1</span></p>
                <p>Download the PowerShell module directly</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        target_format = request.form.get('target_format', 'pdf')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            file.save(tmp.name)
            input_path = Path(tmp.name)
        
        try:
            # Create output file
            output_path = input_path.with_suffix(f'.{target_format}')
            
            # Use your existing converter
            converter = DocumentConverter()
            success = converter.convert_file(input_path, output_path, target_format)
            
            if success and output_path.exists():
                return send_file(str(output_path), as_attachment=True, 
                               download_name=f"{Path(file.filename).stem}.{target_format}")
            else:
                return jsonify({'error': 'Conversion failed'}), 500
                
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress', methods=['POST'])
def compress_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        quality = request.form.get('quality', 'ebook')
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files supported for compression'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            file.save(tmp.name)
            input_path = Path(tmp.name)
        
        try:
            output_path = input_path.with_name(f"{input_path.stem}_compressed.pdf")
            
            # Use your existing compressor
            compressor = PDFCompressor()
            success = compressor.compress_pdf_basic(input_path, output_path)
            
            if success and output_path.exists():
                return send_file(str(output_path), as_attachment=True, 
                               download_name=f"{Path(file.filename).stem}_compressed.pdf")
            else:
                return jsonify({'error': 'Compression failed'}), 500
                
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ocr', methods=['POST'])
def ocr_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        language = request.form.get('language', 'eng')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            file.save(tmp.name)
            input_path = Path(tmp.name)
        
        try:
            # Use your existing OCR extractor
            ocr = PDFOCRExtractor(language=language)
            
            if input_path.suffix.lower() == '.pdf':
                text = ocr.extract_text_from_pdf(input_path)
            else:
                text = ocr.extract_text_from_image(input_path)
            
            return jsonify({'text': text})
                
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/install')
def install_script():
    """Serve the PowerShell installation script"""
    script_content = f"""
# Shift Cloud CLI - PowerShell Installer
# Auto-generated install script

$InstallDir = "$env:USERPROFILE\\shift-cloud"
$ServiceUrl = "{request.host_url.rstrip('/')}"

Write-Host "🚀 Installing Shift Cloud CLI..." -ForegroundColor Cyan

# Create installation directory
if (!(Test-Path $InstallDir)) {{
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}}

try {{
    # Download PowerShell module
    $moduleUrl = "{request.host_url}Shift.psm1"
    $modulePath = "$InstallDir\\Shift.psm1"
    
    Write-Host "📥 Downloading module..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $moduleUrl -OutFile $modulePath -UseBasicParsing
    
    # Install to PowerShell modules directory
    $userModulePath = "$env:USERPROFILE\\Documents\\PowerShell\\Modules\\Shift"
    if (!(Test-Path $userModulePath)) {{
        New-Item -ItemType Directory -Path $userModulePath -Force | Out-Null
    }}
    
    Copy-Item $modulePath $userModulePath -Force
    
    Write-Host "✅ Installation complete!" -ForegroundColor Green
    Write-Host "Usage: shift-convert document.docx -To pdf" -ForegroundColor White
    Write-Host "Import: Import-Module Shift" -ForegroundColor White
    
}} catch {{
    Write-Error "Installation failed: $($_.Exception.Message)"
}}
"""
    return script_content, 200, {'Content-Type': 'text/plain'}

@app.route('/Shift.psm1')
def serve_module():
    """Serve the PowerShell module file"""
    return send_file('Shift.psm1', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
