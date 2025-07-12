#!/usr/bin/env python3
"""
enhanced HTTP server with caching and compression for loyal.love-website
"""

import http.server
import socketserver
import os
import gzip
import mimetypes
from pathlib import Path
import time
import io
import sys

########################################################
#                  constants
########################################################

PORT = 8000

########################################################
#           main class and methods
########################################################

class EnhancedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('image/webp', '.webp')
        super().__init__(*args, **kwargs)

    def handle_one_request(self):
        """Override to handle broken pipe errors gracefully"""
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError) as e:
            pass
        except Exception as e:
            if hasattr(self, 'log_error'):
                self.log_error(f"Unexpected error: {e}")
            else:
                print(f"Unexpected error: {e}", file=sys.stderr)

    def end_headers(self):
        # add security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.add_caching_headers()
        
        super().end_headers()

    def add_caching_headers(self):
        """Add appropriate caching headers based on file type"""
        path = self.path.lower()
        
        # Images - cache for 1 year
        if any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico']):
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
            self.send_header('Expires', self.date_time_string(time.time() + 31536000))
        
        # CSS and JS - cache for 1 month
        elif any(ext in path for ext in ['.css', '.js']):
            self.send_header('Cache-Control', 'public, max-age=2592000')
            self.send_header('Expires', self.date_time_string(time.time() + 2592000))
        
        # HTML files - cache for 1 hour
        elif path.endswith('.html'):
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.send_header('Expires', self.date_time_string(time.time() + 3600))
        
        # Other static files - cache for 1 day
        else:
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.send_header('Expires', self.date_time_string(time.time() + 86400))

    def send_head(self):
        """Override send_head to add compression support"""
        path = self.translate_path(self.path)
        
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', self.path + '/')
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None
        
        accept_encoding = self.headers.get('Accept-Encoding', '')
        can_gzip = 'gzip' in accept_encoding
        
        stat = os.stat(path)
        mtime = self.date_time_string(stat.st_mtime)
        
        content_type = self.guess_type(path)
        
        should_compress = can_gzip and content_type in [
            'text/html', 'text/css', 'application/javascript', 
            'text/plain', 'application/json', 'text/xml'
        ]
        
        if should_compress:
            gzip_path = path + '.gz'
            if os.path.exists(gzip_path):
                try:
                    with open(gzip_path, 'rb') as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Content-Encoding', 'gzip')
                    self.send_header('Last-Modified', mtime)
                    self.end_headers()
                    return io.BytesIO(data)
                except (OSError, IOError) as e:
                    self.send_error(500, f"❌ error reading file: {e}")
                    return None
            else:
                try:
                    with open(path, 'rb') as f:
                        data = f.read()
                    compressed_data = gzip.compress(data)
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', str(len(compressed_data)))
                    self.send_header('Content-Encoding', 'gzip')
                    self.send_header('Last-Modified', mtime)
                    self.end_headers()
                    return io.BytesIO(compressed_data)
                except (OSError, IOError) as e:
                    self.send_error(500, f"❌ error reading file: {e}")
                    return None
        else:
            try:
                f = open(path, 'rb')
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(stat.st_size))
                self.send_header('Last-Modified', mtime)
                return f
            except OSError as e:
                self.send_error(404, f"❌ file not found: {e}")
                return None

    def copyfile(self, source, outputfile):
        """Override copyfile to handle broken pipe errors"""
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError) as e:
            # Don't log these common disconnections - they're normal
            pass
        except Exception as e:
            if hasattr(self, 'log_error'):
                self.log_error(f"❌ error during file transfer: {e}")
            else:
                print(f"❌ error during file transfer: {e}", file=sys.stderr)

    def log_message(self, format, *args):
        """Custom logging to show compression info"""
        if hasattr(self, 'headers') and 'Accept-Encoding' in self.headers:
            encoding = self.headers['Accept-Encoding']
            if 'gzip' in encoding:
                format += " [gzip supported]"
        super().log_message(format, *args)


def create_gzip_files():
    """Pre-compress static files for better performance"""
    static_extensions = ['.html', '.css', '.js', '.xml', '.txt']
    
    for ext in static_extensions:
        for file_path in Path('.').rglob(f'*{ext}'):
            if file_path.is_file() and not file_path.name.endswith('.gz'):
                gzip_path = file_path.with_suffix(file_path.suffix + '.gz')
                if not gzip_path.exists() or gzip_path.stat().st_mtime < file_path.stat().st_mtime:
                    with open(file_path, 'rb') as f_in:
                        with open(gzip_path, 'wb') as f_out:
                            f_out.write(gzip.compress(f_in.read()))
                    print(f"Created {gzip_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced HTTP server for loyal.love-website')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on (default: 8000)')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--precompress', action='store_true', help='Pre-compress static files')
    args = parser.parse_args()
    
    if args.precompress:
        print("Pre-compressing static files...")
        create_gzip_files()
        print("Pre-compression complete!")

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    
    with socketserver.TCPServer((args.host, args.port), EnhancedHTTPRequestHandler) as httpd:
        print(f"✨ server running at http://{args.host}:{args.port}")
        print("(press Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 shutting down server...")
            httpd.shutdown()


if __name__ == '__main__':
    main() 
