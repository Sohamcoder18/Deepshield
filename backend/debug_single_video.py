#!/usr/bin/env python
"""Debug single video processing"""

import cv2
import numpy as np
from pathlib import Path
from mtcnn import MTCNN
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize face detectors
print("Initializing face detectors...")
mtcnn_detector = MTCNN()
haar_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def extract_faces_from_frame(frame):
    """Extract face regions from a frame using MTCNN with Haar Cascade fallback"""
    try:
        # Convert BGR to RGB for MTCNN
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Try MTCNN first
        detections = mtcnn_detector.detect_faces(frame_rgb)
        print(f"  MTCNN detections: {len(detections)}")
        
        faces = []
        for detection in detections:
            x, y, w, h = detection['box']
            # Ensure coordinates are within image bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, frame_rgb.shape[1] - x)
            h = min(h, frame_rgb.shape[0] - y)
            
            if w > 0 and h > 0:
                face = frame_rgb[y:y+h, x:x+w]
                if face.size > 0:
                    # Resize to standard size
                    face = cv2.resize(face, (224, 224))
                    faces.append(face)
        
        # If MTCNN found faces, return them
        if faces:
            print(f"  Returning {len(faces)} MTCNN faces")
            return faces
        
        # Fallback to Haar Cascade if MTCNN found nothing
        print("  MTCNN found no faces, trying Haar Cascade...")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        haar_faces = haar_cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
        print(f"  Haar Cascade detections: {len(haar_faces)}")
        
        for (x, y, w, h) in haar_faces:
            face = frame_rgb[y:y+h, x:x+w]
            if face.size > 0:
                face = cv2.resize(face, (224, 224))
                faces.append(face)
        
        return faces if faces else None
        
    except Exception as e:
        print(f"  Face extraction error: {str(e)}")
        return None

def extract_frames(video_path, num_frames=10):
    """Extract evenly spaced frames from video"""
    frames = []
    try:
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"Could not open video: {video_path}")
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames in video: {total_frames}")
        
        if total_frames < num_frames:
            print(f"Video has fewer frames than requested: {total_frames} < {num_frames}")
            num_frames = total_frames
        
        # Calculate frame indices to extract
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        print(f"Extracting frame indices: {frame_indices}")
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                frames.append(frame)
                print(f"  Extracted frame {idx}")
            else:
                print(f"  Failed to extract frame {idx}")
        
        cap.release()
        
        return frames if len(frames) > 0 else None
    except Exception as e:
        print(f"Error extracting frames from {video_path}: {str(e)}")
        return None

# Test with first video
dataset_path = Path("../dataset")
video_file = sorted((dataset_path / "DeepFakeDetection").glob("*.mp4"))[0]

print(f"\nTesting with video: {video_file.name}")
print("=" * 60)

print("\n1. Extracting frames...")
frames = extract_frames(str(video_file), num_frames=5)

if frames is None:
    print("ERROR: Could not extract frames!")
else:
    print(f"Successfully extracted {len(frames)} frames")
    
    print("\n2. Processing frames for faces...")
    total_faces = 0
    for frame_idx, frame in enumerate(frames):
        print(f"\nFrame {frame_idx}:")
        faces = extract_faces_from_frame(frame)
        
        if faces:
            total_faces += len(faces)
            print(f"  Total faces in this frame: {len(faces)}")
        else:
            print(f"  No faces detected")
    
    print(f"\n\nTotal faces extracted from all frames: {total_faces}")
