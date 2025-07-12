#!/usr/bin/env python3
"""
simple HTTP server for testing
"""

import http.server
import socketserver
import os
import sys

PORT = 8000


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        import mimetypes
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('image/webp', '.webp')
        mimetypes.add_type('video/mp4', '.mp4')
        mimetypes.add_type('video/quicktime', '.mov')
        super().__init__(*args, **kwargs)

    def handle_one_request(self):
        """Override to handle broken pipe errors gracefully"""
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"❌ client disconnected: {e}", file=sys.stderr)
        except Exception as e:
            print(f"❌ unexpected error: {e}", file=sys.stderr)

    def copyfile(self, source, outputfile):
        """Override copyfile to handle broken pipe errors"""
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"❌ client disconnected during file transfer: {e}", file=sys.stderr)
        except Exception as e:
            print(f"❌ error during file transfer: {e}", file=sys.stderr)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    with socketserver.TCPServer(("localhost", PORT), SimpleHTTPRequestHandler) as httpd:
        print(f"✨ simple server running at http://localhost:{PORT}")
        print("(press Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nshutting down server...")
            httpd.shutdown()


if __name__ == '__main__':
    main()