import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

class sendEmail:
    def __init__(self, email_config=None, email_interval=60):
        global LAST_EMAIL_SENT = {}  # Application wide dict() to track last email sent
        self.email_interval = email_interval or 60  # Time in seconds
        self.email_config = email_config or {
            'email': 'yoursender@domain.com',
            'password': 'SomePasswordHere1!',
            'recipient': 'targetemail@domain.com',
            'smtp_server': 'smtp.google.com',
            'smtp_port': 465,
            'useTLS': True,
        }

    def email_task(self, subject, body, image_path=None):
        # Run the email sending task in a separate thread
        email_thread = threading.Thread(target=self._send_email, args=(subject, body, image_path))
        email_thread.start()

    def _send_email(self, subject, body, image_path=None):
        msg = MIMEMultipart()
        msg['From'] = self.email_config['email']
        msg['To'] = self.email_config['recipient']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if image_path:
            with open(image_path, 'rb') as f:
                img_data = f.read()
                img = MIMEImage(img_data, _subtype="jpeg")
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                msg.attach(img)
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            if self.email_config['useTLS']:
                server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print("Failed to send email:", str(e))

# email_sender = sendEmail()
# email_sender.email_task("Subject Here", "Body of the email", "path/to/image.jpg")
