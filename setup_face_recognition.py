#!/usr/bin/env python3
"""
Face Recognition Setup Script - Main Directory
Medical Dispenser - Face Recognition Setup

This script runs the face recognition setup from the main directory.
"""

import os
import sys
import subprocess

def main():
    """Run the face recognition setup"""
    print("=" * 60)
    print("🔧 MEDICAL DISPENSER - FACE RECOGNITION SETUP")
    print("=" * 60)
    print()
    
    # Change to face_recognition directory and run setup
    face_recognition_dir = 'face_recognition'
    
    if not os.path.exists(face_recognition_dir):
        print(f"❌ Face recognition directory not found: {face_recognition_dir}")
        print("Please ensure the face_recognition folder exists in the current directory.")
        return False
    
    print(f"Running face recognition setup from {face_recognition_dir}/ directory...")
    print()
    
    try:
        # Run the setup script from the face_recognition directory
        result = subprocess.run([
            sys.executable, 'setup_face_recognition.py'
        ], cwd=face_recognition_dir)
        
        if result.returncode == 0:
            print("\n✅ Face recognition setup completed successfully!")
            print("\nNext steps:")
            print("1. cd face_recognition")
            print("2. python face_dataset_collection.py <your_username>")
            print("3. python face_training.py")
            print("4. python face_recognition.py")
            print("5. python ../Medical_with_RPI.py")
        else:
            print("\n❌ Face recognition setup failed!")
            
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()