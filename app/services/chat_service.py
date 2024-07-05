from youtube_transcript_api import YouTubeTranscriptApi
from flask import current_app
import chromadb.utils.embedding_functions as embedding_functions
from googleapiclient.discovery import build
from ..services.llm_service import wrapper
from ..services.auth_service import get_user_by_email
import datetime
import json
import time

def get_transcript(video_id, retries=3, delay=5, mongo=None, userId=None):
    video = mongo["videos"].find_one({"videoId": video_id})
    if not video:
        attempt = 0
        while attempt < retries:
            try:
                # Retrieve the transcript from YouTube
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                script = ""
                for entry in transcript:
                    script += entry['text'] + " "
                
                # Retrieve the video description from YouTube
                youtube_api = current_app.config.get("YOUTUBE_API")
                video_description = get_video_details(youtube_api, video_id)

                # Store the transcript in the database
                videos_collection = current_app.db["videos"]
                # check if the video already exists in the database
                video = videos_collection.find_one({"videoId": video_id})
                if not video:
                    videos_collection.insert_one({
                        "videoId": video_id,
                        "transcript": transcript,
                        "script": script,
                        "addedAt": datetime.datetime.now(),
                        "description": video_description
                    })
                return transcript
            except Exception as e:
                print(f"Connection reset by server: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
        print("Failed to retrieve transcript after several attempts.")
        return None
    

    transcript = video['transcript']
    # Store the video category in the database
    topics_collection = current_app.db["topics"]
    # check if the video already exists in the database
    topic = topics_collection.find_one({"videoId": video_id, "userId": userId})
    if not topic:
        script = ""
        for entry in transcript:
            script += entry['text'] + " "
        video_description = video['description']
        # Generate video category
        category = wrapper.generate_response(script=script, video_description=video_description, categorize=True, user_input="categories this video for me.")
        if not topic:
            topics_collection.insert_one({
                "videoId": video_id,
                "topics": json.loads(category),
                "userId": userId,
                "addedAt": datetime.datetime.now()
            })
    return transcript

def crop_transcript(transcript, timestamp):
    cropped_transcript = []
    for entry in transcript:
        entry_end_time = entry['start'] + entry['duration']
        if entry_end_time <= timestamp:
            cropped_transcript.append({
                "text": entry['text'],
                "start": entry['start'],
            })
        else:
            # Optionally, you could add logic here to include the entry that's currently being spoken,
            # even if it's only partially completed.
            break
    return cropped_transcript


def huggingface_ef(input):
    # Assuming current_app.config is available and contains HUGGINGFACE_APIKEYS
    apis = current_app.config.get("HUGGINGFACE_APIKEYS").split(" ")
    for api_key in apis:
        try:
            # Initialize the HuggingFace embedding function with an API key and model name
            hf_embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(
                api_key=api_key,
                model_name="hkunlp/instructor-base"
            )
            # Use the embedding function to process the input and return the embeddings
            return hf_embedding_function(input)
        except Exception as e:
            # Log or handle exceptions as necessary
            print(e)
            continue
    # If all attempts fail, raise an exception or handle it as appropriate for your application
    raise Exception("Failed to generate embeddings using HuggingFace API keys.")


def document_exists(collection, video_id):
    result = collection.get(
        where={"video_id": {"$eq": video_id}},
        include=[]  # We only need the ids to check existence
    )
    return bool(result['ids'])

def get_video_details(youtube_api_key, video_id):
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    # Retrieve the video details
    video_response = youtube.videos().list(
        part='snippet',  # Part parameter specifies that we need snippet information
        id=video_id
    ).execute()

    # Check if there are any results
    if not video_response['items']:
        return "No video found with the specified ID"

    # Extract title and description from the response
    video_details = video_response['items'][0]['snippet']

    return video_details