#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: discord_clone.py
Description: A Python GUI application that mimics Discord's layout. It uses lazy loading to improve performance by loading images dynamically as they come into view.

Author: GandalfTheSysAdmin
Date: October 18, 2023
"""

import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLabel, QListWidgetItem, QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ImageLoaderThread(QThread):
    """
    A QThread class to load images asynchronously.
    """
    image_loaded = pyqtSignal(QLabel, QPixmap)

    def __init__(self, image_label, image_path):
        super().__init__()
        self.image_label = image_label
        self.image_path = image_path

    def run(self):
        """
        The entry point for the thread. Loads the image and emits a signal.
        """
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
            self.image_loaded.emit(self.image_label, pixmap)

class DiscordClone(QWidget):
    """
    Main application class that creates the GUI and handles the loading and displaying of channels and messages.
    """

    def __init__(self, base_dir):
        """
        Initializes the DiscordClone application.

        Parameters:
            base_dir (str): The base directory where the 'backups' folder is located.
        """
        super().__init__()

        # Set the base directory
        self.base_dir = base_dir

        # Data storage
        self.data = {}

        # Track running threads
        self.running_threads = []

        # Set the window title and size
        self.setWindowTitle("NW47 Discord Clone")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize the user interface
        self.initUI()

        # Load data
        self.load_data()

    def initUI(self):
        """
        Initializes the user interface components.
        """
        # Create the main horizontal layout
        main_layout = QHBoxLayout(self)

        # ----------------------------------
        # Left Side: Channel List
        # ----------------------------------

        # Create a QListWidget to display the list of channels
        self.channel_list = QListWidget()
        self.channel_list.itemClicked.connect(self.display_channel)
        main_layout.addWidget(self.channel_list, 1)

        # ----------------------------------
        # Right Side: Message Display Area
        # ----------------------------------

        # Create a QScrollArea to hold the messages
        self.message_area = QScrollArea()

        # Create a QWidget to act as a container for message widgets
        self.message_area_widget = QWidget()

        # Create a vertical layout for messages
        self.message_layout = QVBoxLayout(self.message_area_widget)

        # Set the message area widget and make it resizable
        self.message_area.setWidget(self.message_area_widget)
        self.message_area.setWidgetResizable(True)

        # Add the message area to the main layout
        main_layout.addWidget(self.message_area, 3)

        self.setLayout(main_layout)

        # Connect the scrollbar event to handle lazy loading
        self.message_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

    def load_data(self):
        """
        Loads all messages and images from the channels.
        """
        channels_path = os.path.join(self.base_dir, 'backups', 'channels')
        channels = [
            d for d in os.listdir(channels_path)
            if os.path.isdir(os.path.join(channels_path, d))
        ]

        for channel in channels:
            channel_data = []
            channel_path = os.path.join(channels_path, channel)
            message_file = f"{channel}_messages.txt"
            message_file_path = os.path.join(channel_path, message_file)

            if os.path.exists(message_file_path):
                messages = self.parse_messages(message_file_path, channel_path)
                self.data[channel] = messages
                # Add channel to the channel list
                item = QListWidgetItem(channel)
                self.channel_list.addItem(item)

    def parse_messages(self, file_path, channel_dir):
        """
        Parses the messages from the given text file.

        Parameters:
            file_path (str): The path to the message text file.
            channel_dir (str): The directory of the current channel.

        Returns:
            list: A list of message dictionaries.
        """
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    result = self.parse_line(line)
                    if result:
                        timestamp, username, msg_type, content = result
                        if msg_type == 'image':
                            image_path = os.path.join(channel_dir, content)
                            # Ignore unsupported file formats (e.g., .mov)
                            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                continue
                            messages.append({
                                'type': 'image',
                                'timestamp': timestamp,
                                'username': username,
                                'content': image_path
                            })
                        elif msg_type == 'text':
                            messages.append({
                                'type': 'text',
                                'timestamp': timestamp,
                                'username': username,
                                'content': content
                            })
        except Exception as e:
            # Handle exceptions
            print(f"Error parsing messages: {e}")
        return messages

    def parse_line(self, line):
        """
        Parses a line from the message file.

        Returns:
            tuple: (timestamp, username, message type, content)
        """
        # Pattern for image messages: [timestamp] username shared an image: imagepath
        pattern_image = r'\[(.*?)\] (.*?) shared an image: (.*)'
        # Pattern for normal messages: [timestamp] username: message
        pattern_message = r'\[(.*?)\] (.*?): (.*)'

        match_image = re.match(pattern_image, line)
        if match_image:
            timestamp = match_image.group(1)
            username = match_image.group(2)
            image_path = match_image.group(3)
            return timestamp, username, 'image', image_path

        match_message = re.match(pattern_message, line)
        if match_message:
            timestamp = match_message.group(1)
            username = match_message.group(2)
            message = match_message.group(3)
            return timestamp, username, 'text', message

        # If line does not match any pattern
        return None

    def display_channel(self, item):
        """
        Displays messages for the selected channel.

        Parameters:
            item (QListWidgetItem): The selected channel item.
        """
        # Clear previous messages from the message layout
        for i in reversed(range(self.message_layout.count())):
            widget_to_remove = self.message_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        channel_name = item.text()

        if channel_name in self.data:
            messages = self.data[channel_name]
            for msg in messages:
                if msg['type'] == 'text':
                    self.display_text(msg['username'], msg['content'])
                elif msg['type'] == 'image' and msg['content']:
                    self.create_image_placeholder(msg['username'], msg['content'])
                else:
                    # Handle missing images
                    self.display_text(msg['username'], "Image not found.")
        else:
            # Display a message if no data is found for the channel
            label = QLabel(f"No messages found for channel: {channel_name}")
            self.message_layout.addWidget(label)

    def display_text(self, username, content):
        """
        Displays a text message in the message area.

        Parameters:
            username (str): The username of the message sender.
            content (str): The message content to display.
        """
        # Create a QLabel for the message content
        label = QLabel(f"{username}: {content}")
        label.setWordWrap(True)  # Enable word wrapping for long messages

        # Optional: Set font and styling
        label.setStyleSheet("font-size: 14px; padding: 5px;")

        # Add the label to the message layout
        self.message_layout.addWidget(label)

    def create_image_placeholder(self, username, image_path):
        """
        Creates a placeholder for an image and loads it lazily when it becomes visible.

        Parameters:
            username (str): The username of the message sender.
            image_path (str): The full path to the image.
        """
        # Display username
        user_label = QLabel(f"{username}:")
        user_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.message_layout.addWidget(user_label)

        # Placeholder for the image
        image_label = QLabel("Loading image...")
        self.message_layout.addWidget(image_label)

        # Attach image path to QLabel for reference
        image_label.image_path = image_path
        image_label.setVisible(False)  # Initially hide to load later

    def on_scroll(self):
        """
        Handle scroll events to trigger lazy loading of images.
        """
        scroll_area = self.message_area.verticalScrollBar()
        max_value = scroll_area.maximum()
        current_value = scroll_area.value()

        # Load images that are visible
        for i in range(self.message_layout.count()):
            widget = self.message_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and hasattr(widget, 'image_path') and widget.isVisible() == False:
                image_path = widget.image_path
                if current_value < max_value:
                    # Start a thread to load images asynchronously
                    self.load_image_async(widget, image_path)

    def load_image_async(self, image_label, image_path):
        """
        Starts a thread to load the image asynchronously.

        Parameters:
            image_label (QLabel): The label where the image will be loaded.
            image_path (str): The full path to the image.
        """
        loader = ImageLoaderThread(image_label, image_path)
        loader.image_loaded.connect(self.set_image)
        loader.start()
        self.running_threads.append(loader)

    def set_image(self, image_label, pixmap):
        """
        Sets the loaded image on the QLabel.

        Parameters:
            image_label (QLabel): The label where the image will be set.
            pixmap (QPixmap): The loaded image.
        """
        image_label.setPixmap(pixmap)
        image_label.setVisible(True)  # Make it visible

    def closeEvent(self, event):
        """
        Handle window close event to ensure all threads are properly stopped.
        """
        # Stop all running threads gracefully
        for thread in self.running_threads:
            thread.quit()
            thread.wait()
        event.accept()

if __name__ == '__main__':
    # Create the QApplication instance
    app = QApplication(sys.argv)

    # Set the base directory (current working directory in this case)
    base_directory = os.getcwd()  # Change this if your base directory is different

    # Create and display the main application window
    window = DiscordClone(base_directory)
    window.show()

    # Start the application's event loop
    sys.exit(app.exec_())
