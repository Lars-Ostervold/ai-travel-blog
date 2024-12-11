WORK IN PROGRESS
Not fully functional yet. Currently working on the backend. Uploading a MD file to the frontend is the trivial part...

Travel Blog Bot
Welcome to the Travel Blog Bot! This is a fully automated travel blog where AI generates content and posts it to the blog.

How it Works
Code in the backend is hosted on XXX. Runs a chron job to generate a blog post from a hardcoded list of >500 locations. Uses ChatGPT and DALLE-3 to generate a blog post with images. Uploads the data to Supabase. A MD file is generated from the data on Supabase (using ChatGPT to figure out where the photos go in the post). That MD file is uploaded to the blog. Then we make a Pinterest post from that blog post.

Updates daily for now