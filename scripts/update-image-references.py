#!/usr/bin/env python3
"""
update image references in html files to use optimized images
"""

import os
import re
from pathlib import Path
import argparse


def find_html_files(directory):
    """find all html files in the directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files


def get_optimized_image_path(original_path):
    """get the path to the optimized version of an image"""
    if not original_path:
        return original_path
    clean_path = original_path.lstrip('/')
    if clean_path.startswith('imgs/'):
        clean_path = clean_path[5:]  # remove 'imgs/' prefix
    optimized_path = f"imgs/{clean_path.replace('.png', '_optimized.png').replace('.jpg', '_optimized.jpg').replace('.jpeg', '_optimized.jpeg')}"
    if os.path.exists(optimized_path):
        return optimized_path
    return original_path


def update_image_references_in_file(file_path):
    """update image references in a single html file"""
    print(f"processing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  ✗ error reading file: {e}")
            return False
    original_content = content
    img_pattern = r'src=["\']([^"\']*\.(?:png|jpg|jpeg))["\']'
    
    def replace_image(match):
        original_src = match.group(1)
        optimized_src = get_optimized_image_path(original_src)
        
        if optimized_src != original_src:
            print(f"  {original_src} → {optimized_src}")
            return f'src="{optimized_src}"'
        return match.group(0)
    
    content = re.sub(img_pattern, replace_image, content, flags=re.IGNORECASE)
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ updated {file_path}")
            return True
        except Exception as e:
            print(f"  ✗ error writing file: {e}")
            return False
    else:
        print(f"  - no changes needed")
        return False


def clean_up_original_images(dry_run=True):
    """remove original large images (keeping optimized versions)"""
    print(f"\n{'[dry run] ' if dry_run else ''}cleaning up original images...")
    optimized_images = set()
    for ext in ['_optimized.png', '_optimized.jpg', '_optimized.jpeg']:
        for file_path in Path('imgs').rglob(f'*{ext}'):
            original_name = file_path.name.replace('_optimized', '')
            optimized_images.add(original_name)
    removed_count = 0
    total_size_saved = 0
    
    for file_path in Path('imgs').rglob('*'):
        if file_path.is_file() and file_path.name in optimized_images:
            if '_optimized' in file_path.name or '_webp.webp' in file_path.name:
                continue
            file_size = file_path.stat().st_size / (1024 * 1024)  # mb
            print(f"  would remove: {file_path.name} ({file_size:.1f}mb)")
            total_size_saved += file_size
            removed_count += 1
            if not dry_run:
                file_path.unlink()
                print(f"  ✓ removed: {file_path.name}")
    print(f"\n{'would save' if dry_run else 'saved'}: {total_size_saved:.1f}mb by removing {removed_count} original images")
    return removed_count, total_size_saved


def main():
    parser = argparse.ArgumentParser(description='update image references in html files')
    parser.add_argument('--directory', default='.', help='directory to search for html files')
    parser.add_argument('--cleanup', action='store_true', help='remove original images after updating references')
    parser.add_argument('--dry-run', action='store_true', help='show what would be done without making changes')
    args = parser.parse_args()
    html_files = find_html_files(args.directory)
    print(f"found {len(html_files)} html files to process")
    updated_count = 0
    for html_file in html_files:
        if update_image_references_in_file(html_file):
            updated_count += 1
    print(f"\nupdated {updated_count} html files")
    if args.cleanup:
        clean_up_original_images(dry_run=args.dry_run)
    print("\ndone!")


if __name__ == '__main__':
    main() 