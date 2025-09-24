#!/usr/bin/env python3
"""
Face-Controlled Unlock System for Medical Dispenser
Integrates facial recognition with servo control for secure container access.

This script provides:
1. Face recognition authentication
2. Servo-controlled container unlocking
3. Integration with the existing user database
4. Web interface for face registration and unlock operations

Based on the Face Recognition using Raspberry Pi project:
https://github.com/kunalyelne/Face-Recognition-using-Raspberry-Pi
"""

import cv2
import numpy as np
import os
import sqlite3
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify

# Import existing modules
from face_recognition.face_recognition import FaceAuthenticator
from rpi_servo import get_servo_controller, cleanup_servo_controller

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'face_unlock_secret_key')

# Database configuration
DATABASE = 'users.db'

# Global servo controller instance
servo_controller = get_servo_controller()

class FaceUnlockSystem:
    """Main class for face-controlled unlock system"""
    
    def __init__(self):
        self.face_authenticator = FaceAuthenticator()
        self.servo_controller = servo_controller
        self.unlock_duration = 5  # seconds to keep container unlocked
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the face unlock system"""
        print("Initializing Face Unlock System...")
        
        # Initialize face recognition
        if not self.face_authenticator.initialize():
            print("Failed to initialize face recognition system")
            return False
        
        self.is_initialized = True
        print("✓ Face Unlock System initialized successfully")
        return True
    
    def unlock_container(self, user_id=None, username=None):
        """Unlock container using face recognition"""
        if not self.is_initialized:
            print("Face unlock system not initialized")
            return False, "System not initialized"
        
        print(f"Starting face authentication for container unlock...")
        
        # Perform face recognition
        success, recognized_user_id, recognized_username = self.face_authenticator.authenticate_user(
            expected_user_id=user_id, 
            timeout=30
        )
        
        if not success:
            return False, "Face recognition failed or user not authorized"
        
        if user_id is not None and recognized_user_id != user_id:
            return False, f"Face recognition mismatch: expected user ID {user_id}, got {recognized_user_id}"
        
        # Log the unlock event
        self.log_unlock_event(recognized_user_id, recognized_username)
        
        # Unlock the container
        print(f"✓ Face authentication successful for {recognized_username}")
        print("Unlocking container...")
        
        try:
            # Move servo to unlock position (90 degrees)
            self.servo_controller.servo1.ChangeDutyCycle(7.5)  # 90 degrees
            time.sleep(self.unlock_duration)
            
            # Move servo back to lock position (0 degrees)
            self.servo_controller.servo1.ChangeDutyCycle(2.5)  # 0 degrees
            time.sleep(0.5)
            self.servo_controller.servo1.ChangeDutyCycle(0)  # Stop PWM
            
            print(f"✓ Container unlocked for {self.unlock_duration} seconds")
            return True, f"Container unlocked successfully for {recognized_username}"
            
        except Exception as e:
            print(f"Error controlling servo: {e}")
            return False, f"Error unlocking container: {e}"
    
    def log_unlock_event(self, user_id, username):
        """Log unlock event to database"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Create unlock_log table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unlock_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    unlock_time DATETIME,
                    method TEXT DEFAULT 'face_recognition',
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Log the unlock event
            cursor.execute('''
                INSERT INTO unlock_log (user_id, username, unlock_time, method)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'face_recognition'))
            
            conn.commit()
            conn.close()
            print(f"✓ Unlock event logged for user {username}")
            
        except Exception as e:
            print(f"Error logging unlock event: {e}")
    
    def get_unlock_history(self, limit=10):
        """Get recent unlock history"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, unlock_time, method
                FROM unlock_log
                ORDER BY unlock_time DESC
                LIMIT ?
            ''', (limit,))
            
            history = cursor.fetchall()
            conn.close()
            return history
            
        except Exception as e:
            print(f"Error getting unlock history: {e}")
            return []

# Initialize the face unlock system
face_unlock_system = FaceUnlockSystem()

# Database initialization
def init_db():
    """Initialize database with unlock logging table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create unlock_log table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unlock_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            unlock_time DATETIME,
            method TEXT DEFAULT 'face_recognition',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Flask Routes
@app.route('/face_unlock')
def face_unlock_page():
    """Face unlock interface page"""
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))
    
    # Get unlock history
    unlock_history = face_unlock_system.get_unlock_history(10)
    
    return render_template('face_unlock.html', unlock_history=unlock_history)

@app.route('/unlock_container', methods=['POST'])
def unlock_container():
    """API endpoint to unlock container using face recognition"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    user_id = session['user_id']
    username = session.get('username', 'Unknown')
    
    try:
        # Perform face unlock
        success, message = face_unlock_system.unlock_container(user_id=user_id, username=username)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/emergency_unlock', methods=['POST'])
def emergency_unlock():
    """Emergency unlock without face recognition (admin only)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    try:
        username = session.get('username', 'Admin')
        user_id = session['user_id']
        
        # Log the emergency unlock
        face_unlock_system.log_unlock_event(user_id, f"{username} (Emergency)")
        
        # Unlock the container
        print("Emergency unlock activated by admin")
        face_unlock_system.servo_controller.servo1.ChangeDutyCycle(7.5)  # 90 degrees
        time.sleep(5)
        face_unlock_system.servo_controller.servo1.ChangeDutyCycle(2.5)  # 0 degrees
        time.sleep(0.5)
        face_unlock_system.servo_controller.servo1.ChangeDutyCycle(0)
        
        return jsonify({
            'success': True,
            'message': 'Emergency unlock activated'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/register_face')
def register_face_page():
    """Face registration page"""
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('register_face.html')

@app.route('/start_face_collection', methods=['POST'])
def start_face_collection():
    """Start face collection process"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session.get('username', '')
    
    try:
        # Start face collection in a separate thread
        def collect_faces():
            import subprocess
            result = subprocess.run([
                'python', 'face_dataset_collection.py', username
            ], cwd='face_recognition', capture_output=True, text=True)
            return result.returncode == 0
        
        # Run face collection
        success = collect_faces()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Face data collected for {username}. Please run training next.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Face collection failed. Please try again.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/train_faces', methods=['POST'])
def train_faces():
    """Train face recognition model"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        # Start training in a separate thread
        def train_model():
            import subprocess
            result = subprocess.run([
                'python', 'face_training.py'
            ], cwd='face_recognition', capture_output=True, text=True)
            return result.returncode == 0
        
        # Run training
        success = train_model()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Face recognition model trained successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Face training failed. Please check face data.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

def main():
    """Main function for standalone operation"""
    print("=" * 60)
    print("Medical Dispenser - Face Unlock System")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Initialize face unlock system
    if not face_unlock_system.initialize():
        print("Failed to initialize face unlock system")
        return
    
    print("\nFace unlock system ready!")
    print("Available commands:")
    print("1. 'unlock' - Unlock container using face recognition")
    print("2. 'test' - Test face recognition without unlocking")
    print("3. 'quit' - Exit the system")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                print("Shutting down face unlock system...")
                break
            elif command == 'unlock':
                print("Starting face unlock process...")
                success, message = face_unlock_system.unlock_container()
                print(f"Result: {message}")
            elif command == 'test':
                print("Testing face recognition...")
                success, user_id, username = face_unlock_system.face_authenticator.authenticate_user()
                if success:
                    print(f"✓ Face recognized: {username} (ID: {user_id})")
                else:
                    print("✗ Face recognition failed")
            else:
                print("Invalid command. Use 'unlock', 'test', or 'quit'")
                
        except KeyboardInterrupt:
            print("\nShutting down face unlock system...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    cleanup_servo_controller(servo_controller)
    print("Face unlock system shutdown complete.")

if __name__ == "__main__":
    main()