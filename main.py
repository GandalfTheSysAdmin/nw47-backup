#!/usr/bin/env python
"""
Discord Message Retriever

This script retrieves new messages from all specified Discord channels listed in the
`CHANNELS` dictionary in `channels.py` using the Discord API. The script processes
each channel, retrieves the content, author, and timestamp of new messages, and stores
these messages in files named after each channel. Additionally, any image attachments
found in the messages are downloaded and saved in a related folder structure. The script
also logs its activity for auditing and troubleshooting purposes.

Features:
    - Retrieves and saves new messages from specified Discord channels.
    - Downloads and stores image attachments in a structured directory.
    - Logs script activity to channel-specific log files.
    - Loads the Discord API token securely from a `.env` file.

Author: GandalfTheSysAdmin
Date: 2024-08-31

Usage:
    - The script automatically processes all channels defined in the `CHANNELS` dictionary.
    - Messages, images, and logs are saved in directories named after each channel.
    - Ensure that a valid Discord token is stored in the `.env` file as `DISCORD_TOKEN`.

Requirements:
    - discord: A Python wrapper for the Discord API (to interact with Discord).
    - requests: A simple, yet elegant, HTTP library for Python.
    - json: A built-in Python library for handling JSON data.
    - datetime: A built-in Python module for manipulating dates and times.
    - os: A built-in Python module for interacting with the operating system.
    - time: A built-in Python module for adding delays.
    - logging: A built-in Python module for logging script activity.
    - tqdm: A library for adding a progress bar to loops.
    - aiohttp: A library for asynchronous HTTP requests.
    - python-dotenv: A library to load environment variables from a `.env` file.

Notes:
    - The script retrieves only new messages sent after the last fetched message.
    - Requests are spaced out to avoid overwhelming the Discord API server.

License: MIT License
"""
import discord
import requests
import json
from datetime import datetime
import os
import time
import logging
from tqdm import tqdm
import aiohttp
from tqdm.asyncio import tqdm as tqdm_asyncio
from channels import Channel, CHANNELS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from the .env file
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

LAST_MESSAGE_ID_FILE_TEMPLATE = '{}/last_message_id.txt'

def setup_logging(channel_name):
    log_dir = f"{channel_name}/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = f"{log_dir}/script.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return log_file

def check_token():
    headers = {
        'Authorization': f'Bot {DISCORD_TOKEN}'
    }
    response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)

    if response.status_code == 200:
        logging.info("Token is valid.")
        return True
    else:
        logging.error(f"Failed to authenticate. Status code: {response.status_code}")
        return False

def load_last_message_id(channel_name):
    try:
        with open(LAST_MESSAGE_ID_FILE_TEMPLATE.format(channel_name), 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_last_message_id(channel_name, message_id):
    with open(LAST_MESSAGE_ID_FILE_TEMPLATE.format(channel_name), 'w') as file:
        file.write(message_id)

def parse_timestamp(timestamp):
    try:
        # Try to parse the timestamp with fractional seconds
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        # If that fails, try without fractional seconds
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')

def save_messages_to_file(channel_name, messages):
    filename = f"{channel_name}/{channel_name}_messages.txt"

    # Sort messages by timestamp in reverse order
    messages = sorted(messages, key=lambda x: x.get('timestamp', ''), reverse=True)

    with open(filename, 'a') as file:
        for message in messages:
            content = message.get('content', 'No content')
            author = message.get('author', {}).get('username', 'Unknown user')
            timestamp = message.get('timestamp', None)

            if timestamp:
                parsed_timestamp = parse_timestamp(timestamp)
                formatted_time = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted_time = 'Unknown time'

            file.write(f"[{formatted_time}] {author}: {content}\n")
            logging.info(f"Saved message from {author} at {formatted_time}")

async def valid_image_url(url: str):
    image_extensions = ['png', 'jpg', 'jpeg', 'gif']
    return any(url.endswith(f'.{ext}') for ext in image_extensions)

async def download_image(url: str, images_path: str = ""):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    image_name = os.path.basename(url)
                    file_path = os.path.join(images_path, image_name)

                    # Start progress bar
                    total_size = int(resp.headers.get('content-length', 0))
                    block_size = 1024
                    tqdm_bar = tqdm_asyncio(total=total_size, unit='iB', unit_scale=True, desc=image_name)

                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await resp.content.read(block_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            tqdm_bar.update(len(chunk))

                    tqdm_bar.close()
                    logging.info(f"Downloaded image: {file_path}")
                else:
                    logging.error(f"Failed to download image from {url}. Status code: {resp.status}")
    except Exception as e:
        logging.error(f"Error downloading image from {url}: {e}")

def create_channel_folder(channel_name):
    channel_folder = channel_name
    images_folder = os.path.join(channel_folder, "images")

    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder)
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    return channel_folder, images_folder

async def retrieve_messages(channel):
    num = 0
    headers = {
        'Authorization': f'Bot {DISCORD_TOKEN}'
    }

    last_message_id = load_last_message_id(channel.get_channel_name())
    url = f'https://discord.com/api/v9/channels/{channel.get_channel_id()}/messages?limit=100'
    if last_message_id:
        url += f'&after={last_message_id}'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        if messages:
            save_messages_to_file(channel.get_channel_name(), messages)
            channel_folder, images_folder = create_channel_folder(channel.get_channel_name())
            for message in tqdm(messages, desc=f"Processing {channel.get_channel_name()} messages", leave=False):
                content = message.get('content', 'No content')
                author = message.get('author', {}).get('username', 'Unknown user')
                timestamp = message.get('timestamp', None)

                if timestamp:
                    parsed_timestamp = parse_timestamp(timestamp)
                    formatted_time = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_time = 'Unknown time'

                logging.info(f"Message {num + 1} from channel '{channel.get_channel_name()}'")
                logging.info(f"User: {author}, Time: {formatted_time}, Content: {content}")

                # Check for attachments and download images
                attachments = message.get('attachments', [])
                for attachment in attachments:
                    if await valid_image_url(attachment['url']):
                        filename = attachment.get('filename', attachment['url'].split("/")[-1])
                        await download_image(attachment['url'], images_folder, filename)

                # Check for images in embeds and download them
                for embed in message.get('embeds', []):
                    if embed.get('image') and await valid_image_url(embed['image']['url']):
                        filename = os.path.basename(embed['image']['url'])
                        await download_image(embed['image']['url'], images_folder, filename)

                num += 1

            # Save the ID of the last message in the current batch
            save_last_message_id(channel.get_channel_name(), messages[0]['id'])
            logging.info(f'Number of messages collected from {channel.get_channel_name()}: {num}')
        else:
            logging.info(f'No new messages found for {channel.get_channel_name()}')
    else:
        logging.error(f"Failed to retrieve messages from {channel.get_channel_name()}. Status code: {response.status_code}")

async def main():
    # Check if the token is valid before processing channels
    if not check_token():
        print("Exiting due to invalid token.")
        exit(1)

    for channel_name, channel_id in tqdm(CHANNELS.items(), desc="Processing channels"):
        channel_folder, images_folder = create_channel_folder(channel_name)
        setup_logging(channel_name)
        logging.info(f"Starting message retrieval for channel: {channel_name}")

        channel = Channel(channel_id, channel_name)
        await retrieve_messages(channel)

        # Space out requests to avoid flooding the server
        time.sleep(5)  # Sleep for 5 seconds between channel requests

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
