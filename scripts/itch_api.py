import requests
from os import getenv
# Replace these with your details
API_KEY = getenv("ITCH_API_KEY")
GAME_ID = "dummy"  # Find this in your game URL (e.g., itch.io/game/123456)
USER_NAME = "reayd-falmouth"
NEW_TITLE = "New Dummy"
NEW_DESCRIPTION = "This is an updated game description with new features."
COVER_IMAGE_PATH = "cover.png"  # Path to your new cover image

# Itch.io API endpoint for updating game metadata
BASE_URL = f"https://itch.io/api/1/{API_KEY}/game/{GAME_ID}"

# Update game metadata (title & description)
def update_metadata():
    payload = {
        "title": NEW_TITLE,
        "short_text": NEW_DESCRIPTION,
    }
    response = requests.post(BASE_URL, json=payload)

    if response.status_code == 200:
        print("✅ Game metadata updated successfully!")
    else:
        print(f"❌ Error updating metadata: {response.text}")

# Upload new cover image
def upload_cover_image():
    with open(COVER_IMAGE_PATH, "rb") as img_file:
        files = {"cover": img_file}
        response = requests.post(BASE_URL, files=files)

    if response.status_code == 200:
        print("✅ Cover image updated successfully!")
    else:
        print(f"❌ Error updating cover image: {response.text}")

if __name__ == "__main__":
    update_metadata()
    upload_cover_image()
