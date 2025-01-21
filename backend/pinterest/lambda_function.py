# import post_all_pins
# import post_random_pin_single_board
import post_random_pin_multiple_boards
# import post_recent_pin

def handler(event, context):
    # Call the function from generate_blog_post.py
    
    #Options in each image
    # post_all_pins.main()
    # post_random_pin_single_board.main()
    post_random_pin_multiple_boards.main()
    # post_recent_pin.main()

    
    return {
        'statusCode': 200,
        'body': 'Random pin posted to multiple boards successfully!'
    }