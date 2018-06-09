#!/usr/bin/env python

'''Simple utility functions to manage a personal static website'''

import os
import argparse
import json
from os import path
from datetime import datetime

import markdown


# Paths & Constants
POSTS_LIST = './posts.json'
POSTS_FOLDER = './posts'
MD_FOLDER = './posts.md'

INDEX_TEMPLATE = './templates/index.html'
PREVIEW_TEMPLATE = './templates/post_preview.html'
POST_TEMPLATE = './templates/post.html'

# ===================================================================

# Helper functions and JSON utils

def load_json(filename: str):
    with open(filename, 'r') as fj:
        return json.loads(fj.read())

def dump_json(filename: str, data: list):
    with open(filename, 'w') as fj:
        fj.write(json.dumps(data, indent=4))

def get_post(key: str, data: list):
    for i, post in enumerate(data):
        if post['id'] == key:
            return data.pop(i)
    return None

def build_paths(markdown: str):
    '''
     build full paths for a post with extension suffixes.
    '''
    source = path.join(MD_FOLDER, markdown)
    output = path.join(POSTS_FOLDER, markdown[:-3] + '.html')
    return source, output

def load_template(template_name):
    with open(template_name) as ft:
        return ft.read()
    
def render_post(title, md_path, timestamp):
    '''
     generate post html by injecting redered markdown
     into the post template
    '''
    template = load_template(POST_TEMPLATE)
    
    with open(md_path, 'r') as f:
        # construct post data from markdown
        post_md = f.read()
        post_html = markdown.markdown(
            post_md, extensions=['markdown.extensions.extra']
        )

    return template.format(
        title=title,
        timestamp=timestamp,
        post=post_html
    )

def build_post(post, posts_list):
    '''
     write post's html page and update it's entry in posts.json
    '''
    timestamp = "{:%B, %d %Y}".format(datetime.now())
    post['timestamp'] = timestamp
    
    html = render_post(
        title=post['title'],
        md_path=post['md_path'],
        timestamp=timestamp
    )
    posts_list.append(post)

    with open(post['html_path'], 'w') as html_file:
        html_file.write(html)

    dump_json(POSTS_LIST, posts_list)

def render_preview(info, template):
    return template.format(
        title=info['title'], 
        timestamp=info['timestamp'], 
        preview=info['preview'],
        link=info['link'],
    )

# ===================================================================

# site managment utils

def add_new_post(title, preview, md_path):
    '''
     Add a new post to the blog, this command generates post's html page
     and adds post's info to the posts.json list.

     params:
        - title: Post's actual title for the blog
        - markdown: Post's markdown file name in the posts.md folder
    '''
    posts_list = load_json(POSTS_LIST)
    md_path, html_path = build_paths(md_path)
    
    new_id = len(posts_list) + 1
    post = {
        'id': new_id,'title': title, 'md_path': md_path, 
        'html_path': html_path, 'preview': preview, 
        'link': html_path.strip('.')
    }

    build_post(post, posts_list)

def update_post(key):
    '''
     rebuild post's html page from markdown file
    '''
    posts_list = load_json(POSTS_LIST)
    post = get_post(key, posts_list)
    
    if post:
        build_post(post, posts_list)
    else:
        raise Exception("Post with id {} Not Found.".format(key))

def build_index():
    '''
     Generate Index page and add all posts previews to it.
    '''
    posts_list = load_json(POSTS_LIST)
    template = load_template(INDEX_TEMPLATE)
    preview_template = load_template(PREVIEW_TEMPLATE)
    
    previews = ''.join([
        render_preview(post, preview_template) for post in reversed(posts_list)
    ])

    html = template.format(previews=previews)

    with open('./index.html', 'w') as fi:
        fi.write(html)

def list_posts():
    posts_list = load_json(POSTS_LIST)
    for post in posts_list:
        print("#{id}: {title} > {md}".format(
            id=post['id'], title=post['title'], md=post['md_path']
        ))

# ===================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='simple tool to manage this static website'
    )
    parser.add_argument(
        '--add', 
        help='add a new post, takes an argument in the form of title:markdown:preview'
    )
    parser.add_argument(
        '--update', type=int, 
        help='Update post html page',
    )
    parser.add_argument(
        '--build', help='build index page and comile new posts',
        action="store_true"
    )
    parser.add_argument(
        '--list', help='list posts with there id and title',
        action='store_true'
    )
    args = parser.parse_args()

    if args.build:
        build_index()
    
    if args.update:
        try:
            update_post(args.update)
        except Exception as e:
            print(e)

    if args.add:
        title, md_file, preview = args.add.split(':')
        add_new_post(title, preview, md_file)

    if args.list:
        list_posts()

