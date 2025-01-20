import generate_blog_post

def handler(event, context):
    # Call the function from generate_blog_post.py
    
    generate_blog_post.main()
    
    
    return {
        'statusCode': 200,
        'body': 'Blog post generated successfully!'
    }