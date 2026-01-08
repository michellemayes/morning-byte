"""Email delivery for Kindle (Send-to-Kindle feature)."""

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from morning_byte.config import DeliveryConfig


class EmailDelivery:
    """Send EPUB files to Kindle via email.

    Amazon's Send-to-Kindle feature allows you to email documents
    to your Kindle device. Each Kindle has a unique email address
    (something@kindle.com).

    Setup:
    1. Find your Kindle email in Amazon account settings
    2. Add your sender email to the approved senders list
    3. Configure SMTP settings (Gmail with app password works well)
    """

    def __init__(self, config: DeliveryConfig):
        self.config = config

    def send(self, epub_path: Path, subject: str | None = None) -> bool:
        """Send an EPUB file to Kindle.

        Args:
            epub_path: Path to the EPUB file
            subject: Email subject (defaults to filename)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self._validate_config():
            return False

        if subject is None:
            subject = f"Morning Byte - {epub_path.stem}"

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.config.sender_email
            msg["To"] = self.config.kindle_email
            msg["Subject"] = subject

            # Add body
            body = "Your daily tech digest is attached."
            msg.attach(MIMEText(body, "plain"))

            # Attach EPUB
            with open(epub_path, "rb") as f:
                attachment = MIMEBase("application", "epub+zip")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename={epub_path.name}",
                )
                msg.attach(attachment)

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def _validate_config(self) -> bool:
        """Check if email configuration is valid."""
        required = [
            self.config.kindle_email,
            self.config.sender_email,
            self.config.smtp_user,
            self.config.smtp_password,
        ]
        return all(required)

    @staticmethod
    def get_setup_instructions() -> str:
        """Return instructions for setting up Kindle email delivery."""
        return """
Kindle Email Delivery Setup
============================

1. Find your Kindle email address:
   - Go to amazon.com → Account → Content & Devices → Preferences
   - Under "Personal Document Settings", find your Kindle email
   - It looks like: yourname_abc123@kindle.com

2. Add approved sender:
   - In the same settings page, add your sender email to
     "Approved Personal Document E-mail List"

3. Configure Gmail (recommended):
   - Enable 2-factor authentication on your Google account
   - Go to Google Account → Security → App Passwords
   - Generate an app password for "Mail"
   - Use this app password (not your regular password) in config

4. Set environment variables or config:
   KINDLE_EMAIL=yourname@kindle.com
   SENDER_EMAIL=you@gmail.com
   SMTP_USER=you@gmail.com
   SMTP_PASSWORD=your-app-password

Note: Amazon will automatically convert EPUB to Kindle format.
The document will appear in your Kindle library within minutes.
"""
