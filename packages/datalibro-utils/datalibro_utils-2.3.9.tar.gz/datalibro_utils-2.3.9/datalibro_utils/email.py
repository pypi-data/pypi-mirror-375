import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(subject:str, body:str, send_email_address:str, send_email_password:str, receive_email_address:str, attachment_path=None, attachment_list=None, smtp_address='smtp.feishu.cn', smtp_port=465):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = send_email_address
    msg['To'] = receive_email_address
    msg['Subject'] = subject

    # Add body text
    msg.attach(MIMEText(body, 'plain'))
    if attachment_path is not None and attachment_list is not None:
        # Add multiple attachments
        attachment_paths = [os.path.join(attachment_path, attachment) for attachment in attachment_list]
        for each_path in attachment_paths:
            attachment_filename = each_path.split("/")[-1]
            with open(each_path, "rb") as f:
                attach = MIMEApplication(f.read(), Name=attachment_filename)
            attach['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
            msg.attach(attach)

    # Send the email
    with smtplib.SMTP_SSL(smtp_address, smtp_port) as server:
        server.login(send_email_address, send_email_password)
        server.sendmail(send_email_address, receive_email_address, msg.as_string())
