import requests
import os
from dotenv import load_dotenv
import random
from typing import List
from pinterest_api import PinterestAPI, Pin

load_dotenv()
# Load environment variables
CLIENT_ID = os.getenv("PINTEREST_APP_ID")
CLIENT_SECRET = os.getenv("PINTEREST_APP_SECRET")
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

from supabase import create_client, Client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

def make_list_from_comma_separated(string):
    t = string.split(',')
    t = [word.strip() for word in t]
    return t

def get_blog_post_details(blog_image):
    blog_post_id = blog_image.get('blog_post_id')
    blog_post_response = supabase.table('blog_posts').select('*').eq('id', blog_post_id).execute()
    blog_post = blog_post_response.data[0]
    title = blog_post.get('title')
    description = blog_post.get('excerpt')
    media_url = blog_image.get('image_url')
    board_names: List[str] = make_list_from_comma_separated(blog_post.get('pinterest_boards'))
    link = f"https://chasingmemories.blog/posts/{blog_post_id}_blog"
    return Pin(title, description, media_url, link, board_names).to_dict()

def get_all_blog_images_entries_in_pin_list():
    response = supabase.table('blog_images').select('*').execute()
    pins = [get_blog_post_details(blog_image) for blog_image in response.data]
    return pins

def get_most_recent_blog_post_images():
    response = supabase.table('blog_images').select('*').order('created_at', desc=True).limit(4).execute()
    pins = [get_blog_post_details(blog_image) for blog_image in response.data]
    return pins

def post_all_pins(pinterest_api, post_to_travel_board=False):
    pins = get_all_blog_images_entries_in_pin_list()
    for pin in pins:
        for board_name in pin.get('boards_to_post_to'):
            board_id = pinterest_api.get_board_id_from_name(board_name)
            pinterest_api.post_pin(board_id, pin.get('title'), pin.get('description'), pin.get('media_url'), pin.get('link'))
            if post_to_travel_board:
                pinterest_api.post_pin_to_travel_board(pin.get('title'), pin.get('description'), pin.get('media_url'), pin.get('link'))

def post_random_pin_single_board(pinterest_api):
    pins = get_all_blog_images_entries_in_pin_list()
    random_pin = random.choice(pins)  
    board = random.choice(random_pin.get('boards_to_post_to'))
    board_id = pinterest_api.get_board_id_from_name(board)
    pinterest_api.post_pin(board_id, random_pin.get('title'), random_pin.get('description'), random_pin.get('media_url'), random_pin.get('link'))

def post_random_pin_multiple_boards(pinterest_api, post_to_travel_board=False):
    pins = get_all_blog_images_entries_in_pin_list()
    random_pin = random.choice(pins)
    for board in random_pin.get('boards_to_post_to'):
        board_id = pinterest_api.get_board_id_from_name(board)
        pinterest_api.post_pin(board_id, random_pin.get('title'), random_pin.get('description'), random_pin.get('media_url'), random_pin.get('link'))
        if post_to_travel_board:
            pinterest_api.post_pin_to_travel_board(random_pin.get('title'), random_pin.get('description'), random_pin.get('media_url'), random_pin.get('link'))

def post_recent_pin(pinterest_api, post_to_travel_board=False):
    pins = get_most_recent_blog_post_images()
    for pin in pins:
        for board_name in pin.get('boards_to_post_to'):
            board_id = pinterest_api.get_board_id_from_name(board_name)
            pinterest_api.post_pin(board_id, pin.get('title'), pin.get('description'), pin.get('media_url'), pin.get('link'))
            if post_to_travel_board:
                pinterest_api.post_pin_to_travel_board(pin.get('title'), pin.get('description'), pin.get('media_url'), pin.get('link'))