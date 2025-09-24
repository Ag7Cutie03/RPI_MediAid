#!/usr/bin/env python3
"""
Setup Script for Face Recognition System
Medical Dispenser - Face Recognition Setup

This script helps set up the face recognition system by:
1. Checking system requirements
2. Creating necessary directories
3. Downloading required cascade files
4. Testing camera access
5. Providing setup instructions

Based on the Face Recognition using Raspberry Pi project:
https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi
"""

import os
import sys
import subprocess
import urllib.request
import cv2
import sqlite3

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_required_packages():
    """Check if required packages are installed"""
    print("\nChecking required packages...")
    required_packages = [
        'cv2',
        'numpy',
        'PIL',
        'sqlite3',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"✅ OpenCV version: {cv2.__version__}")
            elif package == 'numpy':
                import numpy
                print(f"✅ NumPy version: {numpy.__version__}")
            elif package == 'PIL':
                from PIL import Image
                print(f"✅ Pillow (PIL) is available")
            elif package == 'sqlite3':
                import sqlite3
                print("✅ SQLite3 is available")
            elif package == 'flask':
                import flask
                print(f"✅ Flask version: {flask.__version__}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating necessary directories...")
    directories = [
        '../face_dataset',
        '../face_trainer'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def download_cascade_file():
    """Download Haar cascade file for face detection"""
    print("\nChecking Haar cascade file...")
    cascade_file = 'haarcascade_frontalface_default.xml'
    
    if os.path.exists(cascade_file):
        print(f"✅ Cascade file already exists: {cascade_file}")
        return True
    
    print("Downloading Haar cascade file...")
    cascade_url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
    
    try:
        urllib.request.urlretrieve(cascade_url, cascade_file)
        print(f"✅ Downloaded cascade file: {cascade_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to download cascade file: {e}")
        print("Please manually download the file from:")
        print("https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml")
        return False

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not accessible")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Could not read from camera")
            cap.release()
            return False
        
        print("✅ Camera is working properly")
        cap.release()
        return True
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def check_database():
    """Check if user database exists"""
    print("\nChecking user database...")
    database_file = '../users.db'
    
    if not os.path.exists(database_file):
        print(f"❌ Database file not found: {database_file}")
        print("Please run the main application first to create the database")
        return False
    
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database exists with {user_count} users")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_face_detection():
    """Test face detection functionality"""
    print("\nTesting face detection...")
    cascade_file = 'haarcascade_frontalface_default.xml'
    
    if not os.path.exists(cascade_file):
        print(f"❌ Cascade file not found: {cascade_file}")
        return False
    
    try:
        face_cascade = cv2.CascadeClassifier(cascade_file)
        if face_cascade.empty():
            print("❌ Failed to load cascade classifier")
            return False
        
        print("✅ Face detection cascade loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("🎯 FACE RECOGNITION SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. 📸 REGISTER YOUR FACE:")
    print("   - Run: python face_dataset_collection.py <your_username>")
    print("   - Look at the camera and wait for 30 samples to be collected")
    print("   - Example: python face_dataset_collection.py john_doe")
    print()
    print("2. 🧠 TRAIN THE MODEL:")
    print("   - Run: python face_training.py")
    print("   - This will train the recognition model on your face data")
    print()
    print("3. 🧪 TEST RECOGNITION:")
    print("   - Run: python face_recognition.py")
    print("   - This will test if face recognition is working")
    print()
    print("4. 🌐 USE WEB INTERFACE:")
    print("   - Start the main application: python Medical_with_RPI.py")
    print("   - Go to: http://localhost:5000")
    print("   - Login and use 'Register Face' and 'Face Unlock' features")
    print()
    print("Note: All face recognition scripts should be run from the face_recognition/ directory")
    print()
    print("5. 🔧 TROUBLESHOOTING:")
    print("   - Ensure good lighting when collecting face data")
    print("   - Keep your face centered and look directly at camera")
    print("   - Remove glasses/hat if possible for better recognition")
    print("   - Run this setup script again if you encounter issues")
    print()
    print("="*60)

def main():
    """Main setup function"""
    print("="*60)
    print("🔧 MEDICAL DISPENSER - FACE RECOGNITION SETUP")
    print("="*60)
    print()
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Directories", create_directories),
        ("Cascade File", download_cascade_file),
        ("Camera Access", test_camera),
        ("Database", check_database),
        ("Face Detection", test_face_detection)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 SETUP SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Face recognition system is ready to use.")
        print_setup_instructions()
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Check camera permissions and USB connection")
        print("- Ensure you're running the main application first")
        print("- Run this script as administrator if needed")

if __name__ == "__main__":
    main()