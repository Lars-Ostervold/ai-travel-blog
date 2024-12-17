##---Credit to yachty66 for the original code---##
##---https://github.com/yachty66/unofficial_midjourney_python_api--

import requests
import json
import time
import random
from urllib.parse import urlparse
from typing import Any, Dict, List

import os
from dotenv import load_dotenv
load_dotenv()

prompt = "A close-up portrait of an elderly Tibetan monk in natural sunlight. His weathered face should show deep wrinkles and laugh lines, with kind, wise eyes that crinkle at the corners. He's wearing traditional maroon and saffron robes with intricate golden embroidery visible on the collar. His head is shaved, and he has a few age spots on his scalp. The monk is sitting in front of a stone wall covered in colorful prayer flags fluttering in a gentle breeze. In the background, slightly out of focus, you can see snow-capped Himalayan peaks. The lighting should be warm and soft, creating gentle shadows that accentuate the textures of his skin and robes. Capture the scene with a shallow depth of field, as if shot with a high-end DSLR camera using a 85mm lens at f/2.8."
application_id = os.getenv("DISCORD_APPLICATION_ID")
guild_id = os.getenv("DISCORD_GUILD_ID")
channel_id = os.getenv("DISCORD_CHANNEL_ID")
version = os.getenv("DISCORD_VERSION")
id = os.getenv("DISCORD_ID")
authorization = os.getenv("DISCORD_BOT_TOKEN")
self_authorization = os.getenv("DISCORD_AUTHORIZATION_TOKEN")

class MidjourneyApi():
    def __init__(self, prompt, application_id, guild_id, channel_id, version, id, self_authorization):
        self.prompt = prompt
        self.application_id = application_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.id = id
        self.self_authorization = self_authorization
        self.message_id = ""
        self.custom_id = ""
        self.image_path_str = ""
        self.send_message()
        self.find_upgrade_button()
        self.upgrade_image()
        self.download_image()

    def send_message(self):
        url = "https://discord.com/api/v9/interactions"

        payload = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "session_id": "cannot be empty",
            "data": {
                "version": self.version,
                "id": self.id,
                "name": "imagine",
                "type": 1,
                "options": [
                    {
                        "type": 3,
                        "name": "prompt",
                        "value": prompt
                    }
                ],
                "application_command": {
                    "id": self.id,
                    "type": 1,
                    "application_id": self.application_id,
                    "version": self.version,
                    "name": "imagine",
                    "description": "Create images with Midjourney",
                    "options": [
                        {
                            "type": 3,
                            "name": "prompt",
                            "description": "The prompt to imagine",
                            "required": True,
                            "description_localized": "The prompt to imagine",
                            "name_localized": "prompt"
                        }
                    ],
                    "dm_permission": True,
                    "contexts": [0, 1, 2],
                    "integration_types": [0, 1],
                    "global_popularity_rank": 1,
                    "description_localized": "Create images with Midjourney",
                    "name_localized": "imagine"
                },
                "attachments": []
            },
            "nonce": "1318319344899325952",
            "analytics_location": "slash_ui"
        }

        headers = {
            'Authorization': self.self_authorization,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, json=payload)

        if response.status_code == 204:
            print("Command sent successfully, Waiting for response...")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            print(response.json())

    def find_upgrade_button(self):
        headers = {
            'Authorization': self.self_authorization,
            "Content-Type": "application/json",
        }
        for i in range(3):
            time.sleep(30)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                components = messages[0]['components'][0]['components']
                buttons = [comp for comp in components if comp.get('label') in ['U1', 'U2', 'U3', 'U4']]
                custom_ids = [button['custom_id'] for button in buttons]
                random_custom_id = random.choice(custom_ids)
                self.custom_id = random_custom_id
                print("Custom ID found. Upgrading image...")
                break
            except:
                ValueError("Timeout")
    
    def upgrade_image(self):
        url = "https://discord.com/api/v9/interactions"
        headers = {
            "Authorization": self.self_authorization,
            "Content-Type": "application/json",
        }
        data = {
            "type": 3,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_flags": 0,
            "message_id": self.message_id,
            "application_id": self.application_id,
            "session_id": "cannot be empty",
            "data": {
                "component_type": 2,
                "custom_id": self.custom_id,
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 204:
            print("Image upgraded successfully. Waiting for download...")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            print(response.json())
    
    def download_image(self):
        headers = {
            'Authorization': self.self_authorization,
            "Content-Type": "application/json",
        }
        for i in range(3):
            time.sleep(30)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                image_url = messages[0]['attachments'][0]['url'] 
                image_response = requests.get(image_url)
                a = urlparse(image_url)
                image_name = os.path.basename(a.path)
                self.image_path_str = f"images/{image_name}"
                with open(f"images/{image_name}", "wb") as file:
                    file.write(image_response.content)
                print("Image downloaded successfully.")
                break
            except:
                raise ValueError("Timeout")


def fetch_latest_messages(channel_id: str, token: str) -> List[Dict[str, Any]]:
    """
    Fetches the latest messages from a specified Discord channel.

    Args:
        channel_id (str): The ID of the Discord channel.
        token (str): The authorization token for the Discord bot.

    Returns:
        List[Dict[str, Any]]: A list of messages from the Discord channel.
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.json())
        print(f"Error fetching messages: {response.status_code}")
        return []


def post_message(channel_id: str, token: str, message: str) -> None:
    """
    Posts a message to a specified Discord channel.

    Args:
        channel_id (str): The ID of the Discord channel.
        token (str): The authorization token for the Discord bot.
        message (str): The message content to post.

    Returns:
        None
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    data: Dict[str, Any] = {
        "content": message,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message posted successfully.")
    else:
        print(response.json())
        print(f"Error posting message: {response.status_code}")
