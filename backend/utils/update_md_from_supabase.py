import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, key)

# Directory containing the markdown files
posts_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/_posts'))

# Ensure the directory exists
if not os.path.exists(posts_directory):
    raise FileNotFoundError(f"The directory {posts_directory} does not exist.")

def update_md_files_from_supabase():
    # Fetch all blog posts from Supabase
    response = supabase.table('blog_posts').select('id', 'content').execute()
    blog_posts = response.data

    for post in blog_posts:
        post_id = post['id']
        new_content = post['content']

        # Find the corresponding markdown file
        md_file_path = os.path.join(posts_directory, f"{post_id}_blog.md")
        if os.path.exists(md_file_path):
            # Overwrite the content of the markdown file with the new content
            with open(md_file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Updated content for post ID {post_id}")

if __name__ == "__main__":
    update_md_files_from_supabase()