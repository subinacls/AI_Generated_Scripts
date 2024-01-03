import cv2
import datetime
import os
import numpy as np
import face_recognition
from mtcnn.mtcnn import MTCNN

class FrameProcessor:
    def __init__(self, output_dir, email_interval, detector, face_encodings):
        self.motion_frames = []
        self.last_video_save_time = datetime.datetime.now()
        self.output_dir = output_dir
        self.email_interval = email_interval
        self.detector = detector  # MTCNN detector
        self.face_encodings = face_encodings
        self.last_email_sent = {}
        self.motion_detector = MotionDetector() 

    def process_frame(self, frame, camera_index):
        unknown_detected = False
        # Motion Detection
        motion_detected = self.motion_detector.detect_motion(frame)
        if motion_detected:
            print(f"Motion detected on camera {camera_index}")
            timestamped_frame = self.add_timestamp_to_frame(frame)
            self.motion_frames.append(timestamped_frame)

        # Save motion frames as video
        if (datetime.datetime.now() - self.last_video_save_time).seconds >= 60:
            self.save_motion_frames_as_video(camera_index) 
            self.motion_frames = []
            self.last_video_save_time = datetime.datetime.now()

        # Face Detection
        results = self.detector.detect_faces(frame)
        unknown_detected = self.process_faces(results, frame, camera_index)

        # Additional Frame Processing
        self.display_processed_frames(frame, camera_index)

        return unknown_detected, frame

    def process_faces(self, results, frame, camera_index):
        unknown_detected = False
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
        # Code to handle face detection, email sending and drawing rectangles on the frame
        # Needs to be implemented, to keep PoC driven data minmal not integrated at this time
        pass

    def display_processed_frames(self, frame, camera_index):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_3_channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        numpy_horizontal = np.hstack((frame, gray_3_channel))
        cv2.imshow(f"Camera {camera_index}", frame)
        cv2.imshow('Numpy Horizontal', numpy_horizontal)
        cv2.imshow('Gray scale', gray)
        cv2.imshow('3rd channel', gray_3_channel)
        cv2.waitKey(1)

# Example usage
# Initialize necessary components like detector, face_encodings, etc.
# output_dir = "path/to/output/dir"
# email_interval = 60  # seconds
# detector = MTCNN()
# face_encodings = {}  # populate with known face encodings
# processor = FrameProcessor(output_dir, email_interval, detector, face_encodings)

# frame = cv2.imread('path/to/frame.jpg')  # Replace with actual frame
# camera_index = 1  # Example camera index
# unknown_detected, processed_frame = processor.process_frame(frame, camera_index)
