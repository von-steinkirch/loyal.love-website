#!/usr/bin/env python3
"""
replace optimized image references with actual existing images
"""

import os
import re


def fix_optimized_references():
    """replace optimized image references with actual images"""

    files_to_fix = [
        'index.html',
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
        content = re.sub(r'_optimized\.png', '.webp', content)
        content = re.sub(r'_optimized\.jpg', '.webp', content)
        content = re.sub(r'_optimized\.jpeg', '.webp', content)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ updated {file_path}")
        else:
            print(f"✅ no changes needed")


if __name__ == '__main__':
    fix_optimized_references()
