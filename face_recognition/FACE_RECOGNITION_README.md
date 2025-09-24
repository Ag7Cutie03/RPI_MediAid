# 🔒 Face Recognition System for Medical Dispenser

This document describes the face recognition system integrated into the Medical Dispenser project, based on the [Face Recognition using Raspberry Pi](https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi) implementation.

## 📋 Overview

The face recognition system provides secure access control for the medical dispenser container using facial authentication. Users can register their faces and then use face recognition to unlock the container and access their medications.

## 🏗️ System Architecture

### Components

1. **Face Dataset Collection** (`face_dataset_collection.py`)
   - Captures multiple face images for training
   - Stores images in `face_dataset/` directory
   - Links face data to user accounts in the database

2. **Face Training** (`face_training.py`)
   - Trains the LBPH (Local Binary Patterns Histograms) recognizer
   - Creates recognition model stored in `face_trainer/trainer.yml`
   - Supports multiple users

3. **Face Recognition** (`face_recognition.py`)
   - Performs real-time face recognition
   - Integrates with user database
   - Provides authentication API

4. **Face Unlock System** (`face_unlock_system.py`)
   - Combines face recognition with servo control
   - Manages container unlocking
   - Logs unlock events
   - Provides web interface

5. **Web Interface**
   - Face registration page (`templates/register_face.html`)
   - Face unlock interface (`templates/face_unlock.html`)
   - Integration with main dashboard

## 🚀 Quick Start

### 1. System Setup

Run the setup script to check system requirements:

```bash
python setup_face_recognition.py
```

### 2. Register Your Face

```bash
python face_dataset_collection.py <your_username>
```

Example:
```bash
python face_dataset_collection.py john_doe
```

### 3. Train the Model

```bash
python face_training.py
```

### 4. Test Recognition

```bash
python face_recognition.py
```

### 5. Use Web Interface

Start the main application:
```bash
python Medical_with_RPI.py
```

Navigate to:
- **Register Face**: http://localhost:5000/register_face
- **Face Unlock**: http://localhost:5000/face_unlock

## 📁 File Structure

```
MedDispenser/
├── face_dataset_collection.py    # Face data collection script
├── face_training.py              # Face recognition training
├── face_recognition.py           # Face recognition engine
├── face_unlock_system.py         # Face unlock system
├── setup_face_recognition.py     # Setup and testing script
├── haarcascade_frontalface_default.xml  # Face detection cascade
├── face_dataset/                 # Collected face images
│   └── User.{id}.{count}.jpg
├── face_trainer/                 # Trained models
│   └── trainer.yml
└── templates/
    ├── register_face.html        # Face registration interface
    └── face_unlock.html          # Face unlock interface
```

## 🔧 Technical Details

### Face Recognition Algorithm

- **Algorithm**: LBPH (Local Binary Patterns Histograms)
- **Library**: OpenCV's `cv2.face.LBPHFaceRecognizer_create()`
- **Training**: 30 samples per user (configurable)
- **Confidence Threshold**: 70% (configurable)

### Database Integration

The system integrates with the existing SQLite database:

```sql
-- Unlock event logging
CREATE TABLE unlock_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    unlock_time DATETIME,
    method TEXT DEFAULT 'face_recognition',
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Servo Control Integration

Face recognition triggers servo motor control:

```python
# Unlock sequence
servo_controller.servo1.ChangeDutyCycle(7.5)  # 90 degrees (unlock)
time.sleep(5)  # Keep unlocked for 5 seconds
servo_controller.servo1.ChangeDutyCycle(2.5)  # 0 degrees (lock)
```

## 🎯 Usage Guide

### For Users

1. **First Time Setup**:
   - Login to the web interface
   - Go to "Register Face" page
   - Follow the 3-step process:
     - Collect face data (30 samples)
     - Train recognition model
     - Test recognition

2. **Daily Usage**:
   - Go to "Face Unlock" page
   - Click "Unlock Container with Face Recognition"
   - Look at the camera for authentication
   - Container unlocks automatically upon recognition

### For Administrators

- **Emergency Unlock**: Available on face unlock page for admin users
- **Unlock History**: View recent unlock events
- **User Management**: Standard user management applies to face recognition

## 🔒 Security Features

1. **User Authentication**: Face recognition tied to user accounts
2. **Access Control**: Users can only unlock for themselves (unless admin)
3. **Audit Logging**: All unlock events are logged with timestamps
4. **Confidence Thresholding**: Low-confidence matches are rejected
5. **Emergency Override**: Admin emergency unlock for critical situations

## ⚙️ Configuration

### Adjustable Parameters

In `face_unlock_system.py`:

```python
# Confidence threshold for recognition (lower = more strict)
self.confidence_threshold = 70

# How long to keep container unlocked (seconds)
self.unlock_duration = 5

# Timeout for face recognition (seconds)
timeout = 30
```

In `face_dataset_collection.py`:

```python
# Number of face samples to collect
sample_limit = 30
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not found**:
   ```bash
   # Check camera permissions
   ls /dev/video*
   
   # Test camera access
   python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
   ```

2. **Face not detected**:
   - Ensure good lighting
   - Remove glasses/hat
   - Look directly at camera
   - Check camera focus

3. **Low recognition accuracy**:
   - Re-collect face data with better lighting
   - Adjust confidence threshold
   - Ensure face is centered in frame during collection

4. **Training fails**:
   - Check if face data exists in `face_dataset/` directory
   - Ensure at least 10 samples per user
   - Verify database connectivity

### Debug Mode

Enable debug output by modifying the confidence threshold:

```python
# In face_unlock_system.py
self.confidence_threshold = 50  # Lower threshold for testing
```

## 📊 Performance

### Benchmarks

- **Face Detection**: ~30ms per frame
- **Face Recognition**: ~50ms per prediction
- **Total Recognition Time**: ~2-5 seconds (including user positioning)
- **Training Time**: ~10-30 seconds (depending on dataset size)

### Optimization Tips

1. **Lighting**: Ensure consistent, good lighting
2. **Camera Position**: Fixed camera position improves accuracy
3. **Face Angle**: Collect data from multiple angles for robustness
4. **Sample Quality**: Higher quality samples improve recognition

## 🔄 Integration with Main System

The face recognition system integrates seamlessly with the existing Medical Dispenser:

### New Routes Added

- `/face_unlock` - Face unlock interface
- `/register_face` - Face registration interface
- `/unlock_container` - API endpoint for face unlock
- `/emergency_unlock` - Admin emergency unlock
- `/start_face_collection` - Start face data collection
- `/train_faces` - Train recognition model

### Database Extensions

- `unlock_log` table for audit trail
- Integration with existing `users` table

### UI Integration

- New buttons on dashboard for face features
- Face unlock and registration pages
- Emergency unlock for administrators

## 🚀 Future Enhancements

Potential improvements for the face recognition system:

1. **Multiple Recognition Methods**: Support for different algorithms
2. **Anti-Spoofing**: Liveness detection to prevent photo attacks
3. **Multi-Factor Authentication**: Combine face with PIN/password
4. **Cloud Integration**: Store face data securely in cloud
5. **Mobile App**: Face registration and unlock via mobile
6. **Advanced Analytics**: Recognition accuracy tracking and improvement

## 📚 References

- [Original Face Recognition Project](https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi)
- [OpenCV Face Recognition Documentation](https://docs.opencv.org/master/da/d60/tutorial_face_main.html)
- [LBPH Algorithm Paper](https://ieeexplore.ieee.org/document/1221218)

## 🤝 Contributing

When contributing to the face recognition system:

1. Test with multiple users and lighting conditions
2. Ensure backward compatibility with existing system
3. Add appropriate error handling and logging
4. Update documentation for any new features
5. Consider security implications of changes

## 📄 License

This face recognition system follows the same license as the main Medical Dispenser project.