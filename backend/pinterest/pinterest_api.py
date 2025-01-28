import requests
from typing import List

class Pin:
    """
    Represents a Pin for Pinterest with a title, description, media URL, and link.
    Attributes:
        title (str): The title of the pin.
        description (str): The description of the pin.
        media_url (str): The URL of the media (image) for the pin.
        link (str): The link associated with the pin.
        boards_to_post_to (List[str]): The list of board names to post the pin to.
    """
    def __init__(self, title: str, description: str, media_url: str, link: str, boards_to_post_to: List[str]) -> None:
        """
        Initialize a Pin object.
        """
        self.title = title[:98]  # Ensure title is max 98 characters
        self.description = description
        self.media_url = media_url
        self.link = link
        self.boards_to_post_to = boards_to_post_to

    def to_dict(self) -> dict:
        """
        Convert the Pin object to a dictionary.

        :return: A dictionary representation of the Pin object.
        """
        return {
            "title": self.title,
            "description": self.description,
            "media_url": self.media_url,
            "link": self.link,
            "boards_to_post_to": self.boards_to_post_to
        }

class PinterestAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def send_failure_email(self, function_name) -> None:
        """
        Sends an email to the user letting them know token is expired.
        
        Raises:
            smtplib.SMTPException: If there is an error sending the email

        Returns:
            None
        """
        import os
        import datetime
        #Failure email
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        s = smtplib.SMTP(os.getenv("EMAIL_HOST"), os.getenv("EMAIL_PORT"))
        s.starttls()

        s.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        
        sender_email = os.getenv("EMAIL_USER")
        receiver_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")

        message = MIMEMultipart("alternative")
        message["Subject"] = "Travel Blog Pinterest Token Expired"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = f"The following function failed due to an expired Pinterest token: {function_name}. The date is {datetime.datetime.now()}"
        part = MIMEText(text, "plain")
        message.attach(part)

        s.sendmail(sender_email, receiver_email, message.as_string())

        s.quit()

    def fetch_and_print_first_25_boards(self):
        boards_url = "https://api.pinterest.com/v5/boards/"
        params = {
            "page_size": 25,
        }
        response = requests.get(boards_url, headers=self.headers, params=params)
        if response.status_code == 200:
            boards = response.json()["items"]
            for board in boards:
                print(f"Board ID: {board['id']}, Name: {board['name']}")
        else:
            print("Error fetching boards:", response.json())
    
    #Pinterest fetches 25 by default, max is 250. Set up a loop to fetch all boards.
    def fetch_all_boards(self):
        boards_url = "https://api.pinterest.com/v5/boards/"
        all_boards = []
        bookmark = None

        while True:
            params = {
                "page_size": 250,
            }
            if bookmark:
                params["bookmark"] = bookmark

            response = requests.get(boards_url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                boards = data["items"]
                all_boards.extend(boards)
                bookmark = data.get("bookmark")
                if not bookmark:
                    break
            elif response.status_code == 403:
                self.send_failure_email("get_board_id_from_name")
            else:
                print("Error fetching boards:", response.json())
                break      

        return all_boards
    
    def delete_all_boards(self):
        boards_url = "https://api.pinterest.com/v5/boards/"
        response = requests.get(boards_url, headers=self.headers)
        if response.status_code == 200:
            boards = response.json()["items"]
            for board in boards:
                board_id = board["id"]
                delete_board_url = f"https://api.pinterest.com/v5/boards/{board_id}"
                response = requests.delete(delete_board_url, headers=self.headers)
                if response.status_code == 204:
                    print(f"Board {board_id} deleted successfully.")
                else:
                    print(f"Error deleting board {board_id}:", response.json())
        else:
            print("Error fetching boards:", response.json())

    def post_pin(self, board_id, title, description, media_url, link):
        pin_url = "https://api.pinterest.com/v5/pins"
        payload = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": {
                "source_type": "image_url",
                "url": media_url
            },
            "link": link, 
        }
        response = requests.post(pin_url, json=payload, headers=self.headers)
        if response.status_code == 201:
            print("Pin Created Successfully!")
        elif response.status_code == 403:
            self.send_failure_email("post_pin")
        else:
            print("Error creating pin:", response.json())

    def fetch_pins(self, board_id):
        pins_url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
        response = requests.get(pins_url, headers=self.headers)
        if response.status_code == 200:
            pins = response.json()["items"]
            for pin in pins:
                print(f"Pin ID: {pin['id']}, Title: {pin['title']}, Description: {pin['description']}")
        else:
            print("Error fetching pins:", response.json())
    
    def create_board_and_get_id(self, board_name):
        boards_url = "https://api.pinterest.com/v5/boards/"
        payload = {
            "name": board_name,
            "description": board_name,
            "privacy": "PUBLIC",
        }
        response = requests.post(boards_url, json=payload, headers=self.headers)
        if response.status_code == 201:
            board_id = response.json()["id"]
            print(f"Board {board_name} created with ID: {board_id}")
            return board_id
        elif response.status_code == 403:
            self.send_failure_email("create_board_and_get_id")
        else:
            print("Error creating board:", response.json())
            return None
    
    def get_board_id_from_name(self, board_name):
        all_boards = self.fetch_all_boards()
        if not all_boards:
            print("No boards found. Likely error in fetching boards.")
            return None
        for board in all_boards:
            print(f"Board name from Pinterest: {board['name']}")
            print(f"Board name from input: {board_name}")
            if board['name'] == board_name:
                print("-----------------MATCH TRIGGERED-----------------")
                return board['id']
        print(f"Board {board_name} not found. Creating board...")
        return self.create_board_and_get_id(board_name)
    
    def post_pin_to_travel_board(self, title, description, media_url, link):
        board_id = self.get_board_id_from_name('Travel')
        self.post_pin(board_id, title, description, media_url, link)
    
    def delete_all_pins(self):
        pins_url = "https://api.pinterest.com/v5/pins"
        response = requests.get(pins_url, headers=self.headers)
        if response.status_code == 200:
            pins = response.json()["items"]
            for pin in pins:
                pin_id = pin["id"]
                delete_pin_url = f"https://api.pinterest.com/v5/pins/{pin_id}"
                response = requests.delete(delete_pin_url, headers=self.headers)
                if response.status_code == 204:
                    print(f"Pin {pin_id} deleted successfully.")
                else:
                    print(f"Error deleting pin {pin_id}:", response.json())
        else:
            print("Error fetching pins:", response.json())
    
    def delete_n_most_recent_pins(self, n):
        pins_url = "https://api.pinterest.com/v5/pins"
        response = requests.get(pins_url, headers=self.headers)
        if response.status_code == 200:
            pins = response.json()["items"]
            #Sort pins by created_at
            pins.sort(key=lambda x: x['created_at'], reverse=True)
            for pin in pins[:n]:
                pin_id = pin["id"]
                delete_pin_url = f"https://api.pinterest.com/v5/pins/{pin_id}"
                response = requests.delete(delete_pin_url, headers=self.headers)
                if response.status_code == 204:
                    print(f"Pin {pin_id} deleted successfully.")
                else:
                    print(f"Error deleting pin {pin_id}:", response.json())
        else:
            print("Error fetching pins:", response.json())