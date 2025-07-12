#!/usr/bin/env python3
"""
script to clean up image files by keeping only webp versions and updating html references.
this script will:
1. find all image files in the imgs/ directory
2. keep only the webp versions (smallest, modern format)
3. update all html files to reference the webp versions
4. delete original and optimized versions
"""


import re
from pathlib import Path


def find_image_groups():
    """find all image groups (original, optimized, webp) in the imgs directory."""
    imgs_dir = Path("imgs")
    image_groups = {}
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        for file_path in imgs_dir.glob(ext):
            filename = file_path.name
            base_name = None
            if filename.endswith('_optimized.png'):
                base_name = filename[:-13]  # remove '_optimized.png'
            elif filename.endswith('_optimized.jpg'):
                base_name = filename[:-13]  # remove '_optimized.jpg'
            elif filename.endswith('_webp.webp'):
                base_name = filename[:-9]   # remove '_webp.webp'
            elif filename.endswith('.png') and not filename.endswith('_optimized.png'):
                base_name = filename[:-4]   # remove '.png'
            elif filename.endswith('.jpg') and not filename.endswith('_optimized.jpg'):
                base_name = filename[:-4]   # remove '.jpg'
            elif filename.endswith('.jpeg'):
                base_name = filename[:-5]   # remove '.jpeg'
            if base_name:
                if base_name not in image_groups:
                    image_groups[base_name] = {}
                
                if filename.endswith('_optimized.png') or filename.endswith('_optimized.jpg'):
                    image_groups[base_name]['optimized'] = filename
                elif filename.endswith('_webp.webp'):
                    image_groups[base_name]['webp'] = filename
                else:
                    image_groups[base_name]['original'] = filename
    return image_groups


def update_html_references():
    """update all html files to reference webp versions instead of optimized versions."""
    html_files = [Path('index.html')] + list(Path('chapters').glob('*.html'))
    
    for html_file in html_files:
        if not html_file.exists():
            continue
        print(f"processing {html_file}...")
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # replace optimized references with webp references
        # pattern: imgs/../imgs/filename_optimized.ext or imgs/filename_optimized.ext
        content = re.sub(
            r'imgs/(?:\.\./)?imgs/([^_]+)_optimized\.(png|jpg)',
            r'imgs/\1_webp.webp',
            content
        )
        
        # also handle direct references without the ../imgs/ part
        content = re.sub(
            r'src="imgs/([^_]+)_optimized\.(png|jpg)"',
            r'src="imgs/\1_webp.webp"',
            content
        )
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"updated {html_file}")


def cleanup_images(image_groups):
    """delete original and optimized versions, keeping only webp versions."""
    imgs_dir = Path("imgs")
    deleted_count = 0
    
    for _, versions in image_groups.items():
        if 'webp' in versions:
            webp_file = imgs_dir / versions['webp']
            print(f"keeping: {webp_file}")
            if 'original' in versions:
                original_file = imgs_dir / versions['original']
                if original_file.exists():
                    original_file.unlink()
                    print(f"deleted: {original_file}")
                    deleted_count += 1
            if 'optimized' in versions:
                optimized_file = imgs_dir / versions['optimized']
                if optimized_file.exists():
                    optimized_file.unlink()
                    print(f"deleted: {optimized_file}")
                    deleted_count += 1
    
    return deleted_count


def main():
    print("starting image cleanup process...")
    image_groups = find_image_groups()
    print(f"found {len(image_groups)} image groups")
    print("\nimage groups found:")
    for base_name, versions in image_groups.items():
        print(f"  {base_name}:")
        if 'original' in versions:
            print(f"    original: {versions['original']}")
        if 'optimized' in versions:
            print(f"    optimized: {versions['optimized']}")
        if 'webp' in versions:
            print(f"    webp: {versions['webp']} (keeping)")
        print()

    response = input("proceed with cleanup? (y/n): ")
    if response.lower() != 'y':
        print("cleanup cancelled.")
        return
    print("\nupdating html references...")
    update_html_references()
    print("\ncleaning up image files...")
    deleted_count = cleanup_images(image_groups)
    print(f"\ncleanup complete! deleted {deleted_count} files.")
    print("all html files now reference webp versions.")


if __name__ == "__main__":
    main()
