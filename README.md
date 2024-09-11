# Discord Channel Backup Script

This Python script automates the process of backing up Discord channel messages and downloading attachments (such as images) to local storage. It tracks progress, logs events, and supports resuming from the last fetched message.

## Features

- **Message Backup**: Fetches and logs messages from specified Discord channels.
- **Attachment Download**: Downloads images and other attachments and organizes them into a dedicated directory for each channel.
- **Progress Tracking**: Shows real-time progress for both message fetching and image downloading.
- **Checkpoint Resumption**: Supports resuming from the last fetched message using a checkpoint system.
- **Logging**: Logs errors, status, and performance for monitoring the backup process.
- **Browser Impersonation**: Uses custom headers to mimic browser requests for Discord API.

## Prerequisites

- **Python 3.x**: Ensure you have Python 3.x installed on your system.
- **Discord User Token**: You’ll need your Discord user token to access the Discord API.

## Installation

1. Clone the repository or download the script files.
2. Set up a `.env` file with your Discord user token:

   ```bash
   DISCORD_TOKEN=<your_discord_user_token_here>
   ```

3. Install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

4. Define the channels you want to back up in the `channels.py` file as a dictionary:

   ```python
   CHANNELS = {
       'channel_name': 'channel_id',
       'another_channel': 'another_channel_id',
   }
   ```

## Usage

To run the script and start backing up messages and images from Discord channels, use the following command:

```bash
python3 main.py
```

The script will automatically:
- Fetch messages from the specified Discord channels.
- Download any attachments (e.g., images) shared in the messages.
- Save the results in organized directories under a `backups/` folder.

![nw47-example-backup](./extras/nw47-backup-example3.gif)

## Example Directory Structure

```plaintext
backups/
├── bluberry/
│   ├── bluberry_messages.txt
│   ├── last_message_bluberry.txt
│   ├── images/
│   │   ├── 2023-11-24T18:57:42Z_username.jpg
│   │   └── 2023-11-25T10:15:30Z_otheruser.jpg
```

## Logging

All script activities are logged to `discord_backup.log`. The log file uses a rotating file handler to prevent it from growing too large. The log includes details on:
- Messages fetched
- Images downloaded
- Errors encountered

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`:
  - `requests`
  - `tqdm`
  - `python-dotenv`

