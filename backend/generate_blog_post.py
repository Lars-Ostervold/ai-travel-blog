#Need a location selector, then can farm data on that location to help the blog post generation
#Ask to generate specific details - festivals, times of year, etc
#Ideally there is some way to go with trends on Google?

from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
from get_blog_topic import get_blog_topic
from supabase import create_client, Client
import tempfile
from datetime import datetime, timezone
from github import Github
import re

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
    message["Subject"] = "Travel Blog Image Generation Failure"
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

    chatbot_role_prompt = f"You are a fun-loving, adventurous girl (named Audrey, aged 30) with a young family - a husband (Noah, aged 31) and two boys aged 2 (Leo) and 5 (Max). You love to travel and share your experiences with others. Your writing style is engaging, humorous, and informative. You're not afraid to be honest about the challenges of traveling with kids, but you always find the silver lining. You're passionate about helping others have amazing travel experiences, and you're always willing to share tips and advice. Your goal is to inspire others to explore the world and create unforgettable memories with their loved ones."
    chatbot_user_prompt = f"""
    Write a SEO-optimized blog post about your recent trip to {destination}. The title should be h2 (##) and subtitles are h3 (###). 
    Share your experiences, the challenges you faced, and the highlights of your trip. Include tips and advice for other young families who are planning a similar trip. Your goal is to inspire others to explore the world and create unforgettable memories with their loved ones.
    Be sure to include personal anecdotes, helpful tips for travelers, and some humor. 
    To the best of your knowledge, be specific about the location and accurate. Do not hallucinate places or activities that do not exist at or near {destination}.
    
    Here are some questions to consider, but be slightly random in the structure of the blog post to keep subsequent blog posts unique:

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

def clean_lead_and_trail_special_characters(title: str) -> str:
    """
    Removes any leading or trailing special characters from the title.

    Args:
        title (str): The title to clean

    Returns:
        str: The cleaned title
    """
    # Define the pattern to match leading or trailing special characters
    pattern = r'^[^\w]+|[^\w!]+$'
    # Use re.sub to replace the matched patterns with an empty string
    cleaned_string = re.sub(pattern, '', title)
    return cleaned_string


def generate_blog_title(blog_post: str) -> str:
    """
    Given a blog post, uses ChatGPT to generate a title.
    Remove any special characters from the title before returning.

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

    # Remove any leading or trailing special characters from the title. Characters include #, *, and other non-alphanumeric characters
    title = completion.choices[0].message.content
    title = clean_lead_and_trail_special_characters(title)

    return title.strip()


def generate_image_prompts_from_blog_post(blog_post: str) -> List[str]:
    """
    Generates image prompts based on the blog post. Number of prompts is limited to 4 by specifying in the chatbot prompt.

    Args:
        blog_post (str): The blog post content

    Returns:
        List[str]: List of generated image prompts
    """
    chatbot_role_prompt = f"""You are an expert travel photographer and AI image prompt engineer. 
    Your task is to create detailed, vivid prompts to that capture the essence of travel destinations and experiences.
    When given a blog post about a trip, you will generate a comprehensive image prompt to produce photographs from AI image generators.
    Do not use full sentences in natural language, but include main elements and details.
    Prompts should be 60-80 words each.
    Here is the formula for creating image prompts from blog posts:
        "[PHOTOGRAPHY TYPE]" + [SUBJECT/ACTION] + [SHOT TYPE] + [LOCATION/SETTING] + [CAMERA SETTINGS] + [EMOTION] + [LIGHTING].
        


    A good example of a prompt follows. Feel free to adjust the style as necessary.: 
    Landscape photography of wild horses grazing near the Dungeness Ruins, wide-angle shot capturing the contrast of the crumbling stone walls and the vibrant green grass of Cumberland Island. Shot on a Nikon Z7 II with a 24-70mm f/2.8 lens. The image evokes serenity and wonder, with golden hour lighting casting long, soft shadows and illuminating the horses’ coats with a warm, golden glow
        """    
    chatbot_user_prompt = f"""
    Generate only 4 image prompts for Midjourney, relevant to this blog post below.
    Space out the images throughout the post, focusing on unique details from the post so each image is of a different topic. 
    Each prompt should be separated with a new line and nothing else. 
    Your response should only include the prompts, separated by new lines. No other words in your response.
    DO NOT GENERATE MORE THAN 4 PROMPTS
    
    Focus on elements from the post that do not include the main characters (Audrey, Noah, Max, Leo).
    Rarely include prompts of the main character. Usually zero prompts should include the Audrey, Max, Leo, or Noah, sparingly, a maximum of one prompt.

    If you generate images of Audrey, Max, Leo, or Noah, here are special instructions you must follow. Ignore these if you do not generate images of the main characters:
    - Only one main character should be in focus in the image. There should be no other people in the foreground.
    - ALWAYS include the BOTH the age AND name of the character (e.g., "Audrey (a woman in her 30s)"). For your reference, Audrey is a mother in her early 30s, Noah is a father in his early 30s, Max is a 5-year old boy toddler, and Leo is a 2-year old boy. 

    BLOG POST:\n \n "{blog_post}". 
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

    #Strip any empty prompts
    prompts = [prompt.strip() for prompt in prompts if prompt.strip()]

    #Add character references and aspect ratio to the prompts
    modified_prompts = []
    for prompt in prompts:
        #aspect ratio
        prompt += " --ar 2:3 --q 2"
        if "AUDREY" in prompt.upper() or "NOAH" in prompt.upper() or "MAX" in prompt.upper() or "LEO" in prompt.upper():
            prompt += " --cref "
        if "AUDREY" in prompt.upper():
            prompt += "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/character-reference/audrey_avatar.png?t=2024-12-20T13%3A20%3A50.930Z "
        if "NOAH" in prompt.upper():
            prompt += "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/character-reference/noah_avatar.png?t=2024-12-20T13%3A21%3A12.678Z "
        if "MAX" in prompt.upper():
            prompt += "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/character-reference/max_avatar.png?t=2024-12-20T13%3A21%3A06.428Z "
        if "LEO" in prompt.upper():
            prompt += "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/character-reference/leo_avatar.png?t=2024-12-20T13%3A20%3A59.162Z "
        modified_prompts.append(prompt.strip())
    return [prompt for prompt in modified_prompts if prompt]

def generate_alt_text_from_prompts(prompts: List[str]) -> List[str]:
    """
    Generates alt text for images based on the prompts

    Args:
        prompts (List[str]): List of image prompts

    Returns:
        List[str]: List of generated alt texts
    """

    alt_texts = []
    for prompt in prompts:
        chatbot_user_prompt = f"Generate alt text for an image from the image prompt below. Respond only with the alt text, nothing else. \n\n {prompt}"

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": chatbot_user_prompt},
            ]
        )

        alt_text = completion.choices[0].message.content
        alt_texts.append(alt_text)
    return alt_texts

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


def store_image_urls(blog_post_id: int, image_urls: List[str], alt_texts: List[str]) -> None:
    """
    Stores the image URLs in the Supabase database

    Args:
        blog_post_id (int): The ID of the blog post
        image_urls (List[str]): List of image URLs
        alt_texts (List[str]): List of alt texts for the images

    Returns:
        None
    """
    for i, image_url in enumerate(image_urls):
        try:
            response = supabase.table("blog_images").insert({"blog_post_id": blog_post_id, "image_url": image_url, "image_number": i+1, "alt_text": alt_texts[i]}).execute()
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
            #Posts message between photo generation calls so we don't download an old image
            midjourney.post_message("Woo great image! Thanks for your help! I'll be back for more soon!")

            #store in temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(midjourney_photo)
                temp_file_path = temp_file.name
            
            # Upload to Supabase
            image_name = f"image_{blog_post_id}_{index}.png"
            supabase_image_url = upload_image_to_supabase(temp_file_path, image_name)
            image_urls.append(supabase_image_url)

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

    chatbot_user_prompt = f"""Given the prompts and blog post below, mark the spots in the blog post where images should be placed. 
    Given the prompt number, mark the locations with [Image 1], [Image 2], [Image 3], [Image 4]. Make sure you mark a spot for all four images. They do not have to be in order, but do not repeat images. 
    Do not change any other text other than to add the image tags. Only respond with the updated blog post. \n\n PROMPTS: \n {numbered_prompts_str} \n\n BLOG POST: \n {blog_post}"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": chatbot_user_prompt}
        ]
    )

    marked_blog_post = completion.choices[0].message.content

    return marked_blog_post


def replace_image_tags_with_urls(blog_post: str, image_urls: List[str], alt_texts: List[str]) -> str:
    """
    Assumes the blog post has already been marked with "[Image X]".
    Replaces image tags in the blog post with image URLs.

    Args:
        blog_post (str): The blog post content
        image_urls (List[str]): List of image URLs
        alt_texts (List[str]): List of alt texts for the images

    Returns:
        str: The blog post with image URLs
    """
    for index, image_url in enumerate(image_urls):
        image_tag = f"[Image {index + 1}]"
        blog_post = blog_post.replace(image_tag, f"![{alt_texts[index]}]({image_url})")

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

def get_clean_excerpt(blog_post: str) -> str:
    """
    Gets a clean excerpt from a blog post. The excerpt is the first 200 characters of the blog post.
    However, we want to remove any leading or trailing characters and end at the end of a sentence.

    Args:
        blog_post (str): The blog post content

    Returns:
        str: The excerpt of the blog post
    """
    # Get the first 200 characters of the blog post
    excerpt = blog_post[:200]

    # Remove any leading or trailing special characters
    cleaned_excerpt = clean_lead_and_trail_special_characters(excerpt)

    #Find positions of all sentence-ending characters
    sentence_end_positions = [pos for pos, char in enumerate(cleaned_excerpt) if char in ".!?"]

    end_of_sentence_exists = False
    last_valid_end = None

    # Loop through sentence-ending positions
    for pos in reversed(sentence_end_positions):
        # Check if pos + 2 is a valid uppercase letter (indicating a new sentence)
        if pos + 2 < len(cleaned_excerpt) and cleaned_excerpt[pos + 2].isupper():
            end_of_sentence_exists = True
            last_valid_end = pos
            break

    # If a valid sentence-ending position is found, return up to that point
    if end_of_sentence_exists and last_valid_end is not None:
        return cleaned_excerpt[:last_valid_end + 1]

    # If no valid sentence end is found, find the last space and return up to that point
    last_space = cleaned_excerpt.rfind(" ")
    if last_space != -1:
        return cleaned_excerpt[:last_space]

    # If no spaces are found, return the cleaned excerpt
    return cleaned_excerpt

def generate_keywords_from_blog_post(blog_post: str) -> str:
    """
    Generates keywords from a blog post using ChatGPT

    Args:
        blog_post (str): The blog post content

    Returns:
        str: Comma-separated list of keywords. Appropriate format for meta keywords.
    """
    chatbot_role_prompt = f"""You are an SEO expert tasked with generating keywords for a travel blog post. Your goal is to identify the most relevant and high-impact keywords that will help the blog post rank well in search engine results. 
    When generating keywords, consider the following guidelines:
    - Focus on long-tail keywords that are specific to the content of the blog post.
    - Include a mix of informational, navigational, and transactional keywords.
    - Use synonyms and related terms to capture a broad range of search queries.
    - Consider the target audience and their search intent.
    - Aim for a balance of high-volume and low-competition keywords.
    - Avoid keyword stuffing and prioritize natural language.
    """
    chatbot_user_prompt = f"""
    Generate keywords for the blog post below. The keywords should be relevant to the content and help improve the SEO of the post. 
    Respond with only the keywords, separated by commas and no period at the end. The format should be appropriate to use as meta keywords.
    \n \n {blog_post}
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": chatbot_role_prompt},
            {"role": "user", "content": chatbot_user_prompt},
        ]
    )

    return completion.choices[0].message.content

def generate_pinterest_board_names(blog_post: str) -> str:
    """
    Generates Pinterest board names based on the blog post content
    
    Args:
        blog_post (str): The blog post content
    
    Returns:
        List[str]: List of generated Pinterest board names
    """
    chatbot_role_prompt = f"You are a Pinterest SEO expert helping me come up with Pinterest Boards to post my blog post on. Your goal is to identify the most relevant and high-impact Board names that will help the blog post rank well in search results."
    chatbot_user_prompt = f"""
    Generate four names for Boards for the blog post below. The Board names should be relevant to the post and help improve SEO for Pinterest. Use two specific board names and two general board names. Keep the board names succinct. Respond with only the Board names, no quotes, separated by commas, and no period at the end. 
    \n \n {blog_post}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": chatbot_role_prompt},
            {"role": "user", "content": chatbot_user_prompt},
        ]
    )

    return completion.choices[0].message.content

def add_metadata_to_blog_post(blog_title: str, blog_post: str, image_urls: List[str], blog_post_id: int, keywords: str, pinterest_boards: str, date_time: str = get_current_datetime_iso8601(),  blogger_name: str = "Audrey Rose", avatar_url: str = "https://nxvznoqipejdootcntuo.supabase.co/storage/v1/object/public/character-reference/audrey_avatar_square.png?t=2024-12-21T13%3A26%3A30.307Z") -> str:
    """
    Adds metadata to the blog post

    Args:
        

    Returns:
        dict: The metadata dictionary
    """
    metadata = f"""---
title: "{blog_title}"
excerpt: "{get_clean_excerpt(blog_post)}"
keywords: "{keywords}"
pinterestBoards: "{pinterest_boards}"
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

    # Upload metadata to Supabase
    metadata_dict = {
        "id": blog_post_id,
        "excerpt": get_clean_excerpt(blog_post),
        "keywords": keywords,
        "pinterest_boards": pinterest_boards,
        "cover_image": image_urls[0],
        "date_of_post": date_time,
        "author_name": blogger_name,
        "author_picture": avatar_url,
        "og_image": image_urls[0]
    }
    try:
        response = supabase.table("blog_posts").upsert(metadata_dict).execute()
    except Exception as e:
        print(f"Failed to store metadata: {e}")


    return metadata + "\n\n" + blog_post

def main():
    print("Generating blog post...")
    blog_post = text_generation()

    print("Generating blog title...")
    blog_title = generate_blog_title(blog_post)

    print("replacing apostrophes...")
    blog_post = blog_post.replace("’", "'")
    blog_title = blog_title.replace("’", "'")

    print("Generating image prompts...")
    prompts = generate_image_prompts_from_blog_post(blog_post)

    print("Generating alt text for images...")
    alt_texts = generate_alt_text_from_prompts(prompts)

    print("Marking spots for images...")
    marked_blog_post = mark_spots_for_images(blog_post, prompts)

    print("Uploaded blog post to Supabase...")
    blog_post_id = insert_blog_post(blog_title, marked_blog_post)

    print("Generating images...")
    image_urls = generate_and_store_images(prompts, blog_title, marked_blog_post, blog_post_id)

    print("Storing image URLs...")
    store_image_urls(blog_post_id, image_urls, alt_texts)

    print("Replacing image tags with URLs...")
    final_blog_post = replace_image_tags_with_urls(marked_blog_post, image_urls, alt_texts)

    print("Generating keywords from blog post...")
    keywords = generate_keywords_from_blog_post(blog_post)

    print("Generating Pinterest board names...")
    pinterest_boards = generate_pinterest_board_names(blog_post)

    print("Adding metadata to blog post...")
    blog_post_plus_metadata = add_metadata_to_blog_post(blog_title, final_blog_post, image_urls, blog_post_id, keywords, pinterest_boards)

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

if __name__ == "__main__":
    main()