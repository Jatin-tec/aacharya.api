from __future__ import absolute_import, unicode_literals
from authentication.utils import send_email
from celery import shared_task

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name="send_welcome_email")
def send_welcome_email(name, email):
    logger.info("Sent welcome email to %s", email)
    return send_email(name, email)