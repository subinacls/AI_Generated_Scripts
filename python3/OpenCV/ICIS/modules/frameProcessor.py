import cv2
import datetime
import os
import face_recognition
from mtcnn.mtcnn import MTCNN

class FrameProcessor:
    def __init__(self, output_dir, email_interval, face_encodings):
        self.motion_frames = []
        self.last_video_save_time = datetime.datetime.now()
        self.output_dir = output_dir
        self.email_interval = email_interval
        self.face_encodings = face_encodings
        self.last_email_sent = {}
        self.detector = MTCNN()

    def detect_motion(self, frame):
        # Implement the motion detection logic
        # For now, let's assume it always returns False
        return False

    def process_frame(self, frame, camera_index):
        unknown_detected = False

        # Motion Detection
        motion_detected = self.detect_motion(frame)
        if motion_detected:
            print(f"Motion detected on camera {camera_index}")
            timestamped_frame = self.add_timestamp_to_frame(frame)  # Implement this method
            self.motion_frames.append(timestamped_frame)

        # Save motion frames as video every minute
        if (datetime.datetime.now() - self.last_video_save_time).seconds >= 60:
            self.save_motion_frames_as_video(camera_index)  # Implement this method
            self.motion_frames = []
            self.last_video_save_time = datetime.datetime.now()

        # Face Detection
        unknown_detected = self.detect_and_handle_faces(frame, camera_index)

        # Display Frames
        self.display_frames(frame, camera_index)

        return unknown_detected, frame

    def detect_and_handle_faces(self, frame, camera_index):
        unknown_detected = False
        results = self.detector.detect_faces(frame)
        for result in results:
            x, y, width, height = result['box']
            face_frame = frame[y:y+height, x:x+width]
            rgb_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_frame)
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(list(self.face_encodings.values()), face_encoding)
                unknown_detected |= self.handle_face_detection(matches, face_encoding, frame, camera_index, x, y, width, height)
        return unknown_detected

    def handle_face_detection(self, matches, face_encoding, frame, camera_index, x, y, width, height):
        # Implement the logic to handle face detection and unknown face processing
        # This includes email sending, image saving, etc.
        pass

    def display_frames(self, frame, camera_index):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow(f"Raw Video Feed Camera {camera_index}", frame)
        cv2.imshow(f"Gray Scale Video Feed Camera {camera_index}", gray)
        cv2.waitKey(1)

# Example usage
# output_dir = "path/to/output/dir"
# email_interval = 60  # seconds
# face_encodings = {}  # populate with known face encodings
# processor = FrameProcessor(output_dir, email_interval, face_encodings)

# frame = cv2.imread('path/to/frame.jpg')  # Replace with actual frame
# camera_index = 1
# unknown_detected, processed_frame = processor.process_frame(frame, camera_index)
