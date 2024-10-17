import smtplib, threading, uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings

# Logger information object
import logging
logger = logging.getLogger('yummypiv')

# Konfigurasi
smtp_server = settings.MAIL_HOST
smtp_port = settings.SMTP_PORT
default_username = settings.DEFAULT_MAIL_USERNAME
default_password = settings.DEFAULT_MAIL_PASSWORD
default_sender = f'{settings.DEFAULT_MAIL_USERNAME}@{settings.MAIL_DOMAIN}'


body = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: black;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: black;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
        }
        p {
            font-size: 16px;
            line-height: 1.5;
            color: #555;
        }
        .footer {
            margin-top: 20px;
            font-size: 14px;
            color: #888;
        }
        .footer .cs {
            margin-top: 5px;            
            color: black;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>No content mail template</h1>
        <p>Empty body,</p>
        <p>Please contact support@systema.id for more information.</p>
        <p class="footer">Tim Layanan Pelanggan</p>
        <p class="footer cs">Tim Layanan Pelanggan</p>
    </div>
</body>
</html>
"""

def _send_mail(sender=default_sender, username=default_username, password=default_password, receipt=None, subject=None, content=None):
    # Buat pesan
    msg = MIMEMultipart()
    msg['Message-ID'] = str(uuid.uuid4()) + '@' + settings.MAIL_DOMAIN
    msg['From'] = sender
    msg['To'] = receipt
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    # Kirim email
    try:
        # Menghubungkan ke server SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Menggunakan TLS
            server.login(username, password)  # Login
            server.send_message(msg)  # Mengirim email
        logger.info(f'Mail alert sent.')
    except Exception as e:
        logger.error(f'Failed to sending mail alert! - please check mail server')
        print(f"Terjadi kesalahan saat kirim mail: {e}")
    

def send_mail(sender=default_sender, username=default_username, password=default_password, receipt=None, subject=None, content=None):
    _mail_thread = threading.Thread(target=_send_mail, args=(sender, username, password, receipt, subject, content,))
    _mail_thread.start()
