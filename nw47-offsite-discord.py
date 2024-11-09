#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: discord_clone.py
Description: A Python GUI application that mimics Discord's layout. It uses efficient image loading and thumbnail generation to improve performance.

Author: GandalfTheSysAdmin
Date: October 18, 2023

Change Log:
- **2024-10-18**:
    - Refactored code to load thumbnails synchronously instead of using threads.
    - Removed ImagePreloader class and threading-related code.
    - Simplified thumbnail creation and loading logic.
    - Fixed issue where thumbnails were not displaying with the posts.
"""

import sys
import os
import re
import signal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLabel, QListWidgetItem, QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image

class DiscordClone(QWidget):
    """
    Main application class that creates the GUI and handles the loading and displaying of channels and messages.
    """

    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self.data = {}
        self.thumbnail_dir = os.path.join(self.base_dir, 'thumbnails')
        os.makedirs(self.thumbnail_dir, exist_ok=True)
        self.setup_window()
        self.initUI()
        self.load_data()

        # Handle graceful exit
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        app.aboutToQuit.connect(self.cleanup_threads)

    def exit_gracefully(self, signum, frame):
        QApplication.quit()

    def setup_window(self):
        self.setWindowTitle("NW47 Discord Clone")
        self.setGeometry(100, 100, 1200, 800)

    def initUI(self):
        main_layout = QHBoxLayout(self)
        self.channel_list = QListWidget()
        self.channel_list.itemClicked.connect(self.display_channel)
        main_layout.addWidget(self.channel_list, 1)

        self.message_area = QScrollArea()
        self.message_area_widget = QWidget()
        self.message_layout = QVBoxLayout(self.message_area_widget)
        self.message_area.setWidget(self.message_area_widget)
        self.message_area.setWidgetResizable(True)
        main_layout.addWidget(self.message_area, 3)

        self.setLayout(main_layout)

    def load_data(self):
        channels_path = os.path.join(self.base_dir, 'backups', 'channels')
        channels = [
            d for d in os.listdir(channels_path)
            if os.path.isdir(os.path.join(channels_path, d))
        ]

        for channel in channels:
            self.load_channel(channel, channels_path)

    def load_channel(self, channel, channels_path):
        channel_path = os.path.join(channels_path, channel)
        message_file = os.path.join(channel_path, f"{channel}_messages.txt")

        if os.path.exists(message_file):
            messages = self.parse_messages(message_file, channel_path)
            self.data[channel] = messages

            # Add channel to the list
            item = QListWidgetItem(channel)
            self.channel_list.addItem(item)

    def parse_messages(self, file_path, channel_dir):
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    result = self.parse_line(line)
                    if result:
                        msg_dict = self.create_message_dict(result, channel_dir)
                        if msg_dict:
                            messages.append(msg_dict)
        except Exception as e:
            print(f"Error parsing messages: {e}")
        return messages

    def parse_line(self, line):
        pattern_image = r'\[(.*?)\] (.*?) shared an image: (.*)'
        pattern_message = r'\[(.*?)\] (.*?): (.*)'

        match_image = re.match(pattern_image, line)
        if match_image:
            return match_image.groups() + ('image',)

        match_message = re.match(pattern_message, line)
        if match_message:
            return match_message.groups() + ('text',)

        return None

    def create_message_dict(self, parsed_data, channel_dir):
        timestamp, username, content, msg_type = parsed_data
        if msg_type == 'image':
            image_path = os.path.join(channel_dir, content)
            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return None
            return {'type': 'image', 'timestamp': timestamp, 'username': username, 'content': image_path}
        return {'type': 'text', 'timestamp': timestamp, 'username': username, 'content': content}

    def display_channel(self, item):
        self.clear_message_layout()

        # Determine which channel was clicked
        channel_name = item.text()
        if channel_name in self.data:
            for msg in self.data[channel_name]:
                if msg:
                    self.display_message(msg)

    def clear_message_layout(self):
        for i in reversed(range(self.message_layout.count())):
            widget = self.message_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def display_message(self, msg):
        if msg['type'] == 'text':
            self.display_text(msg['username'], msg['content'])
        elif msg['type'] == 'image':
            self.display_image_thumbnail(msg['username'], msg['content'])

    def display_text(self, username, content):
        label = QLabel(f"{username}: {content}")
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.message_layout.addWidget(label)

    def display_image_thumbnail(self, username, image_path):
        """
        Displays a thumbnail instead of the full image.
        """
        thumbnail_path = os.path.join(self.thumbnail_dir, os.path.basename(image_path))

        # Check if thumbnail exists; if not, create it
        if not os.path.exists(thumbnail_path):
            try:
                self.create_thumbnail(image_path, thumbnail_path)
            except Exception as e:
                print(f"Error creating thumbnail for {image_path}: {e}")
                return  # Exit if thumbnail creation fails

        # Load the thumbnail synchronously
        pixmap = QPixmap(thumbnail_path)
        if pixmap.isNull():
            print(f"Failed to load thumbnail: {thumbnail_path}")
            return

        self.show_thumbnail(username, pixmap)

    def create_thumbnail(self, image_path, thumbnail_path):
        """
        Creates a thumbnail of the image to speed up loading.
        """
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))
            # Save based on the original file extension
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.png', '.gif']:
                img.save(thumbnail_path, "PNG")
            else:
                img.convert("RGB").save(thumbnail_path, "JPEG")
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")

    def show_thumbnail(self, username, pixmap):
        user_label = QLabel(f"{username}:")
        user_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.message_layout.addWidget(user_label)

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        self.message_layout.addWidget(image_label)

    def cleanup_threads(self):
        pass  # No threads to clean up since we're loading synchronously

if __name__ == '__main__':
    app = QApplication(sys.argv)
    base_directory = os.getcwd()
    window = DiscordClone(base_directory)
    window.show()
    sys.exit(app.exec_())
