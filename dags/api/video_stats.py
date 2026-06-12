import requests
import json
from datetime import date

# import os
# from dotenv import load_dotenv
# load_dotenv()

from airflow.decorators import task
from airflow.models import Variable

API_KEY=Variable.get("API_KEY")
CHANNEL_HANDLE=Variable.get("CHANNEL_HANDLE")
max_results=50 #load the data in batches of 50 as the API has a limit of 50 results per request

@task
def get_playlist_id():
    try:
        url="https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle=" + CHANNEL_HANDLE + "&key=" + API_KEY
        response = requests.get(url)
        response.raise_for_status()
        data=response.json()
        playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return playlist_id
    except Exception as e:
        print("Error fetching playlist ID:", e)
        return None
    
@task
def get_video_ids(playlist_id):
    try:
        base_url=f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}'
        pageToken = None #pageToken is used for pagination, it will be None for the first request and will be updated with the nextPageToken from the response for subsequent requests, until there are no more pages left to fetch.
        video_ids = []
        while True:
            url=base_url
            if pageToken:
                url += f'&pageToken={pageToken}'
            response = requests.get(url)
            response.raise_for_status()
            data=response.json()
            for item in data.get("items",[]):
                video_ids.append(item["contentDetails"]["videoId"])
            pageToken = data.get("nextPageToken")
            if not pageToken:
                break        
        return video_ids
    except Exception as e:
        print("Error fetching video ids:", e)
        return []
    
@task
def extract_video_stats(video_ids):
    extracted_data=[]

    def batch_list(video_id_lst,batch_size):
        for video_id in range(0,len(video_id_lst),batch_size):
            yield video_id_lst[video_id:video_id+batch_size] #yield is used to create a generator that produces batches of video IDs, allowing us to process them in chunks of the specified batch size.

    try:
        for batch in batch_list(video_ids,max_results):
            video_ids_str=",".join(batch)
            url=f"https://youtube.googleapis.com/youtube/v3/videos?part=statistics&part=contentDetails&part=snippet&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data=response.json()
            for item in data.get("items",[]):
                video_id=item['id']
                snippet=item['snippet']
                contentDetails=item['contentDetails']
                statistics=item['statistics']
                video_data={
                    "video_id":video_id,
                    "title":snippet['title'],
                    "publishedAt":snippet['publishedAt'],
                    "duration":contentDetails['duration'],
                    "likeCount":statistics.get('likeCount',None),
                    "viewCount":statistics.get('viewCount',None),
                    "commentCount":statistics.get('commentCount',None)
                }
                extracted_data.append(video_data)
        return extracted_data
    except Exception as e:
        print("Error fetching video statistics:", e)
        return None
    
@task
def save_to_json(extracted_data):
    file_path=f'./data/YT_data_{date.today()}.json'
    with open(file_path,"w",encoding="utf-8") as json_outfile: #encoding is set to utf-8 to ensure that any special characters in the video titles or other fields are properly handled and saved in the JSON file.
        json.dump(extracted_data,json_outfile,indent=4,ensure_ascii=False) #indent=4 is used to format the JSON output with an indentation of 4 spaces for better readability, and ensure_ascii=False allows non-ASCII characters to be saved as they are instead of being escaped, which is important for preserving the integrity of the data, especially if it contains special characters or emojis.
     
   
