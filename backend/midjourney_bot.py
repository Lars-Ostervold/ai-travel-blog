##---Credit to yachty66 for the original code---##
##---https://github.com/yachty66/unofficial_midjourney_python_api

import requests
import json
import time
import random
from urllib.parse import urlparse
from typing import Any, Dict, List

import os

class MidjourneyApi():
    """
    A class to interact with the Midjourney API via Discord.
    Attributes:
    -----------
    prompt : str
        The prompt to generate an image.
    application_id : str
        The application ID for the Discord bot.
    guild_id : str
        The guild (server) ID where the bot is used.
    channel_id : str
        The channel ID where the bot sends messages.
    version : str
        The version of the application command.
    id : str
        The command ID.
    self_authorization : str
        The authorization token for the bot.
    message_id : str
        The ID of the message containing the image.
    custom_id : str
        The custom ID for the upgrade button.
    image_path_str : str
        The path to save the downloaded image.
    Methods:
    --------
    send_imagine_prompt():
        Sends a slash command in Discord channel to generate an image from Midjourney.
    find_upgrade_button():
        Finds the upgrade button in the most recent message.
    upgrade_image():
        Upgrades the generated image by interacting with the upgrade button.
    download_image():
        Downloads the upgraded image from the Discord channel.
    """
    def __init__(self, prompt: str, application_id: str, guild_id: str, channel_id: str, version: str, id: str, self_authorization: str) -> None:
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

    def send_imagine_prompt(self) -> None:
        """
        Sends a slash command to the Discord API to generate an image using Midjourney.

        This function constructs a payload with the necessary data to send a command
        to the Discord API to generate an image based on the provided prompt.

        Returns:
            None
        """
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
                        "value": self.prompt
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
            }
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

    def find_upgrade_button(self) -> None:
        """
        Finds the upgrade button in the most recent message.

        This function fetches the latest messages from the Discord channel and
        searches for the upgrade button in the most recent message. It then
        selects a random upgrade button to use for upgrading the image.

        Returns:
            None
        """
        headers = {
            'Authorization': self.self_authorization,
            "Content-Type": "application/json",
        }

        for i in range(3):
            print(f"Looking for upgrade button attempt {i+1}...")
            time.sleep(60)
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
                print("Custom ID for button found. Upgrading image...")
                break
            except:
                ValueError("Timeout")
    
    def upgrade_image(self) -> None:
        """
        Upgrades the generated image by interacting with the upgrade button.

        This function sends a request to the Discord API to interact with the
        upgrade button, which upgrades the generated image.

        Returns:
            None
        """
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
        print("Trying to send request to upgrade an image...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 204:
            print("Clicked on image upgrade. Waiting before download attempt...")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            print(response.json())
    
    def download_image(self) -> bytes:
        """
        Downloads the upgraded image from the Discord channel.

        This function fetches the latest messages from the Discord channel and
        downloads the image from the most recent message.

        Returns:
            bytes: The content of the downloaded image.
        """
        headers = {
            'Authorization': self.self_authorization,
            "Content-Type": "application/json",
        }
        for i in range(3):
            print(f"Waiting for image download attempt {i+1}...")
            time.sleep(60)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                image_url = messages[0]['attachments'][0]['url'] 
                image_response = requests.get(image_url)
                print("Image downloaded successfully.")
                return image_response.content
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
  "embeds": [{
    "title": "Hello, Embed!",
    "description": "This is an embedded message."
  }]
}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message posted successfully.")
    else:
        print(response.json())
        print(f"Error posting message: {response.status_code}")
