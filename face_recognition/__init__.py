"""
Face Recognition Package for Medical Dispenser

This package contains all the face recognition training and testing components.
"""

from .face_recognition import FaceAuthenticator
from .face_dataset_collection import collect_face_data, get_user_id_from_username
from .face_training import train_face_recognizer, verify_training

__all__ = [
    'FaceAuthenticator',
    'collect_face_data', 
    'get_user_id_from_username',
    'train_face_recognizer',
    'verify_training'
]