import torch
import cv2
import time
from PIL import Image
import numpy as np
from transformers import AutoImageProcessor, SiglipForImageClassification
import logging

logger = logging.getLogger(__name__)

class DeepfakeDetectionService:
    """Service for deepfake detection using pretrained SIGLIP model"""
    
    def __init__(self):
        self.model_name = "prithivMLmods/deepfake-detector-model-v1"
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.label_map = {
            "0": "fake",
            "1": "real"
        }
        self.model_version = "siglip-v1-pretrained"
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
    
    def classify_image(self, image):
        """Classify a single image"""
        try:
            if isinstance(image, str):
                # Load from file path
                image = Image.open(image).convert("RGB")
            elif isinstance(image, np.ndarray):
                # Convert numpy array to PIL Image
                image = Image.fromarray(image).convert("RGB")
            
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
            
            # Ensure probs is always a list (handle single output)
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
        """Extract a specific frame from a video file"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise ValueError(f"Cannot extract frame {frame_num} from video")
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        except Exception as e:
            logger.error(f"Error extracting frame from video: {str(e)}")
            raise
    
    def classify_video(self, video_path, num_frames=5):
        """Classify a video by extracting and analyzing multiple frames"""
        try:
            logger.info(f"Processing video: {video_path}")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if total_frames == 0:
                raise ValueError("Video has no frames")
            
            # Extract frames at intervals
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            predictions = []
            
            for frame_idx in frame_indices:
                try:
                    img = self.extract_frame_from_video(video_path, frame_idx)
                    prediction = self.classify_image(img)
                    predictions.append(prediction)
                except Exception as e:
                    logger.warning(f"Could not process frame {frame_idx}: {str(e)}")
                    continue
            
            if not predictions:
                raise ValueError("Could not extract any valid frames from video")
            
            # Average the predictions
            avg_prediction = {
                "fake": round(np.mean([p["fake"] for p in predictions]), 3),
                "real": round(np.mean([p["real"] for p in predictions]), 3)
            }
            
            logger.info(f"Video prediction: {avg_prediction}")
            return avg_prediction
        except Exception as e:
            logger.error(f"Error classifying video: {str(e)}")
            raise
    
    def process_file(self, file_path, file_type):
        """Process a file and return detection results"""
        start_time = time.time()
        
        try:
            if file_type == "image":
                prediction = self.classify_image(file_path)
            elif file_type == "video":
                prediction = self.classify_video(file_path, num_frames=5)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            processing_time = time.time() - start_time
            
            # Determine if fake based on confidence
            is_fake = prediction["fake"] > prediction["real"]
            
            result = {
                "is_fake": is_fake,
                "fake_confidence": prediction["fake"],
                "real_confidence": prediction["real"],
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

def get_deepfake_service():
    """Get or create the deepfake detection service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DeepfakeDetectionService()
    return _service_instance
