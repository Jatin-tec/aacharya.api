from __future__ import absolute_import, unicode_literals
from conversation.utils import get_video_transcript
from celery import shared_task

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name="get_video_transcript")
def get_video_transcript_task(video_id):
    logger.info("Retrieved video transcript for %s", video_id)
    return get_video_transcript(video_id)
