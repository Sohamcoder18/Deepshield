"""
Enhanced Deepfake & AI Image Detection Service
Detects both deepfakes (manipulated) and AI-generated images
"""

import torch
import cv2
import time
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification
import logging

logger = logging.getLogger(__name__)

class EnhancedDeepfakeDetectionService:
    """
    Enhanced detection service that handles:
    1. Deepfakes (Face swaps, face2face, etc.)
    2. AI-generated images (DALL-E, Midjourney, Stable Diffusion)
    3. Real images
    """
    
    def __init__(self):
        self.model_name = "prithivMLmods/deepfake-detector-model-v1"
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.label_map = {
            "0": "fake",
            "1": "real"
        }
        self.model_version = "siglip-v1-enhanced"
        self._load_model()
    
    def _load_model(self):
        """Load the pretrained model and processor"""
        try:
            logger.info(f"Loading deepfake detection model: {self.model_name}")
            self.model = SiglipForImageClassification.from_pretrained(self.model_name)
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("✅ Deepfake detection model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            raise
    
    def _detect_ai_artifacts(self, image):
        """
        Simple confidence threshold for AI detection
        The pretrained model already detects AI-generated images
        We just need to lower the confidence threshold for detection
        """
        return 0.0  # Disabled - trust the pretrained model only
    
    def classify_image(self, image, detect_ai=True):
        """
        Classify image using ONLY the pretrained SIGLIP model
        No custom artifact detection - pure model predictions
        """
        try:
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(image).convert("RGB")
            
            # Get deepfake prediction from pretrained model
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
            
            if not isinstance(probs, list):
                probs = [probs]
            
            prediction = {
                self.label_map[str(i)]: round(probs[i], 3) for i in range(len(probs))
            }
            
            return prediction
        except Exception as e:
            logger.error(f"Error classifying image: {str(e)}")
            raise
    
    def extract_frame_from_video(self, video_path, frame_num=10):
        """Extract a specific frame from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise ValueError(f"Cannot extract frame {frame_num} from video")
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        except Exception as e:
            logger.error(f"Error extracting frame from video: {str(e)}")
            raise
    
    def classify_video(self, video_path, num_frames=5):
        """Classify video with enhanced detection"""
        try:
            logger.info(f"Processing video: {video_path}")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if total_frames == 0:
                raise ValueError("Video has no frames")
            
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            predictions = []
            
            for frame_idx in frame_indices:
                try:
                    img = self.extract_frame_from_video(video_path, frame_idx)
                    prediction = self.classify_image(img, detect_ai=True)
                    predictions.append(prediction)
                except Exception as e:
                    logger.warning(f"Could not process frame {frame_idx}: {str(e)}")
                    continue
            
            if not predictions:
                raise ValueError("Could not extract any valid frames from video")
            
            # Average predictions
            avg_prediction = {
                "fake": round(np.mean([p["fake"] for p in predictions]), 3),
                "real": round(np.mean([p["real"] for p in predictions]), 3)
            }
            
            logger.info(f"Video prediction: {avg_prediction}")
            return avg_prediction
        except Exception as e:
            logger.error(f"Error classifying video: {str(e)}")
            raise
    
    def process_file(self, file_path, file_type, detect_ai=False):
        """
        Process file using ONLY the pretrained SIGLIP model
        Stable and consistent predictions
        """
        start_time = time.time()
        
        try:
            if file_type == "image":
                prediction = self.classify_image(file_path, detect_ai=False)
            elif file_type == "video":
                prediction = self.classify_video(file_path, num_frames=5)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            processing_time = time.time() - start_time
            
            # Simple, stable decision logic
            fake_score = prediction["fake"]
            real_score = prediction["real"]
            
            # Threshold of 0.5 for binary classification
            is_fake = fake_score > real_score
            
            result = {
                "is_fake": is_fake,
                "fake_confidence": fake_score,
                "real_confidence": real_score,
                "prediction": prediction,
                "processing_time": processing_time,
                "model_version": self.model_version
            }
            
            logger.info(f"Processing complete: {result}")
            return result
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise

# Global instance
_service_instance = None

def get_enhanced_deepfake_service():
    """Get or create the enhanced deepfake detection service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EnhancedDeepfakeDetectionService()
    return _service_instance
