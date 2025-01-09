from flask import Flask, redirect, request, render_template, url_for, session
import requests
from typing import List
import os
import base64
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Load environment variables
CLIENT_ID = os.getenv('PINTEREST_APP_ID')
CLIENT_SECRET = os.getenv('PINTEREST_APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

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

def make_list_from_comma_separated(string):
    t = string.split(',')
    t = [word.strip() for word in t]
    return t

def create_board_and_get_id(access_token, board_name):
    boards_url = "https://api.pinterest.com/v5/boards/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": board_name,
        "description": board_name,
        "privacy": "PUBLIC",
    }
    response = requests.post(boards_url, json=payload, headers=headers)
    if response.status_code == 201:
        board_id = response.json()["id"]
        print(f"Board {board_name} created with ID: {board_id}")
        return board_id
    else:
        print("Error creating board:", response.json())
        return None

def get_board_id(access_token, board_name):
    boards_url = "https://api.pinterest.com/v5/boards/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(boards_url, headers=headers)
    if response.status_code == 200:
        boards = response.json()["items"]
        for board in boards:
            if board['name'] == board_name:
                return board['id']
        print(f"Board {board_name} not found. Creating board...")
        return create_board_and_get_id(access_token, board_name)

    else:
        print("Error fetching boards:", response.json())
    return None

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
        "link": link,
    }
    response = requests.post(pin_url, json=payload, headers=headers)
    if response.status_code == 201:
        print("Pin Created Successfully:", response.json())
    else:
        print("Error creating pin:", response.json())

'''
Home route of the application will render the auth.html template if no code exists.
If a code exists, the application will make a POST request to the Pinterest API to exchange the code for an access token.
If the request is successful, the access token will be saved in the session and the success.html template will be rendered.
'''
@app.route('/')
def pinterest_callback():
    code = request.args.get('code')
    
    if code is None:
        return render_template('auth.html')
    
    token_url = "https://api.pinterest.com/v5/oauth/token"

    # Encode the client ID and client secret
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64auth = base64.b64encode(auth.encode()).decode()
    print(f"b64auth: {b64auth}")
    post_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {b64auth}",
    }
    payload = f"grant_type=authorization_code&code={code}&redirect_uri={REDIRECT_URI}"

    response = requests.post(
        token_url,
        headers=post_headers,
        data=payload
    )

    if response.status_code == 200:
        print("Success")
        access_token = response.json().get("access_token")
        session['access_token'] = access_token
        # Save the access token securely
        return render_template("success.html", token=access_token)
    else:
        print(f"Error: {response.json()}")
        return f"Error: {response.json()}"

@app.route('/auth/pinterest')
def auth_pinterest():
    pinterest_url = (
        f"https://www.pinterest.com/oauth/?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=boards:read,pins:read,pins:write,boards:write"
    )
    return redirect(pinterest_url)

'''
The /available_pins will display all possible pins, sorted from newest to oldest.
Will include the photo, title, and description of the blog post.
'''
@app.route('/available_pins')
def available_pins():
    #We have two tables, blog_posts and blog_images.
    #The goal is to get every blog_image, then get the title and excerpt from the blog_post table where blog_post_id in blog_images matches id in blog_post.
    #Each one of those objects should be a new pin.
    response = supabase.table('blog_images').select('*').execute()
    pins = []
    for blog_image in response.data:
        blog_post_id = blog_image.get('blog_post_id')
        blog_post_response = supabase.table('blog_posts').select('*').eq('id', blog_post_id).execute()
        blog_post = blog_post_response.data[0]
        title = blog_post.get('title')
        description = blog_post.get('excerpt')
        media_url = blog_image.get('image_url')
        board_names: List[str] = make_list_from_comma_separated(blog_post.get('pinterest_boards'))
        link = f"https://chasingmemories.blog/posts/{blog_post_id}_blog"
        pin = Pin(title, description, media_url, link, board_names)
        pins.append(pin.to_dict())
    return render_template('available_pins.html', pins=pins)

@app.route('/confirm_pin', methods=['GET'])
def confirm_pin():
    title = request.args.get('title')
    description = request.args.get('description')
    photo = request.args.get('photo')
    link = request.args.get('link')
    boards = request.args.get('boards')
    return render_template('confirm_pin.html', title=title, description=description, photo=photo, link=link, boards=boards)

@app.route('/pin', methods=['POST'])
def pin():
    title = request.form.get('title')
    description = request.form.get('description')
    photo = request.form.get('photo')
    link = request.form.get('link')
    boards = make_list_from_comma_separated(request.form.get('boards'))

    board_ids = []
    for board in boards:
        id = get_board_id(session['access_token'], board_name=board)
        board_ids.append(id)
    
    for id in board_ids:
        create_pin(session['access_token'], id, title, description, photo, link)
    
    #Return JSON with status and message
    return {"status": "success", "message": "Pinning executed"}
    

if __name__ == "__main__":
    app.run(host="localhost", port=8085, debug=True)
