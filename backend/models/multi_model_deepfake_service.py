"""
Multi-Model Deepfake Detection Service
Uses ensemble of multiple pretrained models for better accuracy
"""

import torch
import cv2
import time
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification
import logging

logger = logging.getLogger(__name__)

class MultiModelDeepfakeDetectionService:
    """
    Ensemble detection service using multiple pretrained models:
    1. SIGLIP (prithivMLmods/deepfake-detector-model-v1)
    2. Alternative models for comparison
    
    Combines predictions for more accurate results
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.processors = {}
        self.model_weights = {}  # Weight for each model's contribution
        self.model_version = "multi-model-ensemble-v1"
        
        # Define available models
        self.available_models = {
            "siglip": {
                "model_name": "prithivMLmods/deepfake-detector-model-v1",
                "weight": 1.0,  # 100% - Only reliable model for images
                "type": "image",
                "enabled": True
            },
            "deepfake_v2": {
                "model_name": "prithivMLmods/Deep-Fake-Detector-v2-Model",
                "weight": 0.0,  # Disabled - Too aggressive, poor calibration
                "type": "image",
                "enabled": False  # Disable this model
            },
            "video_classifier": {
                "model_name": "Naman712/Deep-fake-detection",
                "weight": 0.25,  # Video-specific model weight
                "type": "video",
                "enabled": True
            },
            "audio_classifier": {
                "model_name": "Wav2Vec2 + BiGRU+Attention",
                "weight": 0.15,  # Audio model weight
                "type": "audio",
                "model_path": None,  # Will be loaded from checkpoint if available
                "enabled": True
            }
            }
        
        
        self._load_models()
    
    def _load_models(self):
        """Load all enabled pretrained models"""
        logger.info("🔄 Loading multi-model ensemble...")
        
        for model_id, config in self.available_models.items():
            if not config.get("enabled", False):
                logger.info(f"⏭️  Skipping {model_id} (disabled)")
                continue
            
            try:
                logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                
                if model_id == "siglip":
                    self._load_siglip_model(model_id, config)
                elif model_id == "deepfake_v2":
                    self._load_deepfake_v2_model(model_id, config)
                elif model_id == "video_classifier":
                    self._load_video_classifier(model_id, config)
                elif model_id == "audio_classifier":
                    self._load_audio_classifier(model_id, config)
                
                self.model_weights[model_id] = config["weight"]
                logger.info(f"✅ {model_id} loaded successfully (weight: {config['weight']})")
            
            except Exception as e:
                logger.warning(f"⚠️  Failed to load {model_id}: {str(e)}")
                continue
        
        if not self.models:
            raise RuntimeError("❌ Could not load any detection models!")
        
        logger.info(f"✅ Ensemble ready with {len(self.models)} models")
        logger.info(f"Models: {list(self.models.keys())}")
    
    def _load_siglip_model(self, model_id, config):
        """Load SIGLIP model"""
        from transformers import AutoImageProcessor, SiglipForImageClassification
        
        model = SiglipForImageClassification.from_pretrained(config["model_name"])
        processor = AutoImageProcessor.from_pretrained(config["model_name"])
        
        model.to(self.device)
        model.eval()
        
        self.models[model_id] = model
        self.processors[model_id] = processor
    
    def _load_deepfake_v2_model(self, model_id, config):
        """Load DeepFake Detector v2 Model (ViT-based)"""
        from transformers import ViTForImageClassification, ViTImageProcessor
        
        model = ViTForImageClassification.from_pretrained(config["model_name"])
        processor = ViTImageProcessor.from_pretrained(config["model_name"])
        
        model.to(self.device)
        model.eval()
        
        self.models[model_id] = model
        self.processors[model_id] = processor
    
    def _load_vit_model(self, model_id, config):
        """Load ViT-based deepfake detection model"""
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        try:
            model = AutoModelForImageClassification.from_pretrained(config["model_name"])
            processor = AutoImageProcessor.from_pretrained(config["model_name"])
            
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = processor
        except Exception as e:
            # Fallback if specific model requires different loading
            logger.warning(f"Could not load {model_id} with standard loader: {str(e)}")
            raise
    
    def _load_video_classifier(self, model_id, config):
        """Load video classification pipeline for deepfake detection"""
        from transformers import pipeline
        
        try:
            # Create video classification pipeline
            classifier = pipeline("video-classification", model=config["model_name"], device=0 if torch.cuda.is_available() else -1)
            self.models[model_id] = classifier
            self.processors[model_id] = None  # Pipeline handles preprocessing
        except Exception as e:
            # Gracefully skip if model is gated or unavailable
            error_msg = str(e).lower()
            if "gated" in error_msg or "access" in error_msg or "401" in error_msg:
                logger.warning(f"⚠️  {model_id} is a gated model. Request access at https://huggingface.co/{config['model_name']}")
            else:
                logger.warning(f"Could not load {model_id}: {str(e)}")
            # Don't re-raise - let ensemble continue without this model
    
    def _load_audio_classifier(self, model_id, config):
        """Load audio deepfake detector (Wav2Vec2 + BiGRU+Attention)"""
        try:
            from models.audio_deepfake_detector import AudioDeepfakeDetector
            
            model_path = config.get("model_path")
            audio_detector = AudioDeepfakeDetector(model_path=model_path)
            self.models[model_id] = audio_detector
            self.processors[model_id] = None  # Detector handles preprocessing
        except Exception as e:
            logger.warning(f"Could not load {model_id}: {str(e)}")
            # Don't re-raise - let ensemble continue without this model
    
    def _predict_siglip(self, image, model, processor):
        """Get predictions from SIGLIP model"""
        try:
            inputs = processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
            
            if not isinstance(probs, list):
                probs = [probs]
            
            # SIGLIP: 0=fake, 1=real
            return {
                "fake": round(probs[0], 3),
                "real": round(probs[1], 3) if len(probs) > 1 else round(1 - probs[0], 3)
            }
        except Exception as e:
            logger.error(f"Error in SIGLIP prediction: {str(e)}")
            return None
    
    def _predict_deepfake_v2(self, image, model, processor):
        """Get predictions from DeepFake Detector v2 Model"""
        try:
            inputs = processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
            
            # Normalize to 0-1
            if len(probs.shape) == 0:
                probs = probs.unsqueeze(0)
            
            probs = probs.tolist()
            
            if not isinstance(probs, list):
                probs = [probs]
            
            # DeepFake v2: label mapping from model config
            # Typically: 0=real, 1=fake or similar
            # Get id2label from model config
            label_map = model.config.id2label if hasattr(model.config, 'id2label') else {0: 'real', 1: 'fake'}
            
            if len(probs) >= 2:
                # Determine which label is fake/real
                labels = list(label_map.values())
                if 'fake' in labels and 'authentic' in labels:
                    fake_idx = [i for i, l in label_map.items() if 'fake' in l.lower()][0] if any('fake' in l.lower() for l in labels) else 1
                    real_idx = [i for i, l in label_map.items() if 'authentic' in l.lower() or 'real' in l.lower()][0] if any('authentic' in l.lower() or 'real' in l.lower() for l in labels) else 0
                else:
                    fake_idx = 1
                    real_idx = 0
                
                return {
                    "fake": round(probs[fake_idx], 3) if fake_idx < len(probs) else round(probs[1], 3),
                    "real": round(probs[real_idx], 3) if real_idx < len(probs) else round(probs[0], 3)
                }
            else:
                fake_prob = round(probs[0], 3)
                return {
                    "fake": fake_prob,
                    "real": round(1 - fake_prob, 3)
                }
        except Exception as e:
            logger.error(f"Error in DeepFake v2 prediction: {str(e)}")
            return None
    
    def _predict_vit(self, image, model, processor):
        """Get predictions from ViT model"""
        try:
            inputs = processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
            
            # Normalize to 0-1
            if len(probs.shape) == 0:
                probs = probs.unsqueeze(0)
            
            probs = probs.tolist()
            
            if not isinstance(probs, list):
                probs = [probs]
            
            # ViT: label 0=real, 1=fake (may vary)
            if len(probs) >= 2:
                return {
                    "real": round(probs[0], 3),
                    "fake": round(probs[1], 3)
                }
            else:
                fake_prob = round(probs[0], 3)
                return {
                    "fake": fake_prob,
                    "real": round(1 - fake_prob, 3)
                }
        except Exception as e:
            logger.error(f"Error in ViT prediction: {str(e)}")
            return None
    
    def _predict_video_classifier(self, video_path, classifier):
        """Get predictions from video classification pipeline"""
        try:
            # Use the pipeline directly on video
            results = classifier(video_path)
            
            # Results format: [{"label": "fake"/"real", "score": ...}, ...]
            if isinstance(results, list) and len(results) > 0:
                predictions = {}
                for result in results:
                    label = result.get("label", "").lower()
                    score = result.get("score", 0.0)
                    if "fake" in label:
                        predictions["fake"] = round(score, 3)
                    elif "real" in label or "authentic" in label:
                        predictions["real"] = round(score, 3)
                
                # Ensure both fake and real exist
                if "fake" not in predictions or "real" not in predictions:
                    # Calculate missing one
                    if "fake" in predictions:
                        predictions["real"] = round(1 - predictions["fake"], 3)
                    elif "real" in predictions:
                        predictions["fake"] = round(1 - predictions["real"], 3)
                    else:
                        # Fallback if labels don't match expected format
                        if len(results) >= 2:
                            predictions["fake"] = round(results[0]["score"], 3)
                            predictions["real"] = round(results[1]["score"], 3)
                        else:
                            predictions["fake"] = round(results[0]["score"], 3)
                            predictions["real"] = round(1 - results[0]["score"], 3)
                
                return predictions
            else:
                return None
        except Exception as e:
            logger.error(f"Error in video classifier prediction: {str(e)}")
            return None
    
    def _predict_audio_classifier(self, audio_path, audio_detector):
        """Get predictions from audio deepfake detector"""
        try:
            logger.info(f"Analyzing audio: {audio_path}")
            prediction = audio_detector.predict(audio_path)
            
            # Accept predictions even with heuristic fallback
            if prediction:
                return {
                    "fake": prediction.get("fake", 0.5),
                    "real": prediction.get("real", 0.5)
                }
            else:
                logger.warning("Audio model returned no prediction")
                return None
        except Exception as e:
            logger.error(f"Error in audio classifier prediction: {str(e)}")
            return None
    
    def classify_image_ensemble(self, image):
        """
        Classify image using ensemble of image models
        Combines predictions from all loaded image models
        """
        try:
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(image).convert("RGB")
            
            all_predictions = {}
            model_results = {}
            
            # Get predictions from each model
            for model_id in self.models.keys():
                model = self.models[model_id]
                processor = self.processors[model_id]
                
                if model_id == "siglip":
                    prediction = self._predict_siglip(image, model, processor)
                elif model_id == "deepfake_v2":
                    prediction = self._predict_deepfake_v2(image, model, processor)
                else:
                    prediction = None
                
                if prediction:
                    all_predictions[model_id] = prediction
                    model_results[model_id] = prediction
                    logger.info(f"  {model_id}: Fake={prediction['fake']}, Real={prediction['real']}")
                else:
                    logger.warning(f"  {model_id}: Failed to get prediction")
            
            if not all_predictions:
                raise ValueError("Could not get predictions from any model")
            
            # Weighted ensemble average
            fake_scores = []
            real_scores = []
            weights = []
            
            for model_id, prediction in all_predictions.items():
                weight = self.model_weights.get(model_id, 1.0)
                fake_scores.append(prediction["fake"] * weight)
                real_scores.append(prediction["real"] * weight)
                weights.append(weight)
            
            total_weight = sum(weights)
            ensemble_fake = round(sum(fake_scores) / total_weight, 3)
            ensemble_real = round(sum(real_scores) / total_weight, 3)
            
            # Combine into single prediction
            combined = {
                "fake": ensemble_fake,
                "real": ensemble_real,
                "ensemble_average": True,
                "models_used": len(all_predictions),
                "model_predictions": model_results
            }
            
            logger.info(f"Ensemble result: Fake={ensemble_fake}, Real={ensemble_real}")
            return combined
        
        except Exception as e:
            logger.error(f"Error in ensemble classification: {str(e)}")
            raise
    
    def extract_frame_from_video(self, video_path, frame_num=10):
        """Extract frame from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise ValueError(f"Cannot extract frame {frame_num}")
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        except Exception as e:
            logger.error(f"Error extracting frame: {str(e)}")
            raise
    
    def classify_video_ensemble(self, video_path, num_frames=5):
        """Classify video using ensemble of all models (video-specific + frame-based image models)"""
        try:
            logger.info(f"Processing video with ensemble: {video_path}")
            
            all_predictions = {}
            model_results = {}
            
            # 1. Get predictions from dedicated video classifier if available
            if "video_classifier" in self.models:
                try:
                    logger.info("  🎥 Analyzing with dedicated video classifier...")
                    classifier = self.models["video_classifier"]
                    video_prediction = self._predict_video_classifier(video_path, classifier)
                    
                    if video_prediction:
                        all_predictions["video_classifier"] = video_prediction
                        model_results["video_classifier"] = video_prediction
                        logger.info(f"  video_classifier: Fake={video_prediction['fake']}, Real={video_prediction['real']}")
                    else:
                        logger.warning("  video_classifier: Failed to get prediction")
                except Exception as e:
                    logger.warning(f"  video_classifier error: {str(e)}")
            
            # 2. Get predictions from image models on frames
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if total_frames == 0:
                raise ValueError("Video has no frames")
            
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            frame_predictions = []
            
            logger.info(f"  📹 Extracting {num_frames} frames for image model analysis...")
            for frame_idx in frame_indices:
                try:
                    img = self.extract_frame_from_video(video_path, frame_idx)
                    frame_pred = self.classify_image_ensemble(img)
                    frame_predictions.append(frame_pred)
                except Exception as e:
                    logger.warning(f"Could not process frame {frame_idx}: {str(e)}")
                    continue
            
            if not frame_predictions:
                raise ValueError("Could not analyze any frames")
            
            # Aggregate predictions across frames for image models
            for model_id in self.available_models.keys():
                if self.available_models[model_id].get("type") == "video":
                    continue  # Skip video models, already handled above
                
                if model_id not in self.models:
                    continue  # Skip if model not loaded
                
                model_frame_preds = []
                for frame_pred in frame_predictions:
                    if "model_predictions" in frame_pred and model_id in frame_pred["model_predictions"]:
                        model_frame_preds.append(frame_pred["model_predictions"][model_id])
                
                if model_frame_preds:
                    # Average across frames
                    avg_fake = round(np.mean([p["fake"] for p in model_frame_preds]), 3)
                    avg_real = round(np.mean([p["real"] for p in model_frame_preds]), 3)
                    all_predictions[model_id] = {"fake": avg_fake, "real": avg_real}
                    model_results[model_id] = {"fake": avg_fake, "real": avg_real}
            
            if not all_predictions:
                raise ValueError("Could not analyze video with any model")
            
            # Weighted ensemble average
            fake_scores = []
            real_scores = []
            weights = []
            
            for model_id, prediction in all_predictions.items():
                weight = self.model_weights.get(model_id, 1.0)
                fake_scores.append(prediction["fake"] * weight)
                real_scores.append(prediction["real"] * weight)
                weights.append(weight)
            
            total_weight = sum(weights)
            ensemble_fake = round(sum(fake_scores) / total_weight, 3)
            ensemble_real = round(sum(real_scores) / total_weight, 3)
            
            ensemble_avg = {
                "fake": ensemble_fake,
                "real": ensemble_real,
                "frames_analyzed": len(frame_predictions),
                "ensemble_average": True,
                "models_used": len(all_predictions),
                "model_predictions": model_results
            }
            
            logger.info(f"Video ensemble result: Fake={ensemble_fake}, Real={ensemble_real}")
            return ensemble_avg
        
        except Exception as e:
            logger.error(f"Error classifying video: {str(e)}")
            raise
    
    def classify_audio_ensemble(self, audio_path):
        """Classify audio using audio detector if available"""
        try:
            logger.info(f"Processing audio with ensemble: {audio_path}")
            
            all_predictions = {}
            model_results = {}
            
            # Get predictions from audio model if available
            if "audio_classifier" in self.models:
                try:
                    logger.info("  🎵 Analyzing with audio classifier...")
                    audio_detector = self.models["audio_classifier"]
                    audio_prediction = self._predict_audio_classifier(audio_path, audio_detector)
                    
                    if audio_prediction:
                        all_predictions["audio_classifier"] = audio_prediction
                        model_results["audio_classifier"] = audio_prediction
                        logger.info(f"  audio_classifier: Fake={audio_prediction['fake']}, Real={audio_prediction['real']}")
                    else:
                        logger.warning("  audio_classifier: Failed to get prediction")
                except Exception as e:
                    logger.warning(f"  audio_classifier error: {str(e)}")
            
            if not all_predictions:
                raise ValueError("Could not analyze audio with any model")
            
            # Return audio predictions (single model for now, can expand later)
            ensemble_result = {
                "fake": all_predictions["audio_classifier"]["fake"],
                "real": all_predictions["audio_classifier"]["real"],
                "ensemble_average": True,
                "models_used": len(all_predictions),
                "model_predictions": model_results
            }
            
            logger.info(f"Audio ensemble result: Fake={ensemble_result['fake']}, Real={ensemble_result['real']}")
            return ensemble_result
        
        except Exception as e:
            logger.error(f"Error classifying audio: {str(e)}")
            raise
    
    def process_file(self, file_path, file_type):
        """Process file with multi-model ensemble"""
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Processing {file_type} with {len(self.models)} models")
            
            if file_type == "image":
                prediction = self.classify_image_ensemble(file_path)
            elif file_type == "video":
                prediction = self.classify_video_ensemble(file_path, num_frames=5)
            elif file_type == "audio":
                prediction = self.classify_audio_ensemble(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            processing_time = time.time() - start_time
            
            fake_score = prediction["fake"]
            real_score = prediction["real"]
            is_fake = fake_score > real_score
            
            result = {
                "is_fake": is_fake,
                "fake_confidence": fake_score,
                "real_confidence": real_score,
                "prediction": prediction,
                "processing_time": processing_time,
                "model_version": self.model_version,
                "models_used": len(self.models)
            }
            
            logger.info(f"✅ Analysis complete: {'FAKE' if is_fake else 'REAL'}")
            return result
        
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise

# Global instance
_service_instance = None

def get_multi_model_deepfake_service():
    """Get or create the multi-model detection service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = MultiModelDeepfakeDetectionService()
    return _service_instance
