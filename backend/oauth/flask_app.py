from flask import Flask, redirect, request, render_template, url_for, session
import requests
import os
import base64
from dotenv import load_dotenv

from supabase import create_client, Client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Load environment variables
CLIENT_ID = os.getenv('PINTEREST_APP_ID')
CLIENT_SECRET = os.getenv('PINTEREST_APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def fetch_most_recent_blog_post():
    response = supabase.table('blog_posts').select('*').order('created_at', desc=True).limit(1).execute()
    if response.data:
        return response.data[0]
    return None

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

@app.route('/generate_pin')
def generate_pin():
    blog_post = fetch_most_recent_blog_post()
    if blog_post:
        session['blog_post'] = blog_post
        return render_template('preview.html', blog_post=blog_post)
    return "No blog post found"

@app.route('/confirm_pin', methods=['POST'])
def confirm_pin():
    blog_post = session.get('blog_post')
    access_token = session.get('access_token')
    if blog_post and access_token:
        board_id = 1050253644291870813
        title = "Soak Up Family Fun: Your Ultimate Guide to Hot Springs National Park Adventures!"
        description = "This is an example pin created using the Pinterest API."
        media_url = "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/travel-blog-images/image_27_0.png"  # Replace with your image URL
        link = "https://chasingmemories.blog/posts/27_blog"  # Replace with your blog post URL
        create_pin(access_token, board_id, title, description, media_url, link)
        return "Pin posted successfully"
    return "Error posting pin"

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




if __name__ == "__main__":
    app.run(host="localhost", port=8085, debug=True)
