from fastapi import BackgroundTasks
from src.email import send_welcome_email
from src.core.celery_config import celery_app
import asyncio
from asgiref.sync import async_to_sync


@celery_app.task(name="send_welcome_email_task")
def dispatch_welcome_email(
        email_to: str, username: str="User"
    ) -> None:
        """Schedules the welcome email in the background."""
        async_to_sync(send_welcome_email)(email_to,username)
        print(f"--> [Celery Worker] Email sent successfully to {email_to}!")


