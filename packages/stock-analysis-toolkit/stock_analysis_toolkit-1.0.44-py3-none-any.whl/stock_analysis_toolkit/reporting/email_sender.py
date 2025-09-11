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
        logger.info(f"EmailSender initialized for server={smtp_server}, port={smtp_port}, username={username}")

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
        attachments: Optional[List[Union[str, Path]]] = None,
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
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                from_name=from_name,
            )

            # Attach files if provided
            if attachments:
                for file in attachments:
                    try:
                        file_path = Path(file)
                        if not file_path.exists():
                            logger.warning(f"Attachment not found: {file}")
                            continue
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{file_path.name}"')
                        msg.attach(part)
                    except Exception as e:
                        logger.error(f"Failed to attach file {file}: {e}")

            # Connect to the SMTP server and send the email
            logger.info(f"Connecting to SMTP {self.smtp_server}:{self.smtp_port} (TLS)")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(0)
                code, resp = server.ehlo()
                logger.info(f"SMTP EHLO response: {code} {resp}")
                code, resp = server.starttls()
                logger.info(f"SMTP STARTTLS response: {code} {resp}")
                code, resp = server.ehlo()
                logger.info(f"SMTP EHLO(after TLS) response: {code} {resp}")
                logger.info(f"Attempting SMTP login as {self.username}")
                server.login(self.username, self.password)
                logger.info("SMTP login successful")

                # Prepare recipients list
                def normalize_emails(email_input):
                    if not email_input:
                        return []
                    # Sanitize the input to handle both strings and lists, and remove newlines
                    if isinstance(email_input, list):
                        email_input = ','.join(map(str, email_input))
                    
                    # Replace newlines and then split by comma
                    sanitized_string = str(email_input).replace('\n', ' ').replace('\r', '')
                    return [email.strip() for email in sanitized_string.split(',') if email.strip()]

                # Normalize all recipient lists
                to_emails = normalize_emails(to_email)
                cc_emails = normalize_emails(cc) if cc else []
                bcc_emails = normalize_emails(bcc) if bcc else []
                
                
                # Set headers on the message object just before sending
                msg['To'] = ', '.join(to_emails)
                if cc_emails:
                    msg['Cc'] = ', '.join(cc_emails)

                # Combine all recipients for the SMTP delivery envelope
                all_recipients = to_emails + cc_emails + bcc_emails
                
                # Send the email
                logger.info(f"Sending email to: {', '.join(all_recipients)}")
                server.send_message(msg, from_addr=self.username, to_addrs=all_recipients)

                # Log the successful email sending
                logger.info(f"Email sent to {', '.join(all_recipients)}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
        finally:
            socket.setdefaulttimeout(original_timeout)  # Restore original timeout

