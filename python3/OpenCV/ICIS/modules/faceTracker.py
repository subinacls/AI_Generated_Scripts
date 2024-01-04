
import face_recognition
import pickle
import os

class FaceTracker:
    def __init__(self, encoding_file='global_encodings.pkl'):
        self.encoding_file = encoding_file
        self.global_encodings = self.load_encodings()

    def load_encodings(self):
        if os.path.exists(self.encoding_file):
            with open(self.encoding_file, 'rb') as file:
                return pickle.load(file)
        else:
            return {}

    def save_encodings(self):
        with open(self.encoding_file, 'wb') as file:
            pickle.dump(self.global_encodings, file)

    def update_encodings(self, frame):
        rgb_frame = frame[:, :, ::-1]  # Convert frame to RGB
        face_locations = face_recognition.face_locations(rgb_frame)
        new_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in new_encodings:
            is_known_face = False
            for known_encoding in self.global_encodings.values():
                matches = face_recognition.compare_faces([known_encoding], encoding)
                if True in matches:
                    is_known_face = True
                    break
            
            if not is_known_face:
                # Add new face encoding with a unique identifier
                face_id = len(self.global_encodings) + 1
                self.global_encodings[f"unknown_{face_id}"] = encoding

        self.save_encodings()
