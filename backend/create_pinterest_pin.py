import requests
import json

# Replace these with your actual Pinterest app credentials and access token
APP_ID = 'your_app_id'
APP_SECRET = 'your_app_secret'
ACCESS_TOKEN = 'your_access_token'

def create_pinterest_pin(board_id: str, image_url: str, link: str, title: str, description: str):
    """
    Creates a new Pinterest pin.

    Args:
        board_id (str): The ID of the Pinterest board where the pin will be created.
        image_url (str): The URL of the image to be pinned.
        link (str): The URL to which the pin will link.
        title (str): The title of the pin.
        description (str): The description of the pin.

    Returns:
        dict: The response from the Pinterest API.
    """
    url = f"https://api.pinterest.com/v1/pins/"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "board": board_id,
        "note": description,
        "link": link,
        "image_url": image_url
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create pin: {response.status_code} - {response.text}")

# Example usage
if __name__ == "__main__":
    board_id = "your_board_id"
    image_url = "https://your-image-url.com/image.jpg"
    link = "https://your-blog-url.com/post"
    title = "Your Blog Post Title"
    description = "Your Blog Post Description"

    try:
        pin_response = create_pinterest_pin(board_id, image_url, link, title, description)
        print("Pin created successfully:", pin_response)
    except Exception as e:
        print("Error creating pin:", e)