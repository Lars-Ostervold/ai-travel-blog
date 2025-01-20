# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Copy the requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY generate_blog_post.py ${LAMBDA_TASK_ROOT}
COPY midjourney_bot.py ${LAMBDA_TASK_ROOT}
COPY get_blog_topic.py ${LAMBDA_TASK_ROOT}
COPY .env ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]