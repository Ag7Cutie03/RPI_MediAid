#!/usr/bin/env python3
"""
Face Dataset Collection Script for Medical Dispenser
Based on the Face Recognition using Raspberry Pi project
https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi

This script captures face images for user registration in the medical dispenser system.
"""

import cv2
import os
import sys
import sqlite3

# Database configuration
DATABASE = '../users.db'

def get_user_id_from_username(username):
    """Get user ID from username"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def collect_face_data(username):
    """Collect face data for a specific user"""
    print(f"Starting face data collection for user: {username}")
    
    # Get user ID
    user_id = get_user_id_from_username(username)
    if not user_id:
        print(f"Error: User '{username}' not found in database.")
        return False
    
    # Create dataset directory if it doesn't exist
    dataset_dir = '../face_dataset'
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
        print(f"Created dataset directory: {dataset_dir}")
    
    # Initialize face detector
    face_cascade_path = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(face_cascade_path):
        print(f"Error: {face_cascade_path} not found!")
        print("Please download the Haar cascade file from OpenCV repository")
        return False
    
    face_detector = cv2.CascadeClassifier(face_cascade_path)
    
    # Initialize camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not open camera")
        return False
    
    # Set camera properties
    cam.set(3, 640)  # width
    cam.set(4, 480)  # height
    
    print(f"\nFace data collection for user ID: {user_id}")
    print("Look at the camera and wait for face detection...")
    print("Press 'ESC' to exit or wait for 30 samples to be collected")
    
    # Initialize individual sampling face count
    count = 0
    sample_limit = 30
    
    while True:
        ret, img = cam.read()
        if not ret:
            print("Error: Could not read from camera")
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around detected face
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            count += 1
            # Save the captured image into the datasets folder
            filename = f"User.{user_id}.{count}.jpg"
            filepath = os.path.join(dataset_dir, filename)
            cv2.imwrite(filepath, gray[y:y + h, x:x + w])
            
            # Display count on image
            cv2.putText(img, f"Sample {count}/{sample_limit}", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        # Display the image
        cv2.imshow('Face Data Collection', img)
        
        # Check for exit conditions
        k = cv2.waitKey(100) & 0xff
        if k == 27:  # ESC key
            print("\nFace collection interrupted by user")
            break
        elif count >= sample_limit:
            print(f"\nFace collection completed! {sample_limit} samples collected")
            break
    
    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    
    if count >= 10:  # Minimum samples for training
        print(f"✓ Face data collection successful!")
        print(f"✓ Collected {count} face samples for user {username}")
        return True
    else:
        print(f"✗ Insufficient face samples collected ({count}/10 minimum)")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python face_dataset_collection.py <username>")
        print("Example: python face_dataset_collection.py john_doe")
        sys.exit(1)
    
    username = sys.argv[1]
    
    print("=" * 60)
    print("Medical Dispenser - Face Dataset Collection")
    print("=" * 60)
    
    # Check if user exists in database
    if not get_user_id_from_username(username):
        print(f"Error: User '{username}' not found in database.")
        print("Please register the user first through the web interface.")
        sys.exit(1)
    
    # Start face collection
    success = collect_face_data(username)
    
    if success:
        print("\n" + "=" * 60)
        print("Face dataset collection completed successfully!")
        print("Next steps:")
        print("1. Run: python face_training.py")
        print("2. Test face recognition with: python face_recognition.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Face dataset collection failed!")
        print("Please try again with better lighting and ensure your face is visible.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()