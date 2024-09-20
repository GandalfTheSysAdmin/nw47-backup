"""
Discord Channel Backup Script

Description:
------------
This script automates the process of backing up Discord channel messages and attachments
(e.g., images) to local storage. It fetches messages from specified Discord channels, Downloads
any shared images, and logs them in a structured format within a backup directory.

Features:
---------
- Downloads and logs messages from Discord channels.
- Downloads attachments (images) and saves them to a dedicated directory.
- Tracks progress using a dynamic progress bar for both messages and image downloads.
- Supports resuming from the last fetched message using checkpoint files.
- Provides logging for errors, status, and performance.
- Supports browser impersonation using custom headers.

Usage:
------
1. Ensure that your Discord user token is set in a `.env` file with the key `DISCORD_TOKEN`.
2. Define the channels you want to back up in the `channels.py` file as a dictionary of channel names and IDs.
3. Install the required dependencies:
   $ pip install -r requirements.txt
4. Run the script:
   $ python3 main.py

Requirements:
-------------
- Python 3.x
- Dependencies listed in `requirements.txt`.

Author:
-------
- GandalfTheSysAdmin

Date:
-----
- 2024-09-05
"""

import requests
import json
import time
import os
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from channels import CHANNELS  # Import the CHANNELS dictionary from channels.py
from topics import TOPICS  # Import the TOPICS dictionary from topics.py
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler

# Load environment variables from the .env file
load_dotenv()

# Get the Discord user token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Define headers to impersonate a web browser (Chrome in this case)
headers = {
    "Authorization": DISCORD_TOKEN,  # Use the user token directly here
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
}

# Define the delay between requests to avoid hitting rate limits
delay_between_requests = 1.5  # Adjust based on rate limiting

# Set up logging
log_file = 'discord_backup.log'

# Configure logging with file rotation (10MB max, up to 5 backups)
logging.basicConfig(
    handlers=[RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Log that the script has started
logging.info("Discord Backup Script Started")

# Function to read the last fetched message ID from a checkpoint file
def get_last_message_id(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            return f.read().strip()
    return None

# Function to write the last fetched message ID to a checkpoint file
def save_last_message_id(checkpoint_file, message_id):
    with open(checkpoint_file, "w") as f:
        f.write(message_id)

# Function to download an image from a URL and save it to the images directory
def download_image(url, image_dir, timestamp, username, image_pbar=None):
    image_ext = os.path.splitext(urlparse(url).path)[1]
    image_name = f"{timestamp}_{username}{image_ext}"
    image_path = os.path.join(image_dir, image_name)

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            logging.info(f"Downloaded image: {image_name} from {url}")
            if image_pbar:
                image_pbar.update(1)
            return image_name
        else:
            logging.error(f"Failed to download image: {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error downloading image: {url}. Exception: {e}")
        return None

# Function to format and write messages to a text file, and check for images
def write_messages_to_file(messages, backup_file_path, image_dir):
    image_pbar = tqdm(total=len([msg for msg in messages if msg["attachments"]]), desc="Downloading images", leave=False)

    with open(backup_file_path, "a", encoding="utf-8") as f:
        for message in messages:
            timestamp = message["timestamp"]
            username = message["author"]["username"]
            content = message["content"]

            # Write the regular message content
            f.write(f"[{timestamp}] {username}: {content}\n")

            # Check for attachments (images, files)
            if "attachments" in message and message["attachments"]:
                for attachment in message["attachments"]:
                    if "url" in attachment:
                        image_url = attachment["url"]
                        # Download the image
                        image_name = download_image(image_url, image_dir, timestamp, username, image_pbar)
                        if image_name:
                            f.write(f"[{timestamp}] {username} shared an image: images/{image_name}\n")
                            logging.info(f"Image {image_name} associated with message from {username} at {timestamp}")

    image_pbar.close()

# Function to fetch and back up messages for a specific channel or topic
def fetch_and_backup_messages(item_name, item_id, url, headers, delay_between_requests, backup_type='channel'):
    logging.info(f"Fetching messages for {backup_type}: {item_name} (ID: {item_id})")

    all_messages = []
    backup_dir = f"backups/{backup_type}s/{item_name}/"  # Use 'channels' or 'topics' based on type
    image_dir = os.path.join(backup_dir, "images/")  # Define the images directory within the backup directory
    checkpoint_file = f"{backup_dir}last_message_{item_name}.txt"  # Define the checkpoint file using the name and type
    backup_file_path = f"{backup_dir}{item_name}_messages.txt"  # Define the text file for backup messages
    last_message_id = get_last_message_id(checkpoint_file)  # Retrieve the last saved message ID

    # Ensure the backup and image directories exist
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    channel_pbar = tqdm(total=None, desc=f"Backing up {backup_type} {item_name}", leave=True)

    while True:
        params = {"limit": int(100)}  # Ensure the limit is passed as an integer
        if last_message_id:
            params["after"] = last_message_id  # Get only messages after the last saved one

        try:
            response = requests.get(url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {backup_type} {item_name}: {e}")
            break

        if response.status_code == 200:
            messages = response.json()

            # If no more messages, break the loop
            if not messages:
                logging.info(f"No more messages to fetch for {backup_type} {item_name}")
                break

            # Write messages to the text file and download images
            write_messages_to_file(messages, backup_file_path, image_dir)

            # Update the last message ID for pagination
            last_message_id = messages[-1]["id"]
            all_messages.extend(messages)
            channel_pbar.update(len(messages))

            time.sleep(delay_between_requests)
        else:
            logging.error(f"Failed to fetch messages from {backup_type} {item_name}: {response.status_code} - {response.text}")
            break

    if all_messages:
        save_last_message_id(checkpoint_file, all_messages[-1]["id"])
        logging.info(f"Saved last message ID for {backup_type} {item_name}: {all_messages[-1]['id']}")

    channel_pbar.close()

# Loop through each channel in CHANNELS and back up the messages
for channel_name, channel_id in CHANNELS.items():
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    fetch_and_backup_messages(channel_name, channel_id, url, headers, delay_between_requests, backup_type='channel')

# Loop through each topic in TOPICS and back up the messages
for topic_name, topic_id in TOPICS.items():
    url = f"https://discord.com/api/v9/channels/{topic_id}/messages"
    fetch_and_backup_messages(topic_name, topic_id, url, headers, delay_between_requests, backup_type='topic')

# Log that the script has finished
logging.info("Discord Backup Script Completed")
