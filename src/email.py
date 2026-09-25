from pathlib import Path
from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from src.config import Config
from src.api.users.utils import create_token_serializer



# Path to HTML templates directory (optional but recommended)
TEMPLATE_FOLDER = Path(__file__).parent / "templates"


# Configure FastMail connection
mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)

# fast_mail object
fastmail = FastMail(mail_config)



async def send_welcome_email(email_to: str, username: str="User"):
    """Sends a basic HTML welcome email."""
    token=await create_token_serializer(email_to)
    link=f'{Config.BACKEND_URI}/api/v1/user/verify-email/{token}'
    html_content = f"""
    <html>
        <body>
            <h1>Welcome to Our Platform, {username}!</h1>
            <p>Click the <a href={link}>link</a> to verify your email.</p>
            <p>Thank you for signing up. We are glad to have you on board.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Welcome to Our App!",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    await fastmail.send_message(message)




