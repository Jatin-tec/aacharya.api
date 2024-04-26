from youtube_transcript_api import YouTubeTranscriptApi
from flask import current_app
import chromadb.utils.embedding_functions as embedding_functions
import time

def get_transcript(video_id, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Connection reset by server: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            attempt += 1
    print("Failed to retrieve transcript after several attempts.")
    return None


def crop_transcript(transcript, timestamp):
    cropped_transcript = []
    for entry in transcript:
        entry_end_time = entry['start'] + entry['duration']
        if entry_end_time <= timestamp:
            cropped_transcript.append(entry)
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
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            # Use the embedding function to process the input and return the embeddings
            return hf_embedding_function(input)[0][0]
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

