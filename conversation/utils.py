from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from conversation.models import Video, Topic
from conversation.api.serializers import VideoSerializer, TranscriptField, DescriptionField
from llm_wrapper.wrapper import LLMWrapper
import time
import json
import os

def get_video_transcript(video_id, retries=2, delay=5):
    video = Video.objects.filter(videoId=video_id).first()
    if not video:
        attempt = 0
        while attempt < retries:
            try:
                # Retrieve the transcript from YouTube
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                
                # Retrieve the video description from YouTube
                video_description = get_video_details(video_id)
                
                # Save the video and its transcript to the database using Serializer
                video_data = {
                    'videoId': video_id,
                    'transcript': transcript,
                    'description': video_description
                }

                video_serializer = VideoSerializer(data=video_data)
                if video_serializer.is_valid():
                    video_serializer.save()
                    return transcript
                else:
                    print(video_serializer.errors)
                    return None
            except Exception as e:
                print(f"Connection reset by server: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
                if attempt == retries:
                    print("Failed to retrieve transcript after several attempts.")
                    return None
    else:
        transcript = TranscriptField().to_representation(video.transcript)
        if not video.topic:
            script = ""
            for entry in transcript:
                script += entry['text'] + " "

            video_description = DescriptionField().to_representation(video.description)
            # Generate video category
            wrapper = LLMWrapper()
            category = wrapper.generate_response(script=script, video_description=video_description, categorize=True, user_input="categories this video for me.")

            # Update the video topic
            category = json.loads(category)
            topic = Topic.objects.filter(id=category['id']).first()
            video.topic = topic
            video.save()
    return transcript

def get_video_details(video_id):
    youtube_api = os.environ.get("YOUTUBE_API_KEY", None)
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=youtube_api)

    # Retrieve the video details
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    # Check if there are any results
    if not video_response['items']:
        return "No video found with the specified ID"

    # Extract title and description from the response
    video_details = video_response['items'][0]['snippet']

    return video_details

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