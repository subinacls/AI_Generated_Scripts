from twilio.rest import Client
import os
import datetime

# Global variable to store the log of last MMS sent
LAST_MMS_SENT = {}

class MMS_Sender:
    def __init__(self, twilio_sid, twilio_token, twilio_phone_number, recipient_phone_number):
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_phone_number = twilio_phone_number
        self.recipient_phone_number = recipient_phone_number

    def send_mms(self, image_path):
        global LAST_MMS_SENT  # Reference the global variable

        if not all([self.twilio_sid, self.twilio_token, self.twilio_phone_number, self.recipient_phone_number]):
            print("Twilio credentials or phone number missing. MMS not sent.")
            return

        client = Client(self.twilio_sid, self.twilio_token)
        message = client.messages.create(
            body="Unidentified face detected.",
            from_=self.twilio_phone_number,
            to=self.recipient_phone_number,
            media_url=["file:///" + os.path.abspath(image_path)]
        )

        print(f"MMS sent with SID: {message.sid}")

        # Update the LAST_MMS_SENT dictionary
        LAST_MMS_SENT[self.recipient_phone_number] = {
            'time': datetime.datetime.now(),
            'sid': message.sid,
            'image_path': os.path.abspath(image_path)
        }

# Example usage:
# sender = MMS_Sender('YOUR_TWILIO_SID', 'YOUR_TWILIO_TOKEN', 'YOUR_TWILIO_PHONE_NUMBER', 'RECIPIENT_PHONE_NUMBER')
# sender.send_mms('path/to/image.jpg')
