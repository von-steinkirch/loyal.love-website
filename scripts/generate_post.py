#!/usr/bin/env python3

import datetime
from typing import Optional


def generate_post_id(date: datetime.date) -> str:
    """generate a post ID in the format YYYY_month_DD"""
    return f"{date.year}_{date.strftime('%B').lower()}_{date.day:02d}"


def generate_post_html(
    location: str,
    date: datetime.date,
    astro_status: str,
    main_content: str,
    main_image: str,
    post_side: str,
    meanwhile_title: Optional[str] = None,
    meanwhile_content: Optional[str] = None,
    meanwhile_image: Optional[str] = None,
) -> str:
    """generate HTML for a new post in the website's format."""
    
    post_id = generate_post_id(date)
    date_str = f"{date.year}, {date.strftime('%B').lower()}, {date.day}"

    html = f"""
    <hr class="between-posts" id="{post_id}" name="{post_id}" />
    <h2 class="post-title post-title-{post_side}">{location}; {date_str}</h2>
    <br />
    <h6 class="astro-status astro-status-{post_side}">
      {astro_status}
    </h6>

    <div class="two-column">
      <div class="text-column">
        <h3 class="post-text">
          {main_content}
        </h3>
      </div>
      <div class="image-column">
        <img src="{main_image}" class="image-50 image-rounded" />
      </div>
    </div>
    """

    if meanwhile_title or meanwhile_content:
        html += f"""
    <h2 class="meanwhile-title"> meanwhile... {meanwhile_title or ''} </h2>

    <div class="two-column">
      <div class="image-column">
        <img src="{meanwhile_image or 'imgs/lalala.png'}" class="image-30 image-rounded" />
      </div>
      <div class="text-column">
        <h3 class="post-text"> {meanwhile_content or ''} </h3>
      </div>
    </div>
    """
    
    return html


def insert_post_into_index(html_content: str, index_path: str = "index.html") -> None:
    """Insert the new post HTML at the top of the posts section in index.html"""

    with open(index_path, 'r') as f:
        content = f.read()
    
    insert_position = content.find('</div>\n    <script>\n      includeTitle(\'shared-title\')\n    </script>')
    if insert_position == -1:
        raise ValueError("Could not find the insertion point in index.html")
    
    new_content = content[:insert_position + len('</div>\n    <script>\n      includeTitle(\'shared-title\')\n    </script>')] + \
                 '\n\n    <!-- ............................................................................................................................................... -->\n' + \
                 '    <!-- .......................................       POST       ....................................................................................... -->\n' + \
                 '    <!-- ............................................................................................................................................... -->\n\n' + \
                 html_content + \
                 '\n\n    <!-- .........................................................       END        ................................................................... -->\n\n' + \
                 content[insert_position + len('</div>\n    <script>\n      includeTitle(\'shared-title\')\n    </script>'):]
    
    with open(index_path, 'w') as f:
        f.write(new_content)


def main():

    today = datetime.date.today()
    
    location = input("\n👾 enter location: ")
    astro_status = input("👾 enter astrological status: ")
    main_content = input("👾 enter main content (HTML format): ")
    main_image = input("👾 enter main image path: ")
    meanwhile_title = input("👾 enter meanwhile title: ")
    meanwhile_content = input("👾 enter meanwhile content: ")
    meanwhile_image = input("👾 enter meanwhile image path: ")
    post_side = input("👾 enter post side (left/right): ")
    
    post_html = generate_post_html(
        location=location,
        date=today,
        astro_status=astro_status,
        main_content=main_content,
        main_image=main_image,
        post_side=post_side,
        meanwhile_title=meanwhile_title,
        meanwhile_content=meanwhile_content,
        meanwhile_image=meanwhile_image,
    )
    
    try:
        insert_post_into_index(post_html)
        print("\n✅ post successfully added to index.html!\n")
    except Exception as e:
        print(f"❌ error adding post: {e}")


if __name__ == "__main__":
    main() 
