#!/usr/bin/env python3
"""
Face Training Script for Medical Dispenser
Based on the Face Recognition using Raspberry Pi project
https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi

This script trains the face recognizer using collected face data.
"""

import cv2
import numpy as np
import os
import sqlite3
from PIL import Image

# Database configuration
DATABASE = '../users.db'

def get_images_and_labels(dataset_path):
    """Get images and labels from the dataset directory"""
    image_paths = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path)]
    face_samples = []
    ids = []
    
    # Initialize face detector
    face_cascade_path = 'haarcascade_frontalface_default.xml'
    if not os.path.exists(face_cascade_path):
        print(f"Error: {face_cascade_path} not found!")
        return None, None
    
    detector = cv2.CascadeClassifier(face_cascade_path)
    
    print("Processing face images...")
    
    for image_path in image_paths:
        try:
            # Load image and convert to grayscale
            PIL_img = Image.open(image_path).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            
            # Extract user ID from filename (format: User.{id}.{count}.jpg)
            filename = os.path.split(image_path)[-1]
            user_id = int(filename.split(".")[1])
            
            # Detect faces in the image
            faces = detector.detectMultiScale(img_numpy)
            
            for (x, y, w, h) in faces:
                face_samples.append(img_numpy[y:y + h, x:x + w])
                ids.append(user_id)
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue
    
    return face_samples, ids

def get_username_from_id(user_id):
    """Get username from user ID"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else f"User_{user_id}"
    except Exception as e:
        print(f"Error getting username for ID {user_id}: {e}")
        return f"User_{user_id}"

def train_face_recognizer():
    """Train the face recognizer"""
    print("=" * 60)
    print("Medical Dispenser - Face Recognition Training")
    print("=" * 60)
    
    dataset_path = '../face_dataset'
    trainer_path = '../face_trainer'
    
    # Check if dataset directory exists
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset directory '{dataset_path}' not found!")
        print("Please run face_dataset_collection.py first to collect face data.")
        return False
    
    # Create trainer directory if it doesn't exist
    if not os.path.exists(trainer_path):
        os.makedirs(trainer_path)
        print(f"Created trainer directory: {trainer_path}")
    
    # Get images and labels
    face_samples, ids = get_images_and_labels(dataset_path)
    
    if not face_samples or not ids:
        print("Error: No face samples found in dataset!")
        print("Please collect face data first using face_dataset_collection.py")
        return False
    
    print(f"Found {len(face_samples)} face samples")
    print(f"Unique users: {len(set(ids))}")
    
    # Show user information
    unique_ids = list(set(ids))
    print("\nUsers in training data:")
    for user_id in unique_ids:
        username = get_username_from_id(user_id)
        sample_count = ids.count(user_id)
        print(f"  - {username} (ID: {user_id}): {sample_count} samples")
    
    # Create recognizer
    print("\nTraining face recognizer...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    try:
        # Train the recognizer
        recognizer.train(face_samples, np.array(ids))
        
        # Save the model
        trainer_file = os.path.join(trainer_path, 'trainer.yml')
        recognizer.write(trainer_file)
        
        print(f"✓ Training completed successfully!")
        print(f"✓ Model saved to: {trainer_file}")
        print(f"✓ Trained on {len(np.unique(ids))} users with {len(face_samples)} total samples")
        
        return True
        
    except Exception as e:
        print(f"Error during training: {e}")
        return False

def verify_training():
    """Verify the training results"""
    trainer_file = '../face_trainer/trainer.yml'
    
    if not os.path.exists(trainer_file):
        print("Error: Trainer file not found!")
        return False
    
    try:
        # Load the recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainer_file)
        
        print("✓ Trainer file loaded successfully")
        print("✓ Face recognition model is ready for use")
        return True
        
    except Exception as e:
        print(f"Error verifying trainer: {e}")
        return False

def main():
    """Main function"""
    print("Starting face recognition training process...")
    
    # Train the recognizer
    success = train_face_recognizer()
    
    if success:
        # Verify training
        print("\nVerifying training results...")
        verify_success = verify_training()
        
        if verify_success:
            print("\n" + "=" * 60)
            print("Face recognition training completed successfully!")
            print("The system is now ready for face-based authentication.")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Test face recognition: python face_recognition.py")
            print("2. Use face authentication in the web interface")
            print("=" * 60)
        else:
            print("\nTraining completed but verification failed.")
            print("Please check the trainer file and try again.")
    else:
        print("\n" + "=" * 60)
        print("Face recognition training failed!")
        print("Please ensure you have collected face data first.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    main()