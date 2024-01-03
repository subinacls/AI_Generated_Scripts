import cv2

class MotionDetector:
    def __init__(self, motion_threshold=25, min_motion_area=500):
        self.prev_frame = None
        self.motion_threshold = motion_threshold
        self.min_motion_area = min_motion_area
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

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

# Example usage:
# detector = MotionDetector()
# frame = cv2.imread('path/to/image.jpg')  # Replace with actual frame capture
# motion_detected = detector.detect_motion(frame)
# print("Motion Detected:", motion_detected)
