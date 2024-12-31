import boto3
from botocore.exceptions import ClientError
from flask import current_app as app
import logging

from main.utils.constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SES_SENDER_EMAIL

logger = logging.getLogger(__name__)

class SESEmailSender:
    def __init__(self):
        self.client = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )

    def send_reset_password_email(self, to_email: str, reset_url: str):
        """Send password reset email using Amazon SES"""
        try:
            # HTML version of the email
            html_content = f"""
            <html>
                <body>
                    <h2>Reset Your Password</h2>
                    <p>You requested to reset your password. Click the link below to set a new password:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """

            # Plain text version of the email
            text_content = f"""
            Reset Your Password

            You requested to reset your password. Click the link below to set a new password:
            {reset_url}

            This link will expire in 1 hour.

            If you didn't request this, please ignore this email.
            """

            response = self.client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message={
                    'Subject': {
                        'Data': 'Reset Your Password',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': text_content,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': html_content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            logger.info(f"Email sent! Message ID: {response['MessageId']}")
            return True

        except ClientError as e:
            logger.error(f"Failed to send email via SES: {str(e)}")
            raise