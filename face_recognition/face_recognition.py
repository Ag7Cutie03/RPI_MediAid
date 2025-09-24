#!/usr/bin/env python3
"""
Face Recognition Script for Medical Dispenser
Based on the Face Recognition using Raspberry Pi project
https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi

This script performs face recognition for authentication in the medical dispenser system.
"""

import cv2
import numpy as np
import os
import sqlite3
import time

# Database configuration
DATABASE = '../users.db'

class FaceAuthenticator:
    """Face authentication class for the medical dispenser"""
    
    def __init__(self):
        self.recognizer = None
        self.face_cascade = None
        self.camera = None
        self.names = {}
        self.confidence_threshold = 70  # Confidence threshold for recognition
        
    def initialize(self):
        """Initialize the face recognition system"""
        print("Initializing face recognition system...")
        
        # Check if trainer file exists
        trainer_file = '../face_trainer/trainer.yml'
        if not os.path.exists(trainer_file):
            print(f"Error: Trainer file '{trainer_file}' not found!")
            print("Please run face_training.py first to train the recognizer.")
            return False
        
        # Check if cascade file exists
        cascade_file = 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_file):
            print(f"Error: Cascade file '{cascade_file}' not found!")
            return False
        
        try:
            # Initialize recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read(trainer_file)
            
            # Initialize face cascade
            self.face_cascade = cv2.CascadeClassifier(cascade_file)
            
            # Load user names from database
            self.load_user_names()
            
            print("✓ Face recognition system initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing face recognition: {e}")
            return False
    
    def load_user_names(self):
        """Load user names from database"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users')
            users = cursor.fetchall()
            conn.close()
            
            # Create names dictionary (0-based indexing for OpenCV)
            self.names = {0: 'Unknown'}
            for user_id, username in users:
                self.names[user_id] = username
            
            print(f"Loaded {len(self.names)-1} users for face recognition")
            
        except Exception as e:
            print(f"Error loading user names: {e}")
            self.names = {0: 'Unknown'}
    
    def start_camera(self):
        """Initialize camera"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Set camera properties
        self.camera.set(3, 640)  # width
        self.camera.set(4, 480)  # height
        
        return True
    
    def recognize_face(self, timeout=30):
        """Recognize face with timeout"""
        if not self.start_camera():
            return None, None
        
        print(f"Face recognition started. Timeout: {timeout} seconds")
        print("Look at the camera for face recognition...")
        print("Press 'ESC' to cancel")
        
        start_time = time.time()
        min_confidence = 100  # Track best confidence
        best_match = None
        
        while True:
            ret, img = self.camera.read()
            if not ret:
                print("Error: Could not read from camera")
                break
            
            # Flip image horizontally for mirror effect
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Recognize face
                id, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
                
                # Update best match if confidence is better
                if confidence < min_confidence:
                    min_confidence = confidence
                    best_match = id
                
                # Get user name
                if id in self.names:
                    user_name = self.names[id]
                else:
                    user_name = "Unknown"
                
                # Display recognition result
                if confidence < self.confidence_threshold:
                    confidence_percent = round(100 - confidence)
                    cv2.putText(img, f"{user_name}", (x + 5, y - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, f"{confidence_percent}%", (x + 5, y + h - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
                else:
                    cv2.putText(img, "Unknown", (x + 5, y - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, f"{round(100 - confidence)}%", (x + 5, y + h - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
            
            # Display status
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            cv2.putText(img, f"Time: {remaining}s", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            cv2.imshow('Face Recognition', img)
            
            # Check for exit conditions
            k = cv2.waitKey(10) & 0xff
            if k == 27:  # ESC key
                print("Face recognition cancelled by user")
                break
            elif remaining <= 0:
                print("Face recognition timeout reached")
                break
            
            # Check if we have a good match
            if best_match and min_confidence < self.confidence_threshold:
                # Wait a moment to confirm the match
                time.sleep(1)
                final_ret, final_img = self.camera.read()
                if final_ret:
                    final_gray = cv2.cvtColor(final_img, cv2.COLOR_BGR2GRAY)
                    final_faces = self.face_cascade.detectMultiScale(final_gray, 1.2, 5, minSize=(30, 30))
                    
                    for (x, y, w, h) in final_faces:
                        final_id, final_confidence = self.recognizer.predict(final_gray[y:y + h, x:x + w])
                        if final_id == best_match and final_confidence < self.confidence_threshold:
                            user_name = self.names.get(final_id, "Unknown")
                            print(f"✓ Face recognized: {user_name} (confidence: {round(100 - final_confidence)}%)")
                            return final_id, user_name
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        
        # Return best match if found
        if best_match and min_confidence < self.confidence_threshold:
            user_name = self.names.get(best_match, "Unknown")
            print(f"✓ Face recognized: {user_name} (confidence: {round(100 - min_confidence)}%)")
            return best_match, user_name
        else:
            print("✗ Face not recognized or confidence too low")
            return None, None
    
    def authenticate_user(self, expected_user_id=None, timeout=30):
        """Authenticate a specific user or any registered user"""
        user_id, username = self.recognize_face(timeout)
        
        if user_id is None:
            return False, None, None
        
        if expected_user_id is not None:
            if user_id == expected_user_id:
                return True, user_id, username
            else:
                print(f"✗ Face recognition failed: Expected user ID {expected_user_id}, got {user_id}")
                return False, user_id, username
        else:
            return True, user_id, username

def main():
    """Main function for testing face recognition"""
    print("=" * 60)
    print("Medical Dispenser - Face Recognition Test")
    print("=" * 60)
    
    # Initialize face authenticator
    authenticator = FaceAuthenticator()
    
    if not authenticator.initialize():
        print("Failed to initialize face recognition system")
        return
    
    print("\nStarting face recognition test...")
    print("This will test face recognition for any registered user.")
    
    # Test face recognition
    success, user_id, username = authenticator.authenticate_user()
    
    if success:
        print(f"\n✓ Authentication successful!")
        print(f"✓ User ID: {user_id}")
        print(f"✓ Username: {username}")
    else:
        print(f"\n✗ Authentication failed!")
        if user_id is not None:
            print(f"  Recognized user ID: {user_id}")
            print(f"  Recognized username: {username}")

if __name__ == "__main__":
    main()