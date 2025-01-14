import os
from supabase import create_client, Client
from generate_blog_post import get_clean_excerpt
from dotenv import load_dotenv
import re

load_dotenv()

# Initialize Supabase client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

def remove_yaml_front_matter(content: str) -> str:
    # Regular expression to match YAML front matter
    yaml_pattern = re.compile(r'^---\s*[\s\S]*?---\s*', re.MULTILINE)
    return re.sub(yaml_pattern, '', content)

def update_excerpts_from_blog_post():
    # Fetch all blog posts
    response = supabase.table('blog_posts').select('id, content').execute()
    blog_posts = response.data

    for post in blog_posts:
        post_id = post['id']
        content = post['content']
        
        # Remove YAML front matter
        content_without_yaml = remove_yaml_front_matter(content)
        
        # Generate excerpt
        excerpt = get_clean_excerpt(content_without_yaml)
        
        # Upsert the excerpt into the blog_posts table
        supabase.table('blog_posts').upsert({'id': post_id, 'excerpt': excerpt}).execute()


def update_yaml_header(content: str, excerpt: str) -> str:
    # Define the pattern to find the excerpt field in the YAML header
    pattern = r'(excerpt:\s*")([^"]*)(")'
    # Replace the empty excerpt with the actual excerpt from the database
    updated_content = re.sub(pattern, f'\\1{excerpt}\\3', content, count=1)
    return updated_content

def update_yaml_in_supabase():
    # Fetch data from Supabase
    data = supabase.table('blog_posts').select('id', 'content', 'excerpt').execute()

    for record in data.data:
        content = record['content']
        excerpt = record['excerpt']
        updated_content = update_yaml_header(content, excerpt)

        #Upsert
        supabase.table('blog_posts').upsert({'id': record['id'], 'content': updated_content}).execute()

if __name__ == "__main__":
    update_yaml_in_supabase()