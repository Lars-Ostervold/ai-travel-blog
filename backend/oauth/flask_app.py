from flask import Flask, redirect, request, render_template, url_for
import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
CLIENT_ID = os.getenv('PINTEREST_APP_ID')
CLIENT_SECRET = os.getenv('PINTEREST_APP_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

@app.route('/')
def pinterest_callback():
    code = request.args.get('code')
    print(f"code: {code}")
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
        f"&scope=boards:read"
    )
    return redirect(pinterest_url)




if __name__ == "__main__":
    app.run(host="localhost", port=8085, debug=True)
