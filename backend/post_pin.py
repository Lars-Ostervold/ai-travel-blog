import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Load environment variables
CLIENT_ID = os.getenv("PINTEREST_APP_ID")
CLIENT_SECRET = os.getenv("PINTEREST_APP_SECRET")
USER_TOKEN = os.getenv("PINTEREST_USER_TOKEN")

def fetch_boards(access_token):
    boards_url = "https://api.pinterest.com/v5/boards/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(boards_url, headers=headers)
    if response.status_code == 200:
        boards = response.json()["items"]
        for board in boards:
            print(f"Board ID: {board['id']}, Name: {board['name']}")
    else:
        print("Error fetching boards:", response.json())

def create_pin(access_token, board_id, title, description, media_url, link):
    pin_url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "media_source": {
            "source_type": "image_url",
            "url": media_url
        },
        "link": link,  # Optional: Add a destination link
    }
    response = requests.post(pin_url, json=payload, headers=headers)
    if response.status_code == 201:
        print("Pin Created Successfully:", response.json())
    else:
        print("Error creating pin:", response.json())

def fetch_pins(access_token, board_id):
    pins_url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(pins_url, headers=headers)
    if response.status_code == 200:
        pins = response.json()["items"]
        for pin in pins:
            print(f"Pin ID: {pin['id']}, Title: {pin['title']}, Description: {pin['description']}")
    else:
        print("Error fetching pins:", response.json())

# Main Execution
if __name__ == "__main__":
    # Fetch access token
    access_token = USER_TOKEN
    if access_token:


        # Define pin details
        board_id = "1050253644291870813"
        title = "Soak Up Family Fun: Your Ultimate Guide to Hot Springs National Park Adventures!"
        description = "This is an example pin created using the Pinterest API."
        media_url = "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/travel-blog-images/image_27_0.png"  # Replace with your image URL
        link = "https://chasingmemories.blog/posts/27_blog"  # Replace with your blog post URL

        #Create the pin
        # fetch_boards(access_token)
        # fetch_pins(access_token, board_id)
        create_pin(access_token, board_id, title, description, media_url, link)
        
