#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Test Script for All Deepfake Detection Models
Tests video, image, and audio deepfake detection models
"""

import os
import sys
import cv2
import numpy as np
import librosa
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from tensorflow import keras
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.xception import Xception
    print("[OK] TensorFlow/Keras imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import TensorFlow: {e}")
    sys.exit(1)

try:
    from mtcnn import MTCNN
    print("[OK] MTCNN imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import MTCNN: {e}")
    sys.exit(1)


class DeepfakeModelTester:
    """Test all trained deepfake detection models"""
    
    def __init__(self, models_dir="./models"):
        """Initialize model tester"""
        self.models_dir = Path(models_dir)
        self.models = {}
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'video_tests': [],
            'image_tests': [],
            'audio_tests': []
        }
        
        # Initialize face detector
        logger.info("Initializing MTCNN face detector...")
        self.mtcnn = MTCNN()
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load all models
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        logger.info("\n" + "="*70)
        logger.info("LOADING TRAINED MODELS")
        logger.info("="*70)
        
        model_files = {
            'video': 'xceptionnet_model.h5',
            'image': 'efficientnet_model.h5',
            'audio': 'audio_model.h5'
        }
        
        for model_type, filename in model_files.items():
            filepath = self.models_dir / filename
            
            if filepath.exists():
                try:
                    model = load_model(str(filepath))
                    self.models[model_type] = model
                    logger.info(f"[OK] {model_type.upper()} model loaded: {filepath}")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to load {model_type} model: {e}")
            else:
                # Load pretrained models from Keras
                if model_type == 'video':
                    try:
                        model = Xception(weights='imagenet', include_top=True)
                        self.models[model_type] = model
                        logger.info(f"[OK] {model_type.upper()} model loaded: Pretrained XceptionNet (ImageNet)")
                    except Exception as e:
                        logger.error(f"[ERROR] Failed to load pretrained {model_type} model: {e}")
                else:
                    logger.warning(f"[MISSING] {model_type.upper()} model not found: {filepath}")
    
    def extract_faces_from_frame(self, frame):
        """Extract faces from a frame"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Try MTCNN first
            detections = self.mtcnn.detect_faces(frame_rgb)
            
            faces = []
            for detection in detections:
                x, y, w, h = detection['box']
                x, y = max(0, x), max(0, y)
                w = min(w, frame_rgb.shape[1] - x)
                h = min(h, frame_rgb.shape[0] - y)
                
                if w > 0 and h > 0:
                    face = frame_rgb[y:y+h, x:x+w]
                    if face.size > 0:
                        face = cv2.resize(face, (299, 299))
                        faces.append(face)
            
            if faces:
                return faces
            
            # Fallback to Haar Cascade
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            haar_faces = self.haar_cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
            
            for (x, y, w, h) in haar_faces:
                face = frame_rgb[y:y+h, x:x+w]
                if face.size > 0:
                    face = cv2.resize(face, (299, 299))
                    faces.append(face)
            
            return faces if faces else None
            
        except Exception as e:
            logger.error(f"Face extraction error: {e}")
            return None
    
    def test_video(self, video_path, num_frames=5):
        """Test video deepfake detection model"""
        logger.info("\n" + "="*70)
        logger.info(f"TESTING VIDEO MODEL: {Path(video_path).name}")
        logger.info("="*70)
        
        if 'video' not in self.models:
            logger.error("[ERROR] Video model not loaded")
            return None
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                logger.error(f"[ERROR] Cannot open video: {video_path}")
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Video info: {total_frames} total frames")
            
            if total_frames < num_frames:
                num_frames = total_frames
            
            # Extract frames
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            predictions = []
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"  Could not read frame {idx}")
                    continue
                
                # Extract faces
                faces = self.extract_faces_from_frame(frame)
                
                if not faces:
                    logger.warning(f"  No faces detected in frame {idx}")
                    continue
                
                # Preprocess and predict
                for face in faces:
                    face_normalized = face.astype(np.float32) / 255.0
                    face_expanded = np.expand_dims(face_normalized, axis=0)
                    
                    prediction = self.models['video'].predict(face_expanded, verbose=0)[0][0]
                    predictions.append(prediction)
                    logger.info(f"  Frame {idx}: Deepfake probability = {prediction:.4f}")
            
            cap.release()
            
            if predictions:
                avg_prediction = np.mean(predictions)
                std_prediction = np.std(predictions)
                
                result = {
                    'file': str(video_path),
                    'predictions': predictions,
                    'average': float(avg_prediction),
                    'std_dev': float(std_prediction),
                    'classification': 'DEEPFAKE' if avg_prediction > 0.5 else 'REAL'
                }
                
                logger.info(f"\n[VIDEO RESULT]")
                logger.info(f"  Average prediction: {avg_prediction:.4f}")
                logger.info(f"  Std deviation: {std_prediction:.4f}")
                logger.info(f"  Classification: {result['classification']}")
                logger.info(f"  Confidence: {max(avg_prediction, 1-avg_prediction)*100:.1f}%")
                
                self.results['video_tests'].append(result)
                return result
            else:
                logger.error("[ERROR] No faces detected in any frame")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Video test failed: {e}")
            return None
    
    def test_image(self, image_path):
        """Test image deepfake detection model"""
        logger.info("\n" + "="*70)
        logger.info(f"TESTING IMAGE MODEL: {Path(image_path).name}")
        logger.info("="*70)
        
        if 'image' not in self.models:
            logger.error("[ERROR] Image model not loaded")
            return None
        
        try:
            frame = cv2.imread(str(image_path))
            
            if frame is None:
                logger.error(f"[ERROR] Cannot read image: {image_path}")
                return None
            
            logger.info(f"Image loaded: {frame.shape}")
            
            # Extract faces
            faces = self.extract_faces_from_frame(frame)
            
            if not faces:
                logger.error("[ERROR] No faces detected in image")
                return None
            
            predictions = []
            
            # Predict for each face
            for i, face in enumerate(faces):
                face_normalized = face.astype(np.float32) / 255.0
                face_expanded = np.expand_dims(face_normalized, axis=0)
                
                prediction = self.models['image'].predict(face_expanded, verbose=0)[0][0]
                predictions.append(prediction)
                logger.info(f"  Face {i+1}: Deepfake probability = {prediction:.4f}")
            
            if predictions:
                avg_prediction = np.mean(predictions)
                
                result = {
                    'file': str(image_path),
                    'predictions': predictions,
                    'average': float(avg_prediction),
                    'classification': 'DEEPFAKE' if avg_prediction > 0.5 else 'REAL'
                }
                
                logger.info(f"\n[IMAGE RESULT]")
                logger.info(f"  Average prediction: {avg_prediction:.4f}")
                logger.info(f"  Classification: {result['classification']}")
                logger.info(f"  Confidence: {max(avg_prediction, 1-avg_prediction)*100:.1f}%")
                
                self.results['image_tests'].append(result)
                return result
            else:
                logger.error("[ERROR] No faces extracted from image")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Image test failed: {e}")
            return None
    
    def test_audio(self, audio_path):
        """Test audio deepfake detection model"""
        logger.info("\n" + "="*70)
        logger.info(f"TESTING AUDIO MODEL: {Path(audio_path).name}")
        logger.info("="*70)
        
        if 'audio' not in self.models:
            logger.error("[ERROR] Audio model not loaded")
            return None
        
        try:
            # Load audio
            logger.info("Loading audio file...")
            y, sr = librosa.load(str(audio_path), sr=22050)
            logger.info(f"Audio loaded: {len(y)} samples at {sr} Hz")
            
            # Extract MFCC features
            logger.info("Extracting MFCC features...")
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            mfcc = np.mean(mfcc.T, axis=0)
            
            logger.info(f"MFCC features shape: {mfcc.shape}")
            
            # Predict
            mfcc_expanded = np.expand_dims(mfcc, axis=0)
            prediction = self.models['audio'].predict(mfcc_expanded, verbose=0)[0][0]
            
            result = {
                'file': str(audio_path),
                'prediction': float(prediction),
                'classification': 'DEEPFAKE' if prediction > 0.5 else 'REAL'
            }
            
            logger.info(f"\n[AUDIO RESULT]")
            logger.info(f"  Prediction: {prediction:.4f}")
            logger.info(f"  Classification: {result['classification']}")
            logger.info(f"  Confidence: {max(prediction, 1-prediction)*100:.1f}%")
            
            self.results['audio_tests'].append(result)
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Audio test failed: {e}")
            return None
    
    def test_dataset_samples(self, dataset_root="../dataset", num_samples=3):
        """Test with samples from the dataset"""
        logger.info("\n" + "="*70)
        logger.info("TESTING WITH DATASET SAMPLES")
        logger.info("="*70)
        
        dataset_path = Path(dataset_root)
        
        if not dataset_path.exists():
            logger.error(f"[ERROR] Dataset not found: {dataset_path}")
            return
        
        # Test video samples
        logger.info("\nTesting VIDEO samples...")
        real_videos = sorted((dataset_path / "DeepFakeDetection").glob("*.mp4"))[:num_samples]
        fake_videos = sorted((dataset_path / "Deepfakes").glob("*.mp4"))[:num_samples]
        
        for video_file in real_videos:
            self.test_video(str(video_file), num_frames=3)
        
        for video_file in fake_videos:
            self.test_video(str(video_file), num_frames=3)
        
        logger.info("\n" + "="*70)
        logger.info("ALL TESTS COMPLETED")
        logger.info("="*70)
        
        self._print_summary()
        self._save_results()
    
    def _print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*70)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("="*70)
        
        logger.info(f"\nVideo Tests: {len(self.results['video_tests'])}")
        for result in self.results['video_tests']:
            logger.info(f"  {Path(result['file']).name}: {result['classification']} "
                       f"({result['average']:.4f})")
        
        logger.info(f"\nImage Tests: {len(self.results['image_tests'])}")
        for result in self.results['image_tests']:
            logger.info(f"  {Path(result['file']).name}: {result['classification']} "
                       f"({result['average']:.4f})")
        
        logger.info(f"\nAudio Tests: {len(self.results['audio_tests'])}")
        for result in self.results['audio_tests']:
            logger.info(f"  {Path(result['file']).name}: {result['classification']} "
                       f"({result['prediction']:.4f})")
    
    def _save_results(self):
        """Save test results to JSON file"""
        results_file = Path("test_results.json")
        
        try:
            # Convert numpy types to Python native types for JSON serialization
            import json
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    if isinstance(obj, (np.floating, np.float32, np.float64)):
                        return float(obj)
                    if isinstance(obj, (np.integer, np.int32, np.int64)):
                        return int(obj)
                    return super().default(obj)
            
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, cls=NumpyEncoder)
            logger.info(f"\nTest results saved to: {results_file}")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")


def main():
    """Main test execution"""
    
    print("\n" + "="*70)
    print("DEEPFAKE DETECTION - COMPREHENSIVE MODEL TESTING")
    print("="*70)
    
    # Initialize tester
    tester = DeepfakeModelTester(models_dir="./models")
    
    # Test with dataset samples
    tester.test_dataset_samples(dataset_root="../dataset", num_samples=2)
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
    print("\nTo test with custom files, use:")
    print("  tester.test_video('path/to/video.mp4')")
    print("  tester.test_image('path/to/image.jpg')")
    print("  tester.test_audio('path/to/audio.wav')")


if __name__ == "__main__":
    main()
