from __future__ import absolute_import, unicode_literals

from conversation.utils import get_video_transcript, crop_transcript
from conversation.models import Conversation, Video
from authentication.models import User

from celery.utils.log import get_task_logger
from celery import shared_task

from llm_wrapper.wrapper import LLMWrapper

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
    conversation = Conversation.objects.create(
        videoId=video,
        username=user,
        timestamp=timestamp,
        text=user_message,
        response=response
    )
    
    return response