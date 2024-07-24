from __future__ import absolute_import, unicode_literals

from conversation.utils import get_video_transcript, crop_transcript
from conversation.models import Conversation, Video, Note
from authentication.models import User

from celery.utils.log import get_task_logger
from celery import shared_task

from llm_wrapper.wrapper import LLMWrapper

from time import sleep

logger = get_task_logger(__name__)

@shared_task(name="get_video_transcript")
def get_video_transcript_task(video_id):
    logger.info("Retrieved video transcript for %s", video_id)
    return get_video_transcript(video_id)

@shared_task(name="generate_response")
def generate_response_task(user_message, video_id, timestamp, email):
    logger.info("Generated response for %s", user_message)
    transcript = get_video_transcript(video_id)
    cropped_transcript = crop_transcript(transcript, timestamp)
    wrapper = LLMWrapper()
    response = wrapper.generate_response(user_message, context=cropped_transcript)
    wrapper.history.append({
        "role": "user", 
        "parts": response 
    })
    video = Video.objects.get(videoId=video_id)
    user = User.objects.get(email=email)
    Conversation.objects.create(
        videoId=video,
        username=user,
        timestamp=timestamp,
        text=user_message,
        response=response
    )
    
    return response

@shared_task(name="summarize_video")
def summarize_video(video_id, conversation, email):
    logger.info("Summarized video %s", video_id)
    transcript = get_video_transcript(video_id)
    
    script = ""
    for entry in transcript:
        script += entry['text'] + " "
    
    chunk_size = 8000
    chunks = [script[i:i+chunk_size] for i in range(0, len(script), chunk_size)]
    print(f"Number of chunks: {len(chunks)}")
    
    video = Video.objects.get(videoId=video_id)
    user = User.objects.get(email=email)
    
    try:
        notes = Note.objects.get(videoId=video)
    except Note.DoesNotExist:
        notes = None
    
    wrapper = LLMWrapper()
    
    if notes:
        notes = notes.notes
    else:
        notes = ""
        i = 1
        for chunk in chunks:
            response = wrapper.generate_response(chunk, summary=True,  current=i, total=len(chunks), questions=conversation)
            notes += f"Chunk {i}: {response}\n"
            i += 1
            print("Chunk processed")
            sleep(3)
        
        Note.objects.create(videoId=video, username=user, notes=notes)
    
    return notes