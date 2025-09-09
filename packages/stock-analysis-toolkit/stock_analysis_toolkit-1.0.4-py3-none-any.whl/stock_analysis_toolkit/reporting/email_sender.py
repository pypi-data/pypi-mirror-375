"""
Email notification module.

This module provides functionality to send stock analysis reports
via email with HTML formatting and attachments.
"""

import logging
import os
import smtplib
import socket
from datetime import datetime
import html2text
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape


logger = logging.getLogger(__name__)


class EmailSender:
    """
    Handles sending emails with reports and notifications.

    This class provides methods to send emails with HTML content
    and file attachments, specifically designed for sending
    stock analysis reports.
    """

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        Initialize the email sender with SMTP credentials.

        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP server port (e.g., 465 for SSL)
            username: Email username for authentication
            password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

        # Initialize template environment
        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
        )

        # Define format_currency filter
        def format_currency(value, is_percent=False):
            if value is None or value == "":
                return "N/A"

            # Convert string to float if needed
            try:
                if isinstance(value, str):
                    value = float(value.replace(",", ""))  # Handle numbers with commas
                value = float(value)  # Ensure it's a float
            except (ValueError, TypeError):
                return str(value)  # Return as-is if conversion fails

            if is_percent:
                return f"{value:.2%}"

            abs_value = abs(value)
            if abs_value >= 1e12:  # Trillions
                return f"₹{value/1e12:.2f}T"
            if abs_value >= 1e9:  # Billions
                return f"₹{value/1e9:.2f}B"
            if abs_value >= 1e6:  # Millions
                return f"₹{value/1e6:.2f}M"
            if abs_value >= 1e3:  # Thousands
                return f"₹{value/1e3:.2f}K"
            return f"₹{value:.2f}"

        # Initialize Jinja2 environment with the filter
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Set default template to the new template
        self.default_template = "email_template_new.html"

        # Register the filter
        self.template_env.filters["format_currency"] = format_currency

    def _create_message(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> MIMEMultipart:
        """
        Create a MIME message with optional HTML, text, and attachments.

        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text alternative (optional)
            attachments: List of file paths to attach
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to email address
            from_name: Display name for the sender

        Returns:
            MIMEMultipart: The constructed email message
        """
        # Convert single strings to lists
        if isinstance(to_email, str):
            to_email = [to_email]
        if isinstance(cc, str):
            cc = [cc]
        if isinstance(bcc, str):
            bcc = [bcc]

        # Create the root message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        from_header = f'"{from_name}" <{self.username}>' if from_name else self.username
        msg["From"] = from_header
        to_emails = ", ".join(to_email) if isinstance(to_email, list) else to_email
        msg["To"] = to_emails

        if cc:
            msg["Cc"] = ", ".join(cc) if isinstance(cc, list) else cc
        if bcc:
            msg["Bcc"] = ", ".join(bcc) if isinstance(bcc, list) else bcc

        # Create the main alternative part for text/plain and text/html
        msg_alternative = MIMEMultipart("alternative")

        # Add text part if provided
        if text_content:
            part_text = MIMEText(text_content, "plain")
            msg_alternative.attach(part_text)

        # Create a related part for the HTML and inline images
        msg_related = MIMEMultipart("related")

        # Add HTML part to the related part
        part_html = MIMEText(html_content, "html")
        msg_related.attach(part_html)

        # Track which attachments we've processed to avoid duplicates
        processed_attachments = set()

        # Process all attachments (including inline images)
        if attachments:
            for attachment_info in attachments:
                file_path = Path(attachment_info["path"])
                if not file_path.exists():
                    logger.warning(f"Attachment not found: {file_path}")
                    continue

                try:
                    with open(file_path, "rb") as fp:
                        file_data = fp.read()

                    is_image = file_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif")
                    is_inline = attachment_info.get("inline", False)

                    if is_image and is_inline:
                        image = MIMEImage(file_data, _subtype=file_path.suffix[1:].lower())
                        content_id = attachment_info.get("content_id", file_path.stem)
                        image.add_header('Content-ID', f'<{content_id}>')
                        image.add_header('Content-Disposition', 'inline', filename=file_path.name)
                        msg_related.attach(image)
                    else:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(file_data)
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=file_path.name,
                        )
                        msg.attach(part)

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}", exc_info=True)

        # Add the related part to the alternative part
        msg_alternative.attach(msg_related)

        # Add the alternative part to the root message
        msg.attach(msg_alternative)

        return msg

    def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        template_name: str = None,
        context: Optional[Dict[str, Any]] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
        from_name: Optional[str] = "Stock Analysis Pro",
    ) -> bool:
        """
        Send an email using a template.

        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            template_name: Name of the template file (in templates/email/)
            context: Dictionary with template variables
            text_content: Plain text alternative (auto-generated from HTML
                if not provided)
            attachments: List of file paths to attach
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to email address
            from_name: Display name for the sender

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        original_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(30)  # Set a 30-second global timeout
            # If html_content is provided directly, use it; otherwise use template
            if html_content is None:
                # Prepare context
                context = context or {}
                now = datetime.now()
                context.update(
                    {
                        "subject": subject,
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "year": now.year,
                        "now": now,  # Add this for direct datetime access in template
                        "recipient": (
                            to_email[0] if isinstance(to_email, list) else to_email
                        ),
                        **context,
                    }
                )

                # Use default template if none specified
                template_to_use = template_name or self.default_template

                # Load and render template
                template = self.template_env.get_template(template_to_use)
                html_content = template.render(**context)

            # If no text content provided, create a simple version from HTML
            if not text_content and html_content:
                # Simple HTML to text conversion
                text_content = html2text.html2text(html_content)

            # Create the message
            msg = self._create_message(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                from_name=from_name,
            )

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.username, self.password)

                # Prepare recipients list
                recipients = [to_email] if isinstance(to_email, str) else to_email
                if cc:
                    recipients.extend(cc if isinstance(cc, list) else [cc])
                if bcc:
                    recipients.extend(bcc if isinstance(bcc, list) else [bcc])

                # Send the email
                server.send_message(msg, from_addr=self.username, to_addrs=recipients)

                # Log the successful email sending
                logger.info(
                    f"Email sent to {to_email} with {len(attachments or [])} "
                    "attachments"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
        finally:
            socket.setdefaulttimeout(original_timeout)  # Restore original timeout

    def send_report(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        from_name: Optional[str] = "Stock Analysis Pro",
    ) -> bool:
        """
        Send a pre-generated analysis report via email.

        Args:
            to_email: Recipient email address(es).
            subject: Email subject.
            html_content: The HTML body of the email.
            attachments: A list of file paths to attach.
            cc: CC recipient(s).
            bcc: BCC recipient(s).
            from_name: Display name for the sender.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            # The attachments are expected to be a list of paths
            # We need to convert them to the format expected by `_create_message`
            attachment_list = []
            if attachments:
                for path in attachments:
                    p = Path(path)
                    attachment_list.append({
                        "path": p,
                        "inline": True,
                        "content_id": p.stem
                    })

            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                attachments=attachment_list,
                cc=cc,
                bcc=bcc,
                from_name=from_name,
            )
        except Exception as e:
            logger.error(f"Failed to send report: {e}", exc_info=True)
            return False
