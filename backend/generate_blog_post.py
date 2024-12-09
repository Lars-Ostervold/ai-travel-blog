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

#Failure email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
client = OpenAI() #API key is stored in .env file

supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)


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
    message["Subject"] = "DALL-E Image Generation Failure"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"The following prompt failed 5 times: {prompt}"
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

    chatbot_role_prompt = f"You are a travel blogger writing about the best places to visit in {destination}."
    chatbot_user_prompt = f"What are some of the best places to visit in {destination}?"

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
    chatbot_role_prompt = f"You are a clever, witty writer whose job is to come up with catchy titles for travel blog posts."
    chatbot_user_prompt = f"Generate a catchy title for the blog post below: \n \n {blog_post}"

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
    chatbot_role_prompt = f"You are an expert prompt engineer that generates prompts for DALLE that will generate images for travel blogs. Every image you generate must be relevant to the blog post and should look like a high quality photograph."
    chatbot_user_prompt = f"Generate only 4 image prompts relevant to this blog post below \n \n {blog_post}. Try to focus on unique details from the post so each image is of a different topic. Prompt should begin with 'Photograph of', and end by specifying things like the camera model, aperture, shutter speed, ISO, camera mode, focus mode, white balance, and metering mode. An example is 'fast motion, sunlight, shot with 4k HD DSLR Nikon photography' Separate each prompt with a new line. Individual prompts should be no more than 50 words. DO NOT GENERATE MORE THAN 4 PROMPTS"

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


def image_generation(prompts: List[str], blog_title: str, blog_post: str, blog_post_id: int) -> List[str]:
    """
    Generates images based on the prompts

    Args:
        prompts (List[str]): List of image prompts
        blog_title (str): The title of the blog post
        blog_post (str): The content of the blog post
        blog_post_id (int): The ID of the blog post

    Returns:
        List[str]: List of generated image URLs
    """
    max_attempts = 5

    try:
        image_urls = []
        for index, prompt in enumerate(prompts):
            success = False

            # Sometimes the prompt gets flagged as 'inappropriate', so we catch this in a loop and give a few tries
            for image_attempt in range(max_attempts):
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1792x1024",
                        quality="hd",
                        style="vivid",
                        n=1,
                    )
                    image_url = response.data[0].url
                    
                    # Save the image to Supabase
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        #store in temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                            temp_file.write(image_response.content)
                            temp_file_path = temp_file.name
                        
                        # Upload to Supabase
                        image_name = f"image_{blog_post_id}_{index}.png"
                        supabase_image_url = upload_image_to_supabase(temp_file_path, image_name)
                        image_urls.append(supabase_image_url)

                    success = True
                    break #If reaches this point, we successfully uploaded the image so we can break out of the loop
                except Exception as e:
                    print(f"Image generation attempt {image_attempt + 1} failed: {e}. Resubmitting prompt.")
            if not success:
                raise Exception(f"Failed to generate image for prompt: {prompt}")
        return image_urls
    except Exception as e:
        print(f"Prompt generation failed: {e}")
        failure_email_content = f"The following prompt failed 5 times: \n\n TILE: {blog_title} \n\n POST: \n {blog_post}\n\nPrompts: {prompts}"
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


# ---Execution--#
print("Generating blog post...")
blog_post = text_generation()
print("Generating blog title...")
blog_title = generate_blog_title(blog_post)
print("Generating image prompts...")
prompts = generate_image_prompts_from_blog_post(blog_post)
print("Marking spots for images...")
marked_blog_post = mark_spots_for_images(blog_post, prompts)
print("Uploaded blog post to Supabase...")
blog_post_id = insert_blog_post(blog_title, marked_blog_post)
print("Generating images...")
image_urls = image_generation(prompts, blog_title, blog_post, blog_post_id)
print("Storing image URLs...")
store_image_urls(blog_post_id, image_urls)
print("Replacing image tags with URLs...")
final_blog_post = replace_image_tags_with_urls(marked_blog_post, image_urls)
print("Storing final blog post...")
upsert_blog_post(blog_post_id, final_blog_post)
print("Blog post generation complete!")
