import os
import params
import time
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email import encoders
import re

def authenticate_gmail():
    """Authenticates the user and returns a Gmail API service object."""
    creds = None
    if os.path.exists(params.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(params.TOKEN_PATH, params.SCOPES)
        params.logger.info("Loaded credentials from file.")
    else:
        params.logger.info("No credentials file found.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            params.logger.info("Credentials refreshed.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(params.CRED_PATH, params.SCOPES)
            creds = flow.run_local_server(port=0)
            params.logger.info("New credentials obtained.")

        with open(params.TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
            params.logger.info(f"Credentials saved to {params.TOKEN_PATH}.")

    return build("gmail", "v1", credentials=creds)

def get_unread_emails(service):
    """Fetches all unread emails."""
    result = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
    unread_emails = result.get("messages", [])
    params.logger.info(f"Messages found : {unread_emails}")
    params.logger.info(f"Found {len(unread_emails)} unread email(s)")
    return unread_emails

def mark_as_read(service, email_id):
    """Marks an email as read."""
    # Mark email as read
    params.logger.info(f"Marking email as read: {email_id}")
    service.users().messages().modify(
        userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()

def process_email(service, email_id):
    processed_email = []

    """Processes an email: extracts sender, downloads only PNG/JPG/JPEG attachments, and marks it as read."""
    
    msg = service.users().messages().get(userId="me", id=email_id).execute()
    time.sleep(1)
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    sender = "Unknown"
    for header in headers:
        if header["name"] == "From":
            sender = header["value"]
        
    if sender == "Unknown":
        params.logger.error("Failed to extract sender from email.")
        raise ValueError("Failed to extract sender from email.")

    # Check for attachments
    parts = payload.get("parts", [])
    valid_attachments = [part for part in parts if part.get("filename", "").lower().endswith((".png", ".jpg", ".jpeg"))]

    if len(valid_attachments) > 1:
        params.logger.error("Email has more than one valid image attachment.")
        raise ValueError("Email has more than one valid image attachment.")
        
    for part in parts:
        if part.get("filename"):
            filename = part.get("filename", "").lower()
            attachment_id = part["body"].get("attachmentId")
            attachment_data = service.users().messages().attachments().get(
                userId="me", messageId=email_id, id=attachment_id
            ).execute()
            time.sleep(1)

            file_data = base64.urlsafe_b64decode(attachment_data["data"])
            file_path = os.path.join(params.SAVE_FOLDER, filename)

            with open(file_path, "wb") as file:
                file.write(file_data)
            params.logger.info(f"Attachment saved: {file_path}")

            # Save sender and file path in the global list
            params.logger.info(f"Id: {email_id}, sender: {sender}, file_path: {file_path}")
            processed_email = {"sender": sender, "file_path": file_path}

            # Mark email as read
            mark_as_read(service, email_id)
            time.sleep(1)
    
    return processed_email

def send_emailback(service, sender, response, filepath=None):
    params.logger.info(f"Sending email back to: {sender}")
    """Sends an email back to the sender with the relationship."""
    subject = "Re: Arbol Genealogico"
    body = response

    match = re.search(r'<([^<>]+)>', sender)
    if match:
        sender_email = match.group(1)  # Extrae solo el email
    else:
        sender_email = sender  # En caso de que ya sea solo el email

    # Create the MIMEText email message
    message = MIMEMultipart()
    message["to"] = sender_email
    message["subject"] = subject
    message.attach(MIMEText(body))

    if filepath:
        try:
            # Open the file in binary mode
            with open(filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")  # This is for binary files
                part.set_payload(attachment.read())  # Read the image file
                encoders.encode_base64(part)  # Encode the file as base64
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filepath.split('/')[-1]}",  # Get the filename from the filepath
                )
                part.add_header("Content-Type", "image/png")  # Ensure it's a PNG file
                message.attach(part)  # Attach the image file to the email
        except Exception as e:
            params.logger.error(f"Failed to send email to {sender_email}: {e}")


    # Encode message in base64 for Gmail API
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send email using Gmail API
    try:
        service.users().messages().send(
            userId="me", body={"raw": encoded_message}
        ).execute()
        time.sleep(1)
        params.logger.info(f"Reply sent to: {sender_email}")
    except Exception as e:
        params.logger.error(f"Failed to send email to {sender_email}: {e}")
    
    if filepath:
        os.remove(filepath)
        params.logger.info(f"Removed tree file: {filepath}")