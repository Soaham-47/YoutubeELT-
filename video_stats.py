import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv("API_KEY")
CHANNEL_HANDLE="MrBeast"

def get_playlist_id():
    try:
        url="https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle=" + CHANNEL_HANDLE + "&key=" + API_KEY
        response = requests.get(url)
        data = response.json()
        json.dumps(data, indent=4)
        playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return playlist_id
    except Exception as e:
        print("Error fetching playlist ID:", e)
        return None
    
if __name__ == "__main__":
    playlist_id = get_playlist_id()
    if playlist_id:
        print("Playlist ID:", playlist_id)
    else:
        print("Failed to retrieve playlist ID.")


