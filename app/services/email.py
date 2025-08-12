# app/services/email.py

import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

from app.services.auth import auth_service
from app.conf.config import get_settings

settings = get_settings()

# Load Jinja2 environment to work with HTML templates
env = Environment(loader=FileSystemLoader('templates'))


async def send_email(email: str, username: str, host: str):
    """
    Sends a verification email to a new user.
    """
    try:
        # Generate a unique token for email verification.
        token_verification = auth_service.create_email_token({"sub": email})

        # Build the verification link using the host and the generated token.
        # Виправлено: видаляємо кінцевий слеш з хоста, щоб уникнути подвійних слешів
        clean_host = host.rstrip('/')
        verification_link = f"{clean_host}/api/auth/confirmed_email/{token_verification}"

        # Load the HTML template for the email from the 'templates' folder.
        template = env.get_template('email_verification_template.html')

        # Render the template with the user's data and the verification link.
        html_content = template.render(
            username=username,
            verification_link=verification_link
        )

        # Create an EmailMessage object.
        message = EmailMessage()
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message["Subject"] = "Email Verification"
        message.set_content(html_content, subtype='html')

        # Connect to the SMTP server and send the email asynchronously.
        # Використовуємо порт 587 і start_tls=True
        async with aiosmtplib.SMTP(
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                start_tls=True
        ) as server:
            await server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            await server.send_message(message)

        print(f"Verification email sent to {email}")

    except Exception as e:
        print(f"Failed to send email to {email}: {e}")


async def send_password_reset_email(email: str, username: str, host: str, token_reset: str):
    """
    Sends a password reset email to a user.
    """
    try:
        # Load the HTML template for the email from the 'templates' folder.
        template = env.get_template('password_reset_template.html')

        # Render the template with the user's data and the password reset token.
        html_content = template.render(
            username=username,
            token=token_reset
        )

        # Create an EmailMessage object.
        message = EmailMessage()
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message["Subject"] = "Password Reset Request"
        message.set_content(html_content, subtype='html')

        # Connect to the SMTP server and send the email asynchronously.
        # Використовуємо порт 587 і start_tls=True
        async with aiosmtplib.SMTP(
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                start_tls=True
        ) as server:
            await server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            await server.send_message(message)

        print(f"Password reset email sent to {email}")

    except Exception as e:
        print(f"Failed to send password reset email to {email}: {e}")
