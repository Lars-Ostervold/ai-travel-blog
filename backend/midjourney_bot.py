##---Credit to yachty66 for the original code---##
##---https://github.com/yachty66/unofficial_midjourney_python_api--

import requests
import json
import discord
from discord.ext import commands


# Usage
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

intents = discord.Intents.default()
# intents.messages = True
# intents.guilds = True
# intents.message_content = True  # Enable reading message content

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready and listening for messages.")

    print("fetching messages....")

    # Fetch the target channel
    channel = bot.get_channel(channel_id)
    if not channel:
        print("Channel not found or bot lacks access to it.")
        return

    # Fetch messages
    async for message in channel.history(limit=50):  # Adjust limit as needed
        print(f"[{message.created_at}] {message.author}: {message.content}")
        if message.attachments:
            for attachment in message.attachments:
                print(f"Attachment: {attachment.url}")

    print("Closing bot.")
    # Disconnect after printing messages
    await bot.close()

@bot.event
async def on_message(message):
    # Avoid responding to the bot's own messages
    if message.author == bot.user:
        return

    # Print message details
    print(f"Message from {message.author}: {message.content}")

    # Check if the message contains an image from the bot (e.g., MidJourney)
    if message.author.bot and message.attachments:
        for attachment in message.attachments:
            if attachment.url.endswith((".png", ".jpg", ".jpeg")):  # Check for image file
                print(f"Image URL: {attachment.url}")
                # Optionally, download the image
                await download_image(attachment.url, "output_image.png")

async def download_image(url, filename):
    """Download an image from the given URL."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, "wb") as f:
                    f.write(await resp.read())
                print(f"Image saved as {filename}")
            else:
                print(f"Failed to download image: {resp.status}")


# midjourney = MidjourneyApi(prompt="prompt", application_id="application_id", guild_id="guild_id", channel_id="channel_id", version="version", id="id", authorization="authorization")

url = "https://discord.com/api/v9/interactions"

payload = {
    "type": 2,
    "application_id": application_id,
    "guild_id": guild_id,
    "channel_id": channel_id,
    "session_id": "fc2f6a8a3fa7d0e256f91f14147b5866",
    "data": {
        "version": version,
        "id": id,
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
            "id": id,
            "type": 1,
            "application_id": application_id,
            "version": version,
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

url_message = "https://discord.com/api/v9/channels/1317494443737219094/messages"
payload_normal_message = {
  "mobile_network_type": "unknown",
  "content": "what is happening",
  "flags": 0
}
header_message = {
    'Authorization': authorization,
    'Content-Type': 'application/json'
    }

headers = {
    'Authorization': authorization,
    'Content-Type': 'application/json'
}

# response = requests.request("POST", url_message, headers=header_message, json=payload_normal_message)
# print(response.text)
# print(response.json())

def fetch_latest_messages(channel_id, token):
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

# messages = fetch_latest_messages(channel_id, authorization)
# # print(messages)
# messages.reverse()
# for message in messages:
#     print(message["author"]["username"], message["content"])

# response = requests.request("POST", url, headers=headers, json=payload)



# if response.status_code == 204:
#     print("Command sent successfully, Waiting for response...")
# else:
#     print(f"Error: {response.status_code} - {response.text}")
#     print(response.json())

bot.run(authorization)