#!/usr/bin/env python3
"""
Shift CLI Client - Connects to Cloud Run service
Cross-platform wrapper for the hosted Shift service
"""

import requests
import argparse
import sys
from pathlib import Path
import os

class ShiftCloudClient:
    def __init__(self, service_url="https://shift-web.netlify.app"):
        self.service_url = service_url.rstrip('/')
        # Default to Netlify Functions endpoint
        if 'netlify.app' in service_url and not service_url.endswith('/.netlify/functions'):
            self.convert_endpoint = f"{self.service_url}/.netlify/functions/convert"
            self.health_endpoint = f"{self.service_url}/.netlify/functions/health"
        else:
            self.convert_endpoint = f"{self.service_url}/api/convert"
            self.health_endpoint = f"{self.service_url}/health"
    
    def convert(self, input_file, to_format, output_file=None):
        """Convert file using serverless API (works with Netlify Functions or Cloud Run)"""
        
        if not Path(input_file).exists():
            print(f"Error: File '{input_file}' not found")
            return False
        
        try:
            # For Netlify Functions, we need to send base64 encoded data
            if 'netlify' in self.service_url:
                return self._convert_netlify(input_file, to_format, output_file)
            else:
                return self._convert_multipart(input_file, to_format, output_file)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _convert_netlify(self, input_file, to_format, output_file):
        """Convert using Netlify Functions (base64 encoded)"""
        import base64
        
        # Read and encode file
        with open(input_file, 'rb') as f:
            file_data = base64.b64encode(f.read()).decode()
        
        data = {
            'file_data': file_data,
            'filename': Path(input_file).name,
            'to_format': to_format
        }
        
        print(f"📤 Converting {input_file} using Netlify Functions...")
        response = requests.post(
            self.convert_endpoint,
            json=data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # Decode and save converted file
                converted_data = base64.b64decode(result['data'])
                
                if not output_file:
                    output_file = result['filename']
                
                with open(output_file, 'wb') as f:
                    f.write(converted_data)
                
                print(f"✅ Converted: {output_file}")
                return True
            else:
                print(f"❌ Conversion failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
    
    def _convert_multipart(self, input_file, to_format, output_file):
        """Convert using multipart form data (for Cloud Run, etc.)"""
        with open(input_file, 'rb') as f:
            files = {'file': f}
            data = {'to_format': to_format}
            
            print(f"📤 Uploading {input_file} to cloud service...")
            response = requests.post(
                self.convert_endpoint,
                files=files,
                data=data,
                timeout=300
            )
        
        if response.status_code == 200:
            if not output_file:
                input_path = Path(input_file)
                output_file = f"{input_path.stem}.{to_format}"
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Converted: {output_file}")
            return True
        else:
            print(f"❌ Conversion failed: {response.status_code}")
            if response.text:
                print(f"Error: {response.text}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Shift Cloud CLI - Convert documents using hosted service",
        epilog="""
Examples:
  shift-cloud document.docx --to pdf
  shift-cloud report.md --to html --output result.html
  shift-cloud --service-url https://your-service.run.app file.pdf --to text
        """
    )
    
    parser.add_argument('input', help='Input file to convert')
    parser.add_argument('--to', '-t', required=True, help='Target format (pdf, docx, html, md, text)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--service-url', help='Custom Shift service URL', 
                       default=os.environ.get('SHIFT_SERVICE_URL', 'https://shift-web.netlify.app'))
    
    args = parser.parse_args()
    
    client = ShiftCloudClient(args.service_url)
    success = client.convert(args.input, args.to, args.output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
