#!/usr/bin/env python
"""
Test script to diagnose video reading and face detection issues
"""

import cv2
import numpy as np
from pathlib import Path
from mtcnn import MTCNN
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_reading():
    """Test if videos can be read from dataset"""
    print("\n" + "="*60)
    print("TESTING VIDEO READING")
    print("="*60)
    
    dataset_path = Path("../dataset")
    real_path = dataset_path / "DeepFakeDetection"
    
    if not real_path.exists():
        print(f"ERROR: Dataset path not found: {real_path}")
        return False
    
    video_files = sorted(real_path.glob("*.mp4"))[:5]  # Test first 5
    print(f"Found {len(sorted(real_path.glob('*.mp4')))} videos total")
    print(f"Testing {len(video_files)} videos...\n")
    
    for video_file in video_files:
        print(f"Testing: {video_file.name}")
        
        try:
            cap = cv2.VideoCapture(str(video_file))
            
            if not cap.isOpened():
                print(f"  ✗ Cannot open video - codec issue or corrupted file")
                continue
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"  ✓ Video opened successfully")
            print(f"    - Frames: {total_frames}")
            print(f"    - Resolution: {width}x{height}")
            print(f"    - FPS: {fps}")
            
            # Try to read first frame
            ret, frame = cap.read()
            if ret:
                print(f"    ✓ First frame read successfully (shape: {frame.shape})")
                
                # Try face detection on first frame
                print(f"    Testing face detection on first frame...")
                detector = MTCNN()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                detections = detector.detect_faces(frame_rgb)
                if detections:
                    print(f"    ✓ {len(detections)} face(s) detected!")
                    for i, det in enumerate(detections):
                        print(f"      Face {i+1}: confidence={det['confidence']:.2f}")
                else:
                    print(f"    ✗ No faces detected in first frame")
            else:
                print(f"    ✗ Could not read first frame")
            
            cap.release()
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        print()

def test_face_detection():
    """Test face detection on sample frames"""
    print("\n" + "="*60)
    print("TESTING FACE DETECTION")
    print("="*60)
    
    detector = MTCNN()
    
    # Create a sample image with visible face features
    sample_img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Draw some face-like features
    cv2.circle(sample_img, (60, 70), 20, (255, 200, 150), -1)  # Left eye region
    cv2.circle(sample_img, (160, 70), 20, (255, 200, 150), -1)  # Right eye region
    cv2.ellipse(sample_img, (110, 120), (50, 60), 0, 0, 360, (255, 200, 150), -1)  # Face shape
    
    print("Testing MTCNN on synthetic face image...")
    detections = detector.detect_faces(sample_img)
    print(f"  Detections: {len(detections)}")
    
    # Try with a real frame from video
    dataset_path = Path("../dataset")
    real_path = dataset_path / "DeepFakeDetection"
    video_file = sorted(real_path.glob("*.mp4"))[0]
    
    print(f"\nTesting MTCNN on real video frame from {video_file.name}...")
    cap = cv2.VideoCapture(str(video_file))
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Test on original size
            print(f"  Original frame size: {frame_rgb.shape}")
            detections = detector.detect_faces(frame_rgb)
            print(f"  Detections on original: {len(detections)}")
            
            # Test on smaller size (might be clearer)
            small_frame = cv2.resize(frame_rgb, (320, 240))
            print(f"  Resized frame size: {small_frame.shape}")
            detections_small = detector.detect_faces(small_frame)
            print(f"  Detections on resized: {len(detections_small)}")
        
        cap.release()

if __name__ == "__main__":
    print("\nDEEPFAKE DETECTION - VIDEO AND FACE DETECTION DIAGNOSTIC")
    print("=" * 60)
    
    test_video_reading()
    test_face_detection()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
