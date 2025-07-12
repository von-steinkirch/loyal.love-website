#!/usr/bin/env python3
"""
simple script to fix image paths in HTML files
"""

import os
import re

def fix_image_paths():
    files_to_fix = [
        'chapters/24_winter.html',
        'chapters/25_spring.html'
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"❌ file not found: {file_path}")
            continue
        print(f"🟡 processing: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = re.sub(r'\.\./imgs/\.\./imgs/', '../imgs/', content)
        content = re.sub(r'imgs/\.\./imgs/', '../imgs/', content)
        content = re.sub(r'imgs/\.\.//imgs/', '../imgs/', content)
        content = re.sub(r'src="imgs/([^"]*\.(?:png|jpg|jpeg|webp))"', r'src="../imgs/\1"', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"updated {file_path}")
        else:
            print(f"no changes needed")

if __name__ == '__main__':
    fix_image_paths()
    print("✅ done!")
