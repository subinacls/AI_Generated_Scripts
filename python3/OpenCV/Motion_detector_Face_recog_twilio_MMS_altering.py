import cv2
import multiprocessing
from mtcnn.mtcnn import MTCNN
import face_recognition
import os
import pickle
import datetime
import time
from twilio.rest import Client

class FaceAuthenticator:
    def __init__(self, camera_indexes=[0], encoding_file='encodings.pkl', output_dir='output', twilio_sid=None, twilio_token=None, twilio_phone_number=None, recipient_phone_number=None):
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
    def load_encodings(self):
        if os.path.exists(self.encoding_file):
            with open(self.encoding_file, 'rb') as file:
                return pickle.load(file)
        else:
            return {}
    def capture_frames(self, camera_index):
        capture = cv2.VideoCapture(camera_index)
        recording = False
        start_time = None
        video_writer = None
        while self.running.value:  # Changed from self.running.is_set() to self.running.value
            ret, frame = capture.read()
            if ret:
                unknown_detected, frame = self.process_frame(frame, camera_index)
                current_time = time.time()
                if unknown_detected and (not recording or (current_time - start_time < self.record_duration)):
                    if not recording:
                        start_time = current_time
                        video_writer = self.start_video_recording(frame, camera_index)
                    recording = True
                elif recording and current_time - start_time >= self.record_duration:
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
            timestamped_frame = self.add_timestamp_to_frame(frame)
            self.motion_frames.append(timestamped_frame)
        # Save motion frames as video every minute
        if (datetime.datetime.now() - self.last_video_save_time).seconds >= 60:
            self.save_motion_frames_as_video(camera_index)
            self.motion_frames = []
            self.last_video_save_time = datetime.datetime.now()        
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
                    first_match_index = matches.index(True)
                    name = list(self.face_encodings.keys())[first_match_index]
                else:
                    unknown_detected = True
                    self.save_unknown_user_image(frame, camera_index)
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow(f"Camera {camera_index}", frame)
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
        # Initialize prev_frame
        if self.prev_frame is None:
            self.prev_frame = gray
            return False
        # Compute the absolute difference between the current frame and previous frame
        frameDelta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # Dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Iterate over contours
        for c in contours:
            if cv2.contourArea(c) < 500:
                continue
            return True
        self.prev_frame = gray
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

def main():
    authenticator = FaceAuthenticator(
        camera_indexes=[0, 1],  # Adjust the camera indexes as needed
        twilio_sid='sid_token_here',
        twilio_token='auth_token_here',
        twilio_phone_number='twilio_tele_number',
        recipient_phone_number='your_mms_number'
    )
    authenticator.run()

if __name__ == '__main__':
    # This block ensures the safe spawning of the main process
    multiprocessing.set_start_method('spawn')  # This line might be necessary for some setups
    main()
