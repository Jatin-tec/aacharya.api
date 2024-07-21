from __future__ import absolute_import, unicode_literals
from celery import shared_task
from authentication.utils import send_email

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name="send_interview_schedule_email")
def send_interview_schedule_email(email, context, subject):
    logger.info("Sent welcome email to %s", email)
    return send_email(email, 'emails/schedule.html', context, subject)