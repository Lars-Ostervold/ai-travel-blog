import os
from dotenv import load_dotenv
from backend.pinterest.pinterest_api import PinterestAPI
from backend.pinterest.pinterest_main import post_random_pin_single_board

load_dotenv()
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

if __name__ == "__main__":
    access_token = USER_TOKEN
    if access_token:
        pinterest_api = PinterestAPI(access_token)
        post_random_pin_single_board(pinterest_api)