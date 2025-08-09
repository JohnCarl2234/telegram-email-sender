import requests
import os

# --- CONFIGURATION ---
BOT_TOKEN = '7989024669:AAF3WZNZtBatFnivCzweR_ftsFYMrgyDb-4' 
VIDEO_PATH = '/home/carleaux/python-telegram-bot/media/media2.mp4' 
YOUR_CHAT_ID = '5141207096' 
CONFIG_FILE = 'video_config.py'

def get_and_save_video_id():
    """
    Uploads a video to Telegram to get its file_id and saves it to a config file.
    """
    print("Starting video setup...")

    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Error: Video file not found at '{VIDEO_PATH}'")
        return

    # The URL for the `sendVideo` method of the Telegram Bot API.
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo'

    # Prepare the data for the POST request.
    files = {'video': open(VIDEO_PATH, 'rb')}
    data = {'chat_id': YOUR_CHAT_ID}

    try:
        print(f"Uploading '{VIDEO_PATH}' to Telegram to get its file_id. This might take a moment...")
        # Make the request to the Telegram API.
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)

        # Parse the JSON response from Telegram.
        result = response.json()

        if result.get('ok'):
            # Extract the file_id from the response.
            file_id = result['result']['video']['file_id']
            print(f"✅ Success! Got file_id: {file_id}")

            # Save the file_id to the config file.
            with open(CONFIG_FILE, 'w') as f:
                f.write(f"VIDEO_ID = '{file_id}'\n")
            print(f"✅ Configuration saved to '{CONFIG_FILE}'")
            print("\nSetup complete! You can now run your main bot script.")
        else:
            print(f"❌ Error from Telegram: {result.get('description')}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: Could not connect to Telegram API. {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == '__main__':
    get_and_save_video_id()
