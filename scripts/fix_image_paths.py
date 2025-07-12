#!/usr/bin/env python3
"""
fix image paths in HTML files to ensure they resolve correctly
"""

import os
import re
import argparse


def find_html_files(directory):
    """find all HTML files in the directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files


def fix_image_paths_in_file(file_path):
    """fix image paths in a single HTML file"""
    print(f"🟡 processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ error reading file: {e}")
            return False
    
    original_content = content
    changes_made = False
    
    file_dir = os.path.dirname(file_path)
    img_pattern = r'src=["\']([^"\']*\.(?:png|jpg|jpeg|webp))["\']'
    
    def replace_image(match):
        nonlocal changes_made
        original_src = match.group(1)
        
        if original_src.startswith('http'):
            return match.group(0)
        if original_src.startswith('data:'):
            return match.group(0)
        
        new_src = original_src
        if file_dir.endswith('chapters'):
            if original_src.startswith('imgs/'):
                new_src = '../' + original_src
            elif original_src.startswith('imgs/../imgs/'):
                new_src = '../imgs/' + original_src[12:]
            elif original_src.startswith('imgs/..//imgs/'):
                new_src = '../imgs/' + original_src[13:]
        
        if file_dir.endswith('chapters'):
            target_path = os.path.join(os.path.dirname(file_dir), new_src.lstrip('../'))
        else:
            target_path = os.path.join(os.path.dirname(file_path), new_src)
        
        if not os.path.exists(target_path):
            img_name = os.path.basename(original_src)
            imgs_dir = os.path.join(os.path.dirname(file_dir) if file_dir.endswith('chapters') else os.path.dirname(file_path), 'imgs')
            for ext in ['.webp', '.png', '.jpg', '.jpeg']:
                test_path = os.path.join(imgs_dir, os.path.splitext(img_name)[0] + ext)
                if os.path.exists(test_path):
                    if file_dir.endswith('chapters'):
                        new_src = f'../imgs/{os.path.basename(test_path)}'
                    else:
                        new_src = f'imgs/{os.path.basename(test_path)}'
                    break
        
        if new_src != original_src:
            print(f"  {original_src} → {new_src}")
            changes_made = True
            return f'src="{new_src}"'
        
        return match.group(0)
    
    content = re.sub(img_pattern, replace_image, content, flags=re.IGNORECASE)
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ updated {file_path}")
            return True
        except Exception as e:
            print(f"❌ error writing file: {e}")
            return False
    else:
        print(f"✅ no changes needed")
        return False


def main():
    parser = argparse.ArgumentParser(description='fix image paths in HTML files')
    parser.add_argument('--directory', default='.', help='directory to search for HTML files')
    parser.add_argument('--dry-run', action='store_true', help='show what would be done without making changes')
    
    args = parser.parse_args()
    html_files = find_html_files(args.directory)
    print(f"✅ found {len(html_files)} HTML files to process")
    updated_count = 0
    for html_file in html_files:
        if fix_image_paths_in_file(html_file):
            updated_count += 1
    
    print(f"\n✅ updated {updated_count} HTML files")
    print("\n✅ done!")


if __name__ == '__main__':
    main()
