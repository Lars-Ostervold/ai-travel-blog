import os
from datetime import datetime, timedelta
from generate_blog_post import (
    text_generation, generate_blog_title, generate_image_prompts_from_blog_post,
    generate_alt_text_from_prompts, mark_spots_for_images, insert_blog_post,
    generate_and_store_images, store_image_urls, replace_image_tags_with_urls,
    generate_keywords_from_blog_post, generate_pinterest_board_names,
    add_metadata_to_blog_post, upsert_blog_post, upload_blog_post_to_github, 
    get_specific_datetime_iso8601
)

def generate_dates(start_date: str, num_posts: int, interval_days: int):
    dates = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    for _ in range(num_posts):
        iso_date = get_specific_datetime_iso8601(current_date.year, current_date.month, current_date.day)
        dates.append(iso_date)
        current_date += timedelta(days=interval_days)
    return dates

def generate_blog_post_for_date(date: str):
    print(f"Generating blog post for date: {date}")
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
    blog_post_plus_metadata = add_metadata_to_blog_post(blog_title, final_blog_post, image_urls, blog_post_id, keywords, pinterest_boards, date_time=date)

    # Sometimes the LLM puts "BLOG_POST:" at the beginning
    if "BLOG_POST:" in blog_post_plus_metadata:
        blog_post_plus_metadata = blog_post_plus_metadata.replace("BLOG_POST:", "")

    print("Storing final blog post...")
    upsert_blog_post(blog_post_id, blog_post_plus_metadata)

    print("Blog post generation complete!")

    print("Uploading blog post to GitHub...")
    # GitHub Upload variables
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN")
    REPO_NAME: str = "Lars-Ostervold/ai-travel-blog"
    UPLOAD_PATH: str = f"frontend/_posts/{blog_post_id}_blog.md"
    BRANCH: str = "main"
    COMMIT_MESSAGE: str = f"Automated commit: Uploaded new blog post number {blog_post_id}"
    CONTENT_STRING: str = blog_post_plus_metadata

    upload_blog_post_to_github(CONTENT_STRING, GITHUB_TOKEN, REPO_NAME, UPLOAD_PATH, BRANCH, COMMIT_MESSAGE)
    print("Blog post uploaded to GitHub!")

if __name__ == "__main__":
    start_date = "2024-02-17"
    num_posts = 30
    interval_days = 11

    dates = generate_dates(start_date, num_posts, interval_days)

    for date in dates:
        generate_blog_post_for_date(date)