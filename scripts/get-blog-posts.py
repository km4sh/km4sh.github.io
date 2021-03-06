from notion.client import NotionClient
from datetime import datetime
import os
from slugify import slugify
import re
import hashlib
import shutil
import sys

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_ROOT_PAGE_ID = os.getenv('NOTION_ROOT_PAGE_ID')

if NOTION_TOKEN is None:
    sys.exit("The NOTION_TOKEN is missing, see the readme on how to set it.")
if NOTION_ROOT_PAGE_ID is None:
    sys.exit("The NOTION_ROOT_PAGE_ID is missing, see the readme on how to set it.")

client = NotionClient(token_v2=NOTION_TOKEN)
root_page_id = NOTION_ROOT_PAGE_ID

dest_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', 'content', 'posts'))

markdown_pages = {}
ignore_root = True


def download_file(file_url, destination_folder):
    print(f"-> Downloading {file_url}")
    r = client.get(file_url)
    # converts response headers mime type to an extension (may not work with everything)
    ext = r.headers['content-type'].split('/')[-1]
    file_name = '{}.{}'.format(hashlib.sha1(r.content).hexdigest(), ext)
    file_path = os.path.join(destination_folder, file_name)
    # open the file to write as binary - replace 'wb' with 'w' for text files
    os.makedirs(destination_folder, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(r.content)
    return file_name

def process_block(block, text_prefix=''):
    was_bulleted_list = False
    was_numbered_list = False
    count = 0
    text = ''
    metas = []

    for content in block.children:
        # Close the bulleted list.
        if was_bulleted_list and content.type != 'bulleted_list':
            text = text + '\n'
            was_bulleted_list = False

        if was_numbered_list and content.type != 'numbered_list':
            text = text + '\n'
            was_numbered_list = False
            count = 0

        if content.type == 'header':
            text = text + f'# {content.title}\n\n'
        elif content.type == 'sub_header':
            text = text + f'## {content.title}\n\n'
        elif content.type == 'sub_sub_header':
            text = text + f'### {content.title}\n\n'
        elif content.type == 'code':
            if content.title[:10] == '[METADATA]':
                regex_meta = re.compile(r'^ *(\w+) *:* (.+) *$')
                for item in content.title.split('\n')[1:]:
                    matchMeta = regex_meta.match(item)
                    if matchMeta:
                        key = matchMeta.group(1)
                        value = matchMeta.group(2)
                        if key == 'tags':
                            metas.append("{}: \n  - {}".format(
                                key,
                                '\n  - '.join(value.split(','))
                            ))
                        else:
                            metas.append(f"{key}: {value}")
            else:
                text = text + f'```{content.language}\n{content.title}\n```\n\n'
        elif content.type == 'image':
            path = content.source.replace('/signed/', '/image/')
            path = path + f"table=block&id={content.id}"
            path = path + f"&spaceId={content.parent.space_info['spaceId']}"
            image_name = download_file(path, dest_path)
            text = text + text_prefix + f'![{image_name}]({image_name})\n\n'
        elif content.type == 'bulleted_list':
            text = text + text_prefix + f'* {content.title}\n'
            was_bulleted_list = True
        elif content.type == 'numbered_list':
            count += 1
            text = text + text_prefix + f'{count}. {content.title}\n'
            was_numbered_list = True
        elif content.type == 'divider':
            text = text + '---\n'
        elif content.type == 'text':
            text = text + text_prefix + f'{content.title}\n\n'
        elif content.type == 'video':
            text = text + f'`video: {content.source}`\n\n'
        elif content.type == 'page':
            subpage_slug = fetch_notion_page(content.id, ignore=False)
            text = text + f'[{content.title}](/posts/{subpage_slug})\n\n'
        elif content.type == 'callout':
            text = text + text_prefix + f'{content.title}\n\n'
        elif content.type == 'bookmark':
            text = text + text_prefix + f'\n[{content.title}]({content.link})\n\n'
        elif content.type == 'quote':
            text = text + '> {:s}'.format(content.title.replace("\n", "\n>\n> ")) + "\n\n"
        elif content.type == 'table_of_contents':
            text = text + text_prefix + '\n<!--TOC-->\n\n'
        else:
            print("Unsupported type: " + content.type)

        if len(content.children) and content.type != 'page':
            child_text, child_metas = process_block(content, '  ')
            text = text + child_text
            metas = metas + child_metas

    return text, metas


def fetch_notion_page(page_id, ignore):
    page = client.get_block(page_id)
    page_title = page.title
    print("-> Now fetching:", page_title)
    slug = page_id
    text = ''
    metas = []
    # Handle Frontmatter
    isotime = datetime.fromtimestamp(int(page._get_record_data()['last_edited_time']) // 1000).isoformat()
    isotime = isotime + '.121Z'
    metas.append('title: "{}"'.format(page.title))
    metas.append('date: "{}"'.format(isotime))
    metas.append('slug: "{}"'.format(slug))

    # Download the cover and add it to the frontmatter.

    text, child_metas = process_block(page)

    metas = metas + child_metas
    metaText = '---\n' + '\n'.join(metas) + '\n---\n'
    text = metaText + text

    # Save the page data if it is not the root page.
    if not ignore:
        markdown_pages[slug] = text

    return slug


if __name__ == "__main__":
    print(f'-> Cleaning the" {dest_path}" folder')

    try:
        shutil.rmtree(dest_path)
        os.mkdir(dest_path)
    except FileNotFoundError:
        os.mkdir(dest_path)

    fetch_notion_page(root_page_id, ignore=ignore_root)

    for slug, markdown in markdown_pages.items():
        file_name = slug + '.md'
        file_path = os.path.join(dest_path, file_name)

        file = open(file_path, 'w')
        file.write(markdown)

        print('-> Imported "' + file_name + '"')

    print('Done: imported ' + str(len(markdown_pages)) + ' pages.')
