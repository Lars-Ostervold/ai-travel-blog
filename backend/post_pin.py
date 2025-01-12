import requests
import os
from dotenv import load_dotenv
import random
from typing import List

load_dotenv()
# Load environment variables
CLIENT_ID = os.getenv("PINTEREST_APP_ID")
CLIENT_SECRET = os.getenv("PINTEREST_APP_SECRET")
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

from supabase import create_client, Client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

class Pin:
    """
    Represents a Pin for Pinterest with a title, description, media URL, and link.
    Attributes:
        title (str): The title of the pin.
        description (str): The description of the pin.
        media_url (str): The URL of the media (image) for the pin.
        link (str): The link associated with the pin.
        boards_to_post_to (List[str]): The list of board names to post the pin to.
    """
    def __init__(self, title: str, description: str, media_url: str, link: str, boards_to_post_to: List[str]) -> None:
        """
        Initialize a Pin object.
        """
        self.title = title
        self.description = description
        self.media_url = media_url
        self.link = link
        self.boards_to_post_to = boards_to_post_to

    def to_dict(self) -> dict:
        """
        Convert the Pin object to a dictionary.

        :return: A dictionary representation of the Pin object.
        """
        return {
            "title": self.title,
            "description": self.description,
            "media_url": self.media_url,
            "link": self.link,
            "boards_to_post_to": self.boards_to_post_to
        }

class PinterestAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def fetch_boards(self):
        boards_url = "https://api.pinterest.com/v5/boards/"
        response = requests.get(boards_url, headers=self.headers)
        if response.status_code == 200:
            boards = response.json()["items"]
            for board in boards:
                print(f"Board ID: {board['id']}, Name: {board['name']}")
        else:
            print("Error fetching boards:", response.json())

    def post_pin(self, board_id, title, description, media_url, link):
        pin_url = "https://api.pinterest.com/v5/pins"
        payload = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": {
                "source_type": "image_url",
                "url": media_url
            },
            "link": link, 
        }
        response = requests.post(pin_url, json=payload, headers=self.headers)
        if response.status_code == 201:
            print("Pin Created Successfully:", response.json())
        else:
            print("Error creating pin:", response.json())

    def fetch_pins(self, board_id):
        pins_url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
        response = requests.get(pins_url, headers=self.headers)
        if response.status_code == 200:
            pins = response.json()["items"]
            for pin in pins:
                print(f"Pin ID: {pin['id']}, Title: {pin['title']}, Description: {pin['description']}")
        else:
            print("Error fetching pins:", response.json())
    
    def create_board_and_get_id(self, board_name):
        boards_url = "https://api.pinterest.com/v5/boards/"
        payload = {
            "name": board_name,
            "description": board_name,
            "privacy": "PUBLIC",
        }
        response = requests.post(boards_url, json=payload, headers=self.headers)
        if response.status_code == 201:
            board_id = response.json()["id"]
            print(f"Board {board_name} created with ID: {board_id}")
            return board_id
        else:
            print("Error creating board:", response.json())
            return None
    
    def get_board_id_from_name(self, board_name):
        boards_url = "https://api.pinterest.com/v5/boards/"
        response = requests.get(boards_url, headers=self.headers)
        if response.status_code == 200:
            boards = response.json()["items"]
            for board in boards:
                if board['name'] == board_name:
                    return board['id']
            print(f"Board {board_name} not found. Creating board...")
            return self.create_board_and_get_id(self.access_token, board_name)

        else:
            print("Error fetching boards:", response.json())
        return None
    
    def post_pin_to_travel_board(self, title, description, media_url, link):
        board_id = self.get_board_id_from_name('Travel')
        self.post_pin(board_id, title, description, media_url, link)

def add_travel_booard_to_pin(pin):
    pin['boards_to_post_to'].append('Travel')

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

# Main Execution
if __name__ == "__main__":
    # Fetch access token
    access_token = USER_TOKEN
    if access_token:
        pinterest_api = PinterestAPI(access_token)

        # Post all pins
        # post_all_pins(pinterest_api, post_to_travel_board=True)

        #Random
        # post_random_pin_single_board(pinterest_api)
        # post_random_pin_multiple_boards(pinterest_api, post_to_travel_board=True)

        #Recent
        # post_recent_pin(pinterest_api, post_to_travel_board=True)

        # Create the pin
        # pinterest_api.fetch_boards()
        # pinterest_api.fetch_pins(board_id)
        # pinterest_api.create_pin(board_id, title, description, media_url, link)