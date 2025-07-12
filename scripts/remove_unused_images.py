#!/usr/bin/env python3
"""
script to identify and remove unused images from the imgs directory.
this script will:
1. find all image files in the imgs/ directory
2. extract all image references from html files
3. identify which images are not referenced anywhere
4. remove the unused images (with confirmation)
"""

import os
import re
from pathlib import Path
import argparse


def find_all_image_files():
    """find all image files in the imgs directory."""
    imgs_dir = Path("imgs")
    image_files = set()
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        for file_path in imgs_dir.glob(ext):
            image_files.add(file_path.name)
    
    return image_files


def extract_image_references_from_html():
    """extract all image references from html files."""
    html_files = [Path('index.html')] + list(Path('chapters').glob('*.html'))
    referenced_images = set()
    for html_file in html_files:
        if not html_file.exists():
            continue
        print(f"scanning {html_file}...")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"  error reading file: {e}")
                continue
        img_pattern = r'src=["\']([^"\']*\.(?:png|jpg|jpeg|webp))["\']'
        matches = re.findall(img_pattern, content, re.IGNORECASE)
        for match in matches:
            filename = os.path.basename(match)
            referenced_images.add(filename)
            if filename.startswith('../imgs/'):
                filename = filename[8:]  # remove '../imgs/'
                referenced_images.add(filename)
            if 'loyal.love/imgs/' in match:
                filename = os.path.basename(match)
                referenced_images.add(filename)
            base_name = os.path.splitext(filename)[0]
            referenced_images.add(base_name)
    return referenced_images


def identify_unused_images():
    """identify which images are not referenced anywhere."""
    all_images = find_all_image_files()
    referenced_images = extract_image_references_from_html()
    print(f"\nfound {len(all_images)} total image files")
    print(f"found {len(referenced_images)} referenced images")
    unused_images = set()
    for image_file in all_images:
        base_name = os.path.splitext(image_file)[0]
        # check if either the full filename or base name is referenced
        if image_file not in referenced_images and base_name not in referenced_images:
            unused_images.add(image_file)
    
    print(f"found {len(unused_images)} unused images")
    return unused_images, all_images, referenced_images


def remove_unused_images(unused_images, dry_run=True):
    """remove unused images from the imgs directory."""
    imgs_dir = Path("imgs")
    removed_count = 0
    total_size_saved = 0
    print(f"\n{'[dry run] ' if dry_run else ''}removing unused images...")
    for filename in sorted(unused_images):
        file_path = imgs_dir / filename
        if file_path.exists():
            file_size = file_path.stat().st_size / (1024 * 1024)  # mb
            print(f"  {'would remove' if dry_run else 'removing'}: {filename} ({file_size:.1f}mb)")
            total_size_saved += file_size
            removed_count += 1
            if not dry_run:
                try:
                    file_path.unlink()
                    print(f"  ✓ removed: {filename}")
                except Exception as e:
                    print(f"  ✗ error removing {filename}: {e}")
    print(f"\n{'would save' if dry_run else 'saved'}: {total_size_saved:.1f}mb by removing {removed_count} unused images")
    return removed_count, total_size_saved


def main():
    parser = argparse.ArgumentParser(description='remove unused images from the imgs directory')
    parser.add_argument('--dry-run', action='store_true', help='show what would be removed without actually removing files')
    parser.add_argument('--list-unused', action='store_true', help='just list unused images without removing them')
    args = parser.parse_args()
    print("analyzing image usage...")
    unused_images, _, _ = identify_unused_images()
    if unused_images:
        print(f"\nunused images:")
        for filename in sorted(unused_images):
            print(f"  - {filename}")
        if args.list_unused:
            return
        if not args.dry_run:
            response = input(f"\nremove {len(unused_images)} unused images? (y/n): ")
            if response.lower() != 'y':
                print("operation cancelled.")
                return
        remove_unused_images(unused_images, dry_run=args.dry_run)
    else:
        print("\nno unused images found!")
    print("\ndone!")


if __name__ == "__main__":
    main() 