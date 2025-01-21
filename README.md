# AI Travel Blog

Welcome to the AI Travel Blog! This project is hosted at [Chasingmemories.blog](https://chasingmemories.blog).

## Overview

The goal of this project was to see if I could create a totally self-sustaining AI Travel Blog. I wanted something that, once I was done coding, would continue to update with new posts. I set this up by hosting the frontend on Vercel, which has a webhook to update when this repo is updated. Then, I set up AWS Lambda functions to generate new posts and upload them as .md files to this repo.


I also made some functions that will post content to Pinterest to try and drive traffic to the site. 

I have no explicit end-goal here. It just seemed like a fun way to learn some new skills. I'll probably integrate ads in the future as another thing to learn 🙂.

### Tech Stack
- **Frontend:** Next.js with TypeScript, hosted on Vercel
- **Backend:** Python scripts for content generation
- **Storage:** Supabase for storing images and other assets
- **Image Generation:** Midjourney API through Discord
- **Cloud Functions:** AWS Lambda with scheduler for running code on the cloud
- **Social Media Integration:** Pinterest API for posting content to Pinterest
- **Deployment:** Docker for containerizing Lambda functions


**The rest of this is mostly generated by Copilot, but I clarified where needed**

## Project Structure

The project is divided into two main parts: the backend and the frontend.

### Backend

The backend is responsible for generating the content of the blog posts. It uses OpenAI's API to create detailed and engaging travel stories based on various prompts and data sources.

- **Directory:** `backend/`
- **Main Files:**
  - `Dockerfiles`: Dockerfiles I use to build the images I uploaded for Lambda functions. The Dockerfile.pinterest is for the pinterest scripts.
  - `generate_blog_post.py`: Script to generate individual blog posts.
  - `generate_multiple_blog_posts.py`: Script to generate multiple blog posts.
  - `get_blog_topic.py`: Where I keep my ugly, hardcoded travel destinations because I couldn't figure out a better way to do this.
  - `lambda_function.py`: AWS Lambda function that calls 'generate_blog_post.py'
- `midjourney_bot.py`: Uses Discord's API to generate images with Midjourney. (This was not a trivial adventure.) Mostly inspired by yachty66's code [here](https://github.com/yachty66/unofficial_midjourney_python_api).
  - `utils/`: Utility functions and helpers.
    - `oauth/`: Handles OAuth authentication with Pinterest.
    - `flask_app.py`: Flask application for handling Pinterest OAuth and posting to Pinterest.
    - `templates/`: HTML templates for the OAuth flow.
  - `pinterest/`: Functions for interacting with the Pinterest API.
    - `lambda_function.py`: AWS Lambda function where I'll comment lines before building the Docker image depending on what I want to do.
    - `pinterest_api.py`: Contains the `PinterestAPI` class for interacting with Pinterest. Also contains a 'Pin' class that stores all the info you need for a Pin.
    - `pinterest_main.py`: Main script for Pinterest-related operations.
    - `post_random_pin_multiple_boards.py`: Script to post a random pin to multiple boards.
    - `post_random_pin_single_board.py`: Script to post a random pin to a single board.
    - `post_recent_pin.py`: Script to post the most recent pin.
    - `delete_pins.py`: Script to delete pins.
    - `delete_boards.py`: Script to delete boards.


### Frontend

The frontend is built with Next.js and TypeScript. Displays posts based on .md files in _posts/.

- **Directory:** `frontend/`
- **Main Files:**
  - `_posts/`: Directory containing Markdown files for each blog post.
  - `next.config.ts`: Next.js configuration file.
  - `package.json`: Project dependencies and scripts.
  - `src/`: Source code for the frontend application.
  - `public/`: Static assets such as images and icons.

## Conclusion

Thanks for checking out the AI Travel Blog project! It's been an exciting journey to build and experiment with this self-sustaining blog. I hope you found something interesting. Feel free to explore the code, suggest improvements, or fork me. Happy travels and happy coding! 🚀🌍

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
