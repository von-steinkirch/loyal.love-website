#!/usr/bin/env python3
"""
image optimization script for loyal.love-website
compresses images and creates webp versions for better performance
"""

import os
import sys
from pathlib import Path
from PIL import Image
import subprocess
import argparse


def optimize_image(input_path, output_path, quality=85, max_width=None, max_height=None):
    """optimize a single image"""
    try:
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            if max_width or max_height:
                img.thumbnail((max_width or img.width, max_height or img.height), Image.Resampling.LANCZOS)
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"error optimizing {input_path}: {e}")
        return False


def create_webp(input_path, output_path, quality=80):
    """create webp version of image"""
    try:
        cmd = [
            'cwebp',
            '-q', str(quality),
            '-m', '6',  # method 6 for best compression
            '-af',  # auto-filter
            '-f', '40',  # filter strength
            '-sharpness', '0',  # sharpness
            '-mt',  # multi-threading
            input_path,
            '-o', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"error creating webp for {input_path}: {e}")
        return False


def get_file_size_mb(file_path):
    """get file size in mb"""
    return os.path.getsize(file_path) / (1024 * 1024)


def optimize_images_in_directory(directory, quality=85, webp_quality=80, max_width=1920, max_height=1080):
    """optimize all images in a directory"""
    image_extensions = {'.jpg', '.jpeg', '.png'}
    optimized_count = 0
    total_saved = 0
    
    print(f"optimizing images in {directory}...")
    for file_path in Path(directory).rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            if file_path.stem.endswith('_optimized') or file_path.stem.endswith('_webp'):
                continue
            original_size = get_file_size_mb(file_path)
            optimized_path = file_path.parent / f"{file_path.stem}_optimized{file_path.suffix}"
            if optimize_image(str(file_path), str(optimized_path), quality, max_width, max_height):
                optimized_size = get_file_size_mb(optimized_path)
                saved = original_size - optimized_size
                total_saved += saved
                print(f"✓ {file_path.name}: {original_size:.1f}mb → {optimized_size:.1f}mb (saved {saved:.1f}mb)")
                webp_path = file_path.parent / f"{file_path.stem}_webp.webp"
                if create_webp(str(optimized_path), str(webp_path), webp_quality):
                    webp_size = get_file_size_mb(webp_path)
                    print(f"  webp: {webp_size:.1f}mb")
                
                optimized_count += 1
    print(f"\noptimization complete!")
    print(f"optimized {optimized_count} images")
    print(f"total space saved: {total_saved:.1f}mb")
    return optimized_count, total_saved


def main():
    parser = argparse.ArgumentParser(description='optimize images for web performance')
    parser.add_argument('--directory', default='imgs', help='directory containing images to optimize')
    parser.add_argument('--quality', type=int, default=85, help='jpeg quality (1-100)')
    parser.add_argument('--webp-quality', type=int, default=80, help='webp quality (1-100)')
    parser.add_argument('--max-width', type=int, default=1920, help='maximum width for images')
    parser.add_argument('--max-height', type=int, default=1080, help='maximum height for images')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"directory {args.directory} does not exist")
        sys.exit(1)
    optimize_images_in_directory(
        args.directory, 
        args.quality, 
        args.webp_quality, 
        args.max_width, 
        args.max_height
    )


if __name__ == '__main__':
    main() 