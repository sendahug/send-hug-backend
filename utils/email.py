import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

SG_CLIENT = SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
DEFAULT_FROM = "no-reply@send-hug.com"


def send(to: str, subject: str, content: str, from_email: str = DEFAULT_FROM):
    mail = Mail(Email(from_email), To(to), subject, Content("text/plain", content))
    # No types. Le sigh https://github.com/sendgrid/sendgrid-python/issues/956
    response = SG_CLIENT.client.mail.send.post(request_body=mail.get())  # type: ignore

    return response
