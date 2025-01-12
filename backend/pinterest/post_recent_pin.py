import os
from dotenv import load_dotenv
from backend.pinterest.pinterest_api import PinterestAPI
from backend.pinterest.pinterest_main import post_recent_pin

load_dotenv()
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

if __name__ == "__main__":
    access_token = USER_TOKEN
    if access_token:
        pinterest_api = PinterestAPI(access_token)
        post_recent_pin(pinterest_api, post_to_travel_board=True)