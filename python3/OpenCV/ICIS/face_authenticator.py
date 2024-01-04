import cv2
import numpy as np
import multiprocessing
from mtcnn.mtcnn import MTCNN
import face_recognition
import os
import pickle
import datetime
import time
import threading
import hashlib
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class FaceAuthenticator:
    def __init__(self, camera_indexes=[0], encoding_file='encodings.pkl', output_dir='output', twilio_sid=None, twilio_token=None, twilio_phone_number=None, recipient_phone_number=None, email_config=None, email_interval=60, motion_threshold=100, min_motion_area=700, global_encoding_file='global_encodings.pkl'):
        self.camera_indexes = camera_indexes
        self.encoding_file = encoding_file
        self.face_encodings = self.load_encodings()
        self.detector = MTCNN()
        self.output_dir = output_dir
        self.prev_frame = None
        self.motion_frames = []
        self.last_video_save_time = datetime.datetime.now()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.record_duration = 5  # duration in seconds for recording
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_phone_number = twilio_phone_number
        self.recipient_phone_number = recipient_phone_number
        self.running = multiprocessing.Value('i', 1)
        self.video_capture = cv2.VideoCapture(0)
        self.is_running = False
        self.thread = None
        self.last_email_sent = {}  # Dictionary to track last email sent time
        self.email_interval = email_interval or 60  # Time in seconds
        self.email_config = email_config or {
            'email': 'yoursender@domain.com',
            'password': 'SomePasswordHere1!',
            'recipient': 'targetemail@domain.com',
            'smtp_server': 'smtp.google.com',
            'smtp_port': 465
        }
        self.motion_threshold = motion_threshold
        self.min_motion_area = min_motion_area
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.face_tracker = FaceTracker(global_encoding_file)

    def send_email(self, subject, body, image_path):
        def email_task(subject, body, image_path):
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            if image_path:
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    img = MIMEImage(img_data, _subtype="jpeg")  # Specify the subtype
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    msg.attach(img)
            try:
                server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
                server.quit()
                print("Email sent successfully")
            except Exception as e:
                print("Failed to send email:", str(e))
        # Start the email sending task in a new thread
        thread = threading.Thread(target=email_task, args=(subject, body, image_path))
        thread.start()

    def send_mms(self, image_path):
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

    def get_face_identifier(self, face_frame):  
        # Convert face frame to a consistent format (e.g., grayscale) and resize
        resized_frame = cv2.resize(cv2.cvtColor(face_frame, cv2.COLOR_BGR2GRAY), (100, 100))
        # Compute a hash of the resized frame
        return hashlib.md5(resized_frame.tobytes()).hexdigest()

    def load_encodings(self):
        if os.path.exists(self.encoding_file):
            with open(self.encoding_file, 'rb') as file:
                return pickle.load(file)
        else:
            return {}

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.process_video, args=(1,))
            self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()
        self.video_capture.release()

    def process_video(self, camera_index):
        capture = cv2.VideoCapture(camera_index)
        recording = False
        start_time = None
        video_writer = None
        while self.is_running:
            ret, frame = self.video_capture.read()
            if ret:
                unknown_detected, frame = self.process_frame(frame, camera_index)
                current_time = datetime.datetime.now()
                if unknown_detected:
                    if not recording or (current_time - start_time).total_seconds() < self.record_duration:
                        if not recording:
                            start_time = current_time
                            video_writer = self.start_video_recording(frame, camera_index)
                    recording = True
                elif recording and (current_time - start_time).total_seconds() >= self.record_duration:
                    recording = False
                    video_writer.release()
                    video_writer = None
                if recording:
                    video_writer.write(frame)
        capture.release()
        if video_writer:
            video_writer.release()
        cv2.destroyWindow(f"Camera {camera_index}")

    def process_frame(self, frame, camera_index):
        unknown_detected = False
        # Motion Detection
        motion_detected = self.detect_motion(frame)
        if motion_detected:
            print("Motion detected on camera {}".format(camera_index))
            timestamped_frame = self.add_timestamp_to_frame(frame)
            self.motion_frames.append(timestamped_frame)
        # Save motion frames as video every minute
        if (datetime.datetime.now() - self.last_video_save_time).seconds >= 60:
            self.save_motion_frames_as_video(camera_index)
            self.motion_frames = []
            self.last_video_save_time = datetime.datetime.now()        
        # Track user across different streams
        self.face_tracker.update_encodings(frame)
        # Detect faces using MTCNN
        results = self.detector.detect_faces(frame)
        for result in results:
            x, y, width, height = result['box']
            face_frame = frame[y:y+height, x:x+width]
            rgb_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_frame)
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(list(self.face_encodings.values()), face_encoding)
                name = "Unknown"
                if True in matches:
                    print("Match detected on camera {}".format(camera_index))
                    first_match_index = matches.index(True)
                    name = list(self.face_encodings.keys())[first_match_index]
                else:
                    unknown_detected = True
                    current_time = datetime.datetime.now()
                    face_identifier = self.get_face_identifier(face_frame)  # Implement this method
                    if face_identifier not in self.last_email_sent or (current_time - self.last_email_sent[face_identifier]).total_seconds() > self.email_interval:
                        print("Unknown face detected on camera {}".format(camera_index))
                        self.last_email_sent[face_identifier] = current_time
                        image_path = os.path.join(self.output_dir, f"unknown_{camera_index}_{current_time.strftime('%Y%m%d_%H%M%S')}.jpg")
                        cv2.imwrite(image_path, frame)
                        self.send_email("Unknown Face Detected", "An unknown face has been detected.", image_path)
                        print("Unknown face from cam {} send via Email".format(camera_index))
                    self.save_unknown_user_image(frame, camera_index)
                    print("Unknown face detected on camera {} saved to disk {}".format(camera_index,  image_path))
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_3_channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        numpy_horizontal = np.hstack((frame, gray_3_channel))
        cv2.imshow(f"Camera {camera_index}", frame)
        cv2.imshow('Numpy Horizontal', numpy_horizontal)
        cv2.imshow('Gray scale', gray)
        cv2.imshow('3rd channel', gray_3_channel)
        cv2.waitKey(1)
        return unknown_detected, frame

    def save_unknown_user_image(self, frame, camera_index):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"unknown_{camera_index}_{timestamp}.jpg")
        cv2.imwrite(filename, frame)

    def start_video_recording(self, frame, camera_index):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"unknown_{camera_index}_{timestamp}.avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_height, frame_width = frame.shape[:2]
        return cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))

    def detect_motion(self, frame):
        # Convert frame to grayscale and apply Gaussian blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        cv2.imshow('GaussianBlur scale', gray)
        # Initialize prev_frame
        if self.prev_frame is None:
            self.prev_frame = gray
            return False
        mask = self.background_subtractor.apply(gray)
        fg_mask = cv2.GaussianBlur(mask, (21, 21), 0)
        cv2.imshow('MOG2 Background Subtractor Mask', fg_mask)
        _, thresh = cv2.threshold(fg_mask, self.motion_threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Iterate over contours
        for contour in contours:
            if cv2.contourArea(contour) < self.min_motion_area:
                continue
            return True
        self.prev_frame = fg_mask
        return False

    def add_timestamp_to_frame(self, frame):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), font, 0.5, (0, 0, 255), 1)
        return frame

    def save_motion_frames_as_video(self, camera_index):
        if len(self.motion_frames) == 0:
            return
        video_name = f"motion_{camera_index}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height, width, _ = self.motion_frames[0].shape
        video = cv2.VideoWriter(os.path.join(self.output_dir, video_name), fourcc, 2, (width, height))
        for frame in self.motion_frames:
            video.write(frame)
        video.release()

    def run(self):
        # Replace the threading Event with a multiprocessing Value for the running state
        self.running = multiprocessing.Value('i', 1)
        processes = []
        for index in self.camera_indexes:
            process = multiprocessing.Process(target=self.capture_frames, args=(index,))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()
