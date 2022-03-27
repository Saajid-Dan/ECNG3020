from app import app
import traceback
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(subject, body):
    '''
    This function sends emails using SendGrid's API
    '''
    message = Mail(                                     # Create email
    from_email=app.config['MAIL_DEFAULT_SENDER'],       # Sender
    to_emails=app.config['MAIL_DEFAULT_SENDER'],        # Receiver
    subject=subject,                                    # email subject
    html_content=body)                                  # email body

    sg = SendGridAPIClient(app.config['MAIL_PASSWORD'])     # SendGrid's API
    response = sg.send(message)                             # send email

def email_exception(e, subject):
    '''
    This function writes an email body with error exception
    '''
    traceback_msg = traceback.format_exc()                              # traceback
    error = "Error: " + str(e) + "<br><br>Traceback: " + traceback_msg      # email body
    send_email(subject, error)