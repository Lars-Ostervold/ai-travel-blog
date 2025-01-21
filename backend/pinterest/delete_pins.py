import os
from dotenv import load_dotenv
from pinterest_api import PinterestAPI
from pinterest_main import post_recent_pin

load_dotenv()
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

def main():
    access_token = USER_TOKEN
    if access_token:
        pinterest_api = PinterestAPI(access_token)
        # pinterest_api.delete_n_most_recent_pins(32)
        # pinterest_api.delete_all_pins()

if __name__ == "__main__":
    main()