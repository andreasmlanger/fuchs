from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId)
from django.contrib.auth.models import User
from python_http_client.exceptions import HTTPError
import base64
from mysite.settings import config


# https://app.sendgrid.com/guide/integrate
SENDGRID_API_KEY = config.get('SENDGRID_API_KEY')


def send_email(to_email, subject, html_content, attachments=None):
    from_email = 'foxikachu@gmail.com'

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    if attachments is not None:
        for attached_file in attachments:
            message.attachment = attached_file

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    try:
        sg.send(message)
        print(f'Email sent to {to_email}')
    except HTTPError as e:
        print(e.to_dict)


def get_emails_of_superusers():
    superusers = User.objects.filter(is_superuser=True)
    superuser_emails = [user.email for user in superusers]
    return superuser_emails


def send_error_email(traceback):
    print(traceback)
    traceback = str(traceback).replace('\n', '<br>').replace('  ', '&nbsp;&nbsp;')
    html = f'<html><body><p>{traceback}</p></body></html>'
    for email in get_emails_of_superusers():
        send_email(email, 'An error has occurred on fuchs.render.com!', html)


def put_together_attachments(list_of_files):
    attachments = []
    for idx, path in enumerate(list_of_files):
        file = path.split('/')[-1]
        file_name, file_type = file.split('.')

        with open(path, 'rb') as f:
            data = f.read()
            f.close()
        encoded_file = base64.b64encode(data).decode()

        if file_type == 'png':
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(file),
                FileType('image/png'),
                Disposition('inline'),
                ContentId(f'attachment_{idx}')
            )
            attachments.append(attached_file)
    return attachments
