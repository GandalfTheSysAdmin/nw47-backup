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

# Define the backup directory
BACKUP_DIR = 'backups'

LAST_MESSAGE_ID_FILE_TEMPLATE = '{}/last_message_id.txt'

def setup_logging(channel_name):
    log_dir = os.path.join(BACKUP_DIR, channel_name, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "script.log")
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
    filename = os.path.join(BACKUP_DIR, channel_name, f"{channel_name}_messages.txt")

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

def create_channel_folder(channel_name):
    channel_folder = os.path.join(BACKUP_DIR, channel_name)
    images_folder = os.path.join(channel_folder, "images")

    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder)
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    return channel_folder, images_folder
