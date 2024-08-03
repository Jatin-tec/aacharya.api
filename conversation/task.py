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
def get_video_transcript_task(video_id, email):
    logger.info("Retrieved video transcript for %s", video_id)
    return get_video_transcript(video_id=video_id, email=email)

@shared_task(name="generate_response")
def generate_response_task(user_message, video_id, timestamp, email):
    transcript = get_video_transcript(video_id)
    cropped_transcript = crop_transcript(transcript, timestamp)
    wrapper = LLMWrapper()
    
    # append history with user last 3 messages if exists
    conversation = Conversation.objects.filter(videoId=video_id, username=email).order_by('-timestamp')[:3]
    if conversation:
        history = []
        for entry in conversation:
            history.append({
                "role": "user", 
                "parts": [entry.user_message]
            }, {
                "role": "model",
                "parts": [entry.response]
            })
    response = wrapper.generate_response(user_message, context=cropped_transcript)
    user = User.objects.filter(email=email).first()
    video = Video.objects.filter(videoId=video_id).first()
    Conversation.objects.create(
        videoId=video,
        username=user,
        text=user_message,
        response=response
    )
    logger.info("Generated response for %s", user_message)
    return response

@shared_task(name="summarize_video")
def summarize_video(video_id, conversation, email):
    transcript = get_video_transcript(video_id)
    script = ""
    for entry in transcript:
        script += entry['text'] + " "
    chunk_size = 8000
    chunks = [script[i:i+chunk_size] for i in range(0, len(script), chunk_size)]
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
    
    logger.info("Summarized video %s", video_id)
    return notes

@shared_task(name="get_flowchart_data")
def get_flowchart_data(video_id):
    video = Video.objects.get(videoId=video_id)
    if video.visual_data:
        logger.info("Flowchart data already exists for %s", video_id)
        return video.visual_data
    else:
        transcript = get_video_transcript(video_id)
        wrapper = LLMWrapper()
        response = wrapper.generate_response("Extracts topics for video provided.", context=transcript, visualize=True)
        video.visual_data = response
        video.save()
        logger.info("Generated flowchart data for %s", video_id)
        return response