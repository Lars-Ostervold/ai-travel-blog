# WORK IN PROGRESS
The frontend/backend pipeline is integrated, but need to build out a backend that will make Pinterest posts.

## Travel Blog Bot
Welcome to the Travel Blog Bot! This is a fully automated travel blog where AI generates content and posts it to the blog.

## End Goal
Host backend on a cloud computing service and it runs on a chron job. The backend generates a blog post (text and images) from a hardcoded list of >500 locations. The text generation is handled by ChatGPT 4o-mini and the image generation is handled by Midjourney. I set up a Discord bot to prompt Midjourney, which heavily leveraged previous code [(repo).](https://github.com/yachty66/unofficial_midjourney_python_api). The backend uploads blog post data to Supabase as it generates, then compiles everything into a single .md file which is pushed to fronted/_posts. Once pushed to the _posts folder, a webhook on Vercel automatically updates the website. 

**Pinterest Post**
The largest remaining to-do is to generate a Pinterest post from the content.

