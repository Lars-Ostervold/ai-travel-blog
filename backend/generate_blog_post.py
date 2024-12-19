#Need a location selector, then can farm data on that location to help the blog post generation
#Ask to generate specific details - festivals, times of year, etc
#Ideally there is some way to go with trends on Google?

from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
from get_blog_topic import get_blog_topic
from supabase import create_client, Client
import requests
import tempfile
from datetime import datetime, timezone
from github import Github
import time

#Failure email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
client = OpenAI() #API key is stored in .env file

supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

#Midjourney API
from midjourney_bot import MidjourneyApi
application_id = os.getenv("DISCORD_APPLICATION_ID")
guild_id = os.getenv("DISCORD_GUILD_ID")
channel_id = os.getenv("DISCORD_CHANNEL_ID")
version = os.getenv("DISCORD_VERSION")
id = os.getenv("DISCORD_ID")
authorization = os.getenv("DISCORD_BOT_TOKEN")
self_authorization = os.getenv("DISCORD_AUTHORIZATION_TOKEN")


def send_failure_email(prompt: str) -> None:
    """
    Sends an email to the user with the prompt that failed

    Args:
        prompt (str): The prompt that failed
    
    Raises:
        smtplib.SMTPException: If there is an error sending the email

    Returns:
        None
    """
    
    s = smtplib.SMTP(os.getenv("EMAIL_HOST"), os.getenv("EMAIL_PORT"))
    s.starttls()

    s.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
    
    sender_email = os.getenv("EMAIL_USER")
    receiver_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Tralel Blog Image Generation Failure"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"The following prompt failed: {prompt}"
    part = MIMEText(text, "plain")
    message.attach(part)

    s.sendmail(sender_email, receiver_email, message.as_string())

    s.quit()


def text_generation() -> str:
    """
    Generates a blog post using OpenAI chat model. Gets topic for blog post from get_blog_topic.py

    Returns:
        str: The generated blog post
    """
    destination = get_blog_topic()

    chatbot_role_prompt = f"You are a fun-loving, adventurous girl (named Audrey Rose) in your 20s with a young family - a husband (Noah) in his 20s, and two boys aged 2 (Leo) and 5 (Max). You love to travel and share your experiences with others. Your writing style is engaging, humorous, and informative. You're not afraid to be honest about the challenges of traveling with kids, but you always find the silver lining. You're passionate about helping others have amazing travel experiences, and you're always willing to share tips and advice. Your goal is to inspire others to explore the world and create unforgettable memories with their loved ones."
    chatbot_user_prompt = f"""
    Write a SEO-optimized blog post about your recent trip to {destination}. 
    Share your experiences, the challenges you faced, and the highlights of your trip. Include tips and advice for other young families who are planning a similar trip. Your goal is to inspire others to explore the world and create unforgettable memories with their loved ones.
    Be sure to include personal anecdotes, helpful tips for travelers, and some humor. 
    To the best of your knowledge, be specific about the location and accurate. Do not include any information that is not true or that you are unsure of.
    
    Here are some questions to consider:

    What were the highlights of your trip?
    What were some of the challenges you faced?
    What are your top recommendations for things to see and do?
    What are some tips for traveling to [Destination] with kids?
    What are some budget-friendly activities and attractions?
    What are some must-try local foods?
    What are some cultural customs or etiquette tips to keep in mind?
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": chatbot_role_prompt},
            {"role": "user", "content": chatbot_user_prompt},
        ]
    )

    return completion.choices[0].message.content


def generate_blog_title(blog_post: str) -> str:
    """
    Given a blog post, uses ChatGPT to generate a title.

    Args:
        blog_post (str): The blog post content

    Returns:
        str: The generated blog title
    """
    chatbot_role_prompt = f"You are a clever, witty writer whose job is to come up with catchy titles for travel blog posts. You prioritize SEO."
    chatbot_user_prompt = f"Generate an catchy title that is SEO for the blog post below: \n \n {blog_post}"

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": chatbot_role_prompt},
            {"role": "user", "content": chatbot_user_prompt},
        ]
    )

    return completion.choices[0].message.content


def generate_image_prompts_from_blog_post(blog_post: str) -> List[str]:
    """
    Generates image prompts based on the blog post. Number of prompts is limited to 4 by specifying in the chatbot prompt.

    Args:
        blog_post (str): The blog post content

    Returns:
        List[str]: List of generated image prompts
    """
    chatbot_role_prompt = f"""You are an expert visual artist and professional photographer with a keen eye for detail and composition. Your task is to create detailed, vivid image prompts that could be used by AI image generators to produce photorealistic images. When crafting these prompts, follow these guidelines:
        Begin with a clear, concise description of the main subject.  
        Specify the type of shot (e.g., close-up, wide-angle, aerial) and perspective.
        Describe the lighting conditions in detail, including direction, quality, and color temperature.
        Include information about the setting or background, providing context and depth.
        Mention specific textures, materials, and colors where relevant.
        Reference photographic techniques like depth of field, focus points, or motion blur when appropriate.
        Suggest camera settings (e.g., lens type, aperture) to achieve the desired effect.
        Include atmospheric elements like weather conditions or time of day.   

        A good example of a prompt is: A close-up portrait of an elderly Tibetan monk in natural sunlight. His weathered face should show deep wrinkles and laugh lines, with kind, wise eyes that crinkle at the corners. He's wearing traditional maroon and saffron robes with intricate golden embroidery visible on the collar. His head is shaved, and he has a few age spots on his scalp. The monk is sitting in front of a stone wall covered in colorful prayer flags fluttering in a gentle breeze. In the background, slightly out of focus, you can see snow-capped Himalayan peaks. The lighting should be warm and soft, creating gentle shadows that accentuate the textures of his skin and robes. Capture the scene with a shallow depth of field, as if shot with a high-end DSLR camera using a 85mm lens at f/2.8.
        """    
    chatbot_user_prompt = f"""
    Generate only 4 image prompts relevant to this blog post below. Try to space out the images throughout the post. Try to focus on unique details from the post so each image is of a different topic. 
    Separate each prompt with a new line. DO NOT GENERATE MORE THAN 4 PROMPTS
    Only one image prompt should be of the main characters in the blog post.
    
    
    When generating images of the main characters, use these details in your prompts:

    Audrey (the narrator):
        Hair: Long, light brown with soft waves, often tied back in a casual ponytail or messy bun.
        Eyes: Warm hazel with a hint of green.
        Skin: Fair with a light tan from outdoor adventures.
        Build: Medium height, fit but with a relaxed, approachable appearance.
        Style: Practical yet stylish, often wearing flowy tops, comfortable jeans, and sneakers.
    
    Noah (husband):
        Hair: Short, dark brown, slightly tousled.
        Eyes: Deep blue, kind and expressive.
        Skin: Light olive complexion with a touch of sun-kissed glow.
        Build: Tall and lean, with broad shoulders and an athletic frame.
        Style: Casual, often seen in neutral-colored T-shirts, cargo shorts, and hiking boots.

    Max (5-year-old male):
        Hair: Sandy blond, slightly messy and windswept.
        Eyes: Bright blue, full of curiosity and mischief.
        Skin: Fair with a few light freckles across his nose.
        Build: Small and energetic, always on the move.
        Style: Bright-colored T-shirts with fun graphics, shorts, and sporty sneakers.

    Leo (2-year-old male toddler):
        Hair: Light brown, soft and slightly curly.
        Eyes: Big and brown, with a curious, innocent expression.
        Skin: Rosy cheeks and a fair complexion.
        Build: Chubby-cheeked toddler with a sturdy little frame.
        Style: Overalls or comfy rompers, often in earthy tones or playful patterns.
    
    \n \n {blog_post}. 
    "
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": chatbot_role_prompt},
            {"role": "user", "content": chatbot_user_prompt},
        ]
    )

    # We asked GPT to separate the prompts with a new line, so we split the response by new lines
    prompts = completion.choices[0].message.content.split("\n")
    return [prompt.strip() for prompt in prompts if prompt.strip()]


def insert_blog_post(title: str, content: str) -> int:
    """
    Inserts a blog post into the Supabase database

    Args:
        title (str): The title of the blog post
        content (str): The content of the blog post

    Returns:
        int: The ID of the inserted blog post
    """
    response = supabase.table("blog_posts").insert({"title": title, "content": content}).execute()
    return response.data[0]["id"]


def upload_image_to_supabase(image_path: str, image_name: str) -> Optional[str]:
    """
    Uploads an image to Supabase storage

    Args:
        image_path (str): The path to the image file to be uploaded
        image_name (str): What the image should be named in Supabase storage

    Returns:
        Optional[str]: The URL of the uploaded image, or None if upload fails
    """
    with open(image_path, "rb") as image_file:
        try:
            response = supabase.storage.from_("travel-blog-images").upload(image_name, image_file)
            return f"{supabase_url}/storage/v1/object/public/travel-blog-images/{image_name}"
        except Exception as e:
            print(f"Failed to upload image: {e}")


def store_image_urls(blog_post_id: int, image_urls: List[str]) -> None:
    """
    Stores the image URLs in the Supabase database

    Args:
        blog_post_id (int): The ID of the blog post
        image_urls (List[str]): List of image URLs

    Returns:
        None
    """
    for i, image_url in enumerate(image_urls):
        try:
            response = supabase.table("blog_images").insert({"blog_post_id": blog_post_id, "image_url": image_url, "image_number": i+1}).execute()
        except Exception as e:
            print(f"Failed to store image URL: {e}")


def generate_and_store_images(prompts: List[str], blog_title: str, marked_blog_post: str, blog_post_id: int) -> List[str]:
    """
    Generates images and uploads to Supabase storage based on the prompts

    Args:
        prompts (List[str]): List of image prompts
        blog_title (str): The title of the blog post
        blog_post (str): The content of the blog post
        blog_post_id (int): The ID of the blog post

    Returns:
        List[str]: List of generated image URLs
    """
    try:
        image_urls = []
        for index, prompt in enumerate(prompts):

            midjourney = MidjourneyApi(prompt, application_id, guild_id, channel_id, version, id, self_authorization)
            midjourney.send_imagine_prompt()
            midjourney.find_upgrade_button()
            midjourney.upgrade_image()
            midjourney_photo = midjourney.download_image()

            #store in temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(midjourney_photo)
                temp_file_path = temp_file.name
            
            # Upload to Supabase
            image_name = f"image_{blog_post_id}_{index}.png"
            supabase_image_url = upload_image_to_supabase(temp_file_path, image_name)
            image_urls.append(supabase_image_url)

            # #The second API request doesn't show up if we send too fast.
            # print("Waiting before submitting new API request.")
            # time.sleep(300)
        return image_urls
    except Exception as e:
        print(f"Prompt generation failed: {e}")
        failure_email_content = f"The following prompt failed: \n\n TILE: {blog_title} \n\n POST: \n {marked_blog_post}\n\nPrompts: {prompts}"
        send_failure_email(failure_email_content)
        raise


def number_prompts_into_single_string(prompts: List[str]) -> str:
    """
    We want to give all the prompts to ChatGPT at the same time, so this function takes
    the list of prompts and puts them in a single string, numerically separated.

    Args:
        prompts (List[str]): List of prompts

    Returns:
        str: Numbered prompts as a single string
    """
    # Check if the prompts are already numbered
    is_numbered = all(prompt.startswith(f"{i+1}.") for i, prompt in enumerate(prompts) if prompt.strip())

    if is_numbered:
        numbered_prompts_str = "\n".join(prompts)
    else:
        # Number the prompts
        numbered_prompts = [f"{i+1}. {prompt}" for i, prompt in enumerate(prompts) if prompt.strip()]

        # Join the numbered prompts into a single string
        numbered_prompts_str = "\n".join(numbered_prompts)

    return numbered_prompts_str


def mark_spots_for_images(blog_post: str, prompts: List[str]) -> str:
    """
    Uses ChatGPT to marks spots in the blog post where images should be placed.
    Tries to match the prompt to the most logical spot in the blog post.

    Args:
        blog_post (str): The blog post content
        prompts (List[str]): List of prompts

    Returns:
        str: The marked blog post with image tags
    """
    # This function will take the blog post and mark spots where images should be placed. 
    # This will be used to generate the final blog post with images.

    # Number the prompts
    numbered_prompts_str = number_prompts_into_single_string(prompts)

    chatbot_user_prompt = f"Given the prompts below, mark the spots in the blog post where images should be placed. Given the prompt number, mark the locations with [Image 1], [Image 2], etc. They do not have to be in order. Do not change any other text other than to add the image tags. \n\n PROMPTS: \n {numbered_prompts_str} \n\n BLOG POST: \n {blog_post}"

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": chatbot_user_prompt}
        ]
    )

    marked_blog_post = completion.choices[0].message.content

    return marked_blog_post


def replace_image_tags_with_urls(blog_post: str, image_urls: List[str]) -> str:
    """
    Assumes the blog post has already been marked with "[Image X]".
    Replaces image tags in the blog post with image URLs.

    Args:
        blog_post (str): The blog post content
        image_urls (List[str]): List of image URLs

    Returns:
        str: The blog post with image URLs
    """
    for index, image_url in enumerate(image_urls):
        image_tag = f"[Image {index + 1}]"
        blog_post = blog_post.replace(image_tag, f"![Image {index + 1}]({image_url})")

    return blog_post


def upsert_blog_post(blog_id: int, content: str) -> None:
    """
    Upserts a blog post into the Supabase database

    Args:
        blog_id (int): The ID of the blog post
        content (str): The content of the blog post

    Returns:
        None
    """
    supabase.table("blog_posts").upsert({"id": blog_id, "content": content}).execute()

def upload_blog_post_to_github(content_string: str, token: str, repo_name: str, upload_path: str, branch: str = "main", commit_message: str = "automated commit") -> None:
    """
    Uploads a blog post to a GitHub repository. Assumes blog post is markdown format stored in a string.

    Args:
        token (str): The GitHub token
        repo_name (str): The name of the repository
        upload_path (str): The path to upload the file to
        branch (str): The branch to upload to
        commit_message (str): The commit message
        content_string (str): The content of the file
    
    Returns:
        None
    """
    # Authenticate with GitHub
    g = Github(token)
    repo = g.get_repo(repo_name)

    
    try:
        # Check if the file already exists
        file = repo.get_contents(upload_path, ref=branch)

        # Update the existing file
        repo.update_file(
            path=file.path,
            message=commit_message,
            content=content_string,
            sha=file.sha,
            branch=branch
        )
        print(f"Updated file at {upload_path}")
    except:
        print(f"path not found: {upload_path}")
        # Create a new file
        repo.create_file(
            path=upload_path,
            message=commit_message,
            content=content_string,
            branch=branch
        )
        print(f"Created new file at {upload_path}")

def get_current_datetime_iso8601():
    # Get the current date and time in UTC
    now = datetime.now(timezone.utc)
    
    # Format the date and time as an ISO 8601 string with milliseconds
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return formatted_datetime

def get_specific_datetime_iso8601(year: int, month: int, day: int) -> str:
    # Create a specific date and time in UTC
    specific_datetime = datetime(year, month, day, tzinfo=timezone.utc)
    
    # Format the date and time as an ISO 8601 string with milliseconds
    formatted_datetime = specific_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return formatted_datetime

def add_metadata_to_blog_post(blog_title: str, blog_post: str, image_urls: List[str], blog_post_id: int, date_time: str = get_current_datetime_iso8601(),  blogger_name: str = "Audrey Rose", avatar_url: str = "https://i.pravatar.cc/100") -> str:
    """
    Adds metadata to the blog post

    Args:
        

    Returns:
        dict: The metadata dictionary
    """
    metadata = f"""---
title: "{blog_title}"
excerpt: "{blog_post[:200]}"
coverImage: "{image_urls[0]}"
date: "{date_time}"
author:
    name: "{blogger_name}"
    picture: "{avatar_url}"
ogImage:
    url: "{image_urls[0]}"
blogPostID: "{blog_post_id}"
---
    """

    return metadata + "\n\n" + blog_post

# ---Execution--#
print("Generating blog post...")
blog_post = text_generation()

print("Generating blog title...")
blog_title = generate_blog_title(blog_post)

print("replacing apostrophes...")
blog_post = blog_post.replace("’", "'")
blog_title = blog_title.replace("’", "'")

print("Generating image prompts...")
prompts = generate_image_prompts_from_blog_post(blog_post)

print("Marking spots for images...")
marked_blog_post = mark_spots_for_images(blog_post, prompts)

print("Uploaded blog post to Supabase...")
blog_post_id = insert_blog_post(blog_title, marked_blog_post)

print("Generating images...")
image_urls = generate_and_store_images(prompts, blog_title, marked_blog_post, blog_post_id)

print("Storing image URLs...")
store_image_urls(blog_post_id, image_urls)

print("Replacing image tags with URLs...")
final_blog_post = replace_image_tags_with_urls(marked_blog_post, image_urls)

print("Adding metadata to blog post...")
blog_post_plus_metadata = add_metadata_to_blog_post(blog_title, final_blog_post, image_urls, blog_post_id)

#Sometimes the LLM puts "BLOG_POST:" at the beginning
if "BLOG_POST:" in blog_post_plus_metadata:
    blog_post_plus_metadata = blog_post_plus_metadata.replace("BLOG_POST:", "")

print("Storing final blog post...")
upsert_blog_post(blog_post_id, blog_post_plus_metadata)

print("Blog post generation complete!")


print("Uploading blog post to GitHub...")
#GitHub Upload variables
GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN")
REPO_NAME: str = "Lars-Ostervold/ai-travel-blog"
UPLOAD_PATH: str = f"frontend/_posts/{blog_post_id}_blog.md"
BRANCH: str = "main"
COMMIT_MESSAGE: str = f"Automated commit: Uploaded new blog post number {blog_post_id}"
CONTENT_STRING: str = blog_post_plus_metadata


upload_blog_post_to_github(CONTENT_STRING, GITHUB_TOKEN, REPO_NAME, UPLOAD_PATH, BRANCH, COMMIT_MESSAGE, )
print("Blog post uploaded to GitHub!")