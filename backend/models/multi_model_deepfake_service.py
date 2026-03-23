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
            "efficientnet": {
                "model_path": "model.pt",
                "weight": 0.5,  # 50% - primary deepfake detection
                "type": "image",
                "enabled": True,
                "architecture": "efficientnet"
            },
            "siglip": {
                "model_name": "prithivMLmods/deepfake-detector-model-v1",
                "weight": 0.0,  # Disabled
                "type": "image",
                "enabled": False
            },
            "ai_detector": {
                "model_name": "umm-maybe/AI-image-detector",
                "weight": 0.0,  # DISABLED - detects AI-generated images, not deepfakes specifically
                "type": "image",
                "enabled": False
            },
            "deepfake_v2": {
                "model_name": "prithivMLmods/Deep-Fake-Detector-v2-Model",
                "weight": 0.2,  # 20% - artifact/deepfake detection
                "type": "image",
                "enabled": True
            },
            "ai_vs_real": {
                "model_name": "prithivMLmods/AI-vs-Deepfake-vs-Real-9999",
                "weight": 0.3,  # 30% - 3-class detector: AI/Deepfake/Real (99.89% accuracy)
                "type": "image",
                "enabled": True
            },
            "genconvit": {
                "model_name": "Deressa/GenConViT",
                "weight": 1.0,  # Used exclusively for video-level analysis
                "type": "video",
                "enabled": True
            },
            "audio_classifier": {
                "model_name": "mo-thecreator/Deepfake-audio-detection",
                "weight": 1.0,  # Wav2Vec2 fine-tuned: 98.8% accuracy
                "type": "audio",
                "model_path": None,
                "enabled": True  # HuggingFace Wav2Vec2 pretrained audio deepfake detector
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
                if model_id == "efficientnet":
                    logger.info(f"📥 Loading {model_id}: {config['model_path']}")
                    self._load_efficientnet_model(model_id, config)
                elif model_id == "siglip":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_siglip_model(model_id, config)
                elif model_id == "deepfake_v2":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_deepfake_v2_model(model_id, config)
                elif model_id == "ai_detector":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_vit_model(model_id, config)
                elif model_id == "ai_vs_real":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_ai_vs_real_model(model_id, config)
                elif model_id == "genconvit":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_genconvit_model(model_id, config)
                elif model_id == "audio_classifier":
                    logger.info(f"📥 Loading {model_id}: {config['model_name']}")
                    self._load_wav2vec2_audio_model(model_id, config)
                
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
        """Load SIGLIP model with fallback for missing processor config"""
        from transformers import AutoImageProcessor, AutoProcessor, SiglipForImageClassification
        import os
        
        try:
            # Try loading model first
            logger.info(f"Loading SIGLIP model: {config['model_name']}")
            hf_token = os.getenv('HF_TOKEN', None)
            
            model = SiglipForImageClassification.from_pretrained(
                config["model_name"],
                token=hf_token,
                trust_remote_code=False
            )
            
            # Try AutoImageProcessor first
            try:
                processor = AutoImageProcessor.from_pretrained(
                    config["model_name"],
                    token=hf_token,
                    trust_remote_code=False
                )
            except Exception as e:
                error_str = str(e).lower()
                if "404" in error_str or "processor_config" in error_str:
                    logger.warning(f"Processor config not found (404), trying AutoProcessor fallback...")
                    try:
                        # Fallback to AutoProcessor
                        processor = AutoProcessor.from_pretrained(
                            config["model_name"],
                            token=hf_token,
                            trust_remote_code=False
                        )
                    except:
                        # Last resort: create minimal processor
                        logger.warning(f"Using minimal image processor fallback")
                        from PIL import Image
                        from torchvision import transforms
                        
                        # Create a minimal processor that handles image resizing
                        class MinimalImageProcessor:
                            def __init__(self):
                                self.transform = transforms.Compose([
                                    transforms.Resize((384, 384)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(
                                        mean=[0.5, 0.5, 0.5],
                                        std=[0.5, 0.5, 0.5]
                                    )
                                ])
                            
                            def __call__(self, images=None, return_tensors=None, **kwargs):
                                if isinstance(images, list):
                                    images = [self.transform(img) if isinstance(img, Image.Image) else img for img in images]
                                    images = torch.stack(images)
                                else:
                                    images = self.transform(images) if isinstance(images, Image.Image) else images
                                    if images.dim() == 3:
                                        images = images.unsqueeze(0)
                                
                                class ProcessorOutput:
                                    def __init__(self, pixel_values):
                                        self.pixel_values = pixel_values
                                    
                                    def to(self, device):
                                        self.pixel_values = self.pixel_values.to(device)
                                        return self
                                
                                return ProcessorOutput(images)
                        
                        processor = MinimalImageProcessor()
                else:
                    raise
            
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = processor
            logger.info(f"✅ Successfully loaded SIGLIP model with processor")
            
        except Exception as e:
            logger.error(f"Failed to load SIGLIP model: {str(e)}")
            logger.warning(f"To authenticate with HuggingFace, set HF_TOKEN environment variable")
            raise
    
    def _load_ai_vs_real_model(self, model_id, config):
        """Load prithivMLmods/AI-vs-Real-Image-Detector (SigLIP-based AI vs Real classifier)"""
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        try:
            model_name = config["model_name"]
            logger.info(f"Loading AI-vs-Real detector from HuggingFace: {model_name}")
            
            processor = AutoImageProcessor.from_pretrained(model_name)
            model = AutoModelForImageClassification.from_pretrained(model_name)
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = processor
            
            # Log label mapping so we know the index order at startup
            label_map = model.config.id2label if hasattr(model.config, 'id2label') else {}
            logger.info(f"✅ AI-vs-Real detector loaded. Label map: {label_map}")
        except Exception as e:
            logger.error(f"Error loading AI-vs-Real model: {str(e)}")
            raise

    def _predict_ai_vs_real(self, image, model, processor):
        """Get predictions from AI-vs-Deepfake-vs-Real-9999 (3-class SigLIP model).

        Returns a dict with keys:
          ai       - probability the image is AI-generated
          deepfake - probability the image is a deepfake
          real     - probability the image is authentic
          fake     - ai + deepfake (combined non-real probability)
        """
        try:
            inputs = processor(images=image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze()

            if len(probs.shape) == 0:
                probs = probs.unsqueeze(0)
            probs = probs.tolist()
            if not isinstance(probs, list):
                probs = [probs]

            label_map = model.config.id2label if hasattr(model.config, 'id2label') else {}

            # Always log raw values for debugging
            raw_debug = {label_map.get(i, str(i)): round(float(probs[i]), 4) for i in range(len(probs))}
            logger.info(f"🖼️  AI-vs-Real RAW label_map={label_map}")
            logger.info(f"🖼️  AI-vs-Real RAW probs_per_class={raw_debug}")

            # Find indices for each class
            AI_KW       = ('artificial', 'ai', 'generated', 'synthetic')
            DEEP_KW     = ('deepfake', 'deep_fake', 'deep-fake', 'manipulated')
            REAL_KW     = ('real', 'authentic', 'genuine', 'natural', 'human')

            ai_idx   = next((i for i, l in label_map.items() if any(k in str(l).lower() for k in AI_KW)), None)
            deep_idx = next((i for i, l in label_map.items() if any(k in str(l).lower() for k in DEEP_KW)), None)
            real_idx = next((i for i, l in label_map.items() if any(k in str(l).lower() for k in REAL_KW)), None)

            # prithivMLmods convention fallback: 0=Artificial, 1=Deepfake, 2=Real
            if ai_idx is None:
                ai_idx = 0
                logger.warning(f"🖼️  AI-vs-Real: no AI keyword match, defaulting ai_idx=0")
            if deep_idx is None:
                deep_idx = 1 if len(probs) >= 3 else None
                logger.warning(f"🖼️  AI-vs-Real: no Deepfake keyword match, defaulting deep_idx={deep_idx}")
            if real_idx is None:
                real_idx = 2 if len(probs) >= 3 else (1 if len(probs) == 2 else 0)
                logger.warning(f"🖼️  AI-vs-Real: no Real keyword match, defaulting real_idx={real_idx}")

            ai_prob   = round(float(probs[ai_idx])   if ai_idx   < len(probs) else 0.0, 3)
            deep_prob = round(float(probs[deep_idx]) if deep_idx is not None and deep_idx < len(probs) else 0.0, 3)
            real_prob = round(float(probs[real_idx]) if real_idx < len(probs) else 0.0, 3)
            fake_prob = round(min(ai_prob + deep_prob, 1.0), 3)

            result = {
                "ai":       ai_prob,
                "deepfake": deep_prob,
                "real":     real_prob,
                "fake":     fake_prob,   # combined for backward-compat weighted ensemble
            }
            logger.info(f"🖼️  AI-vs-Real FINAL: ai={ai_prob}, deepfake={deep_prob}, real={real_prob}")
            return result
        except Exception as e:
            logger.error(f"Error in AI-vs-Real prediction: {str(e)}")
            return None

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
        """Load generic ViT-based image classification model"""
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        try:
            model = AutoModelForImageClassification.from_pretrained(config["model_name"])
            processor = AutoImageProcessor.from_pretrained(config["model_name"])
            
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = processor
            logger.info(f"✅ ViT model {model_id} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading ViT model {model_id}: {str(e)}")
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
    
    def _load_efficientnet_model(self, model_id, config):
        """Load EfficientNet PyTorch model from checkpoint (supports TorchScript)"""
        try:
            import os
            from torchvision import models
            
            model_path = config.get("model_path")
            
            # Convert relative path to absolute if needed
            if not os.path.isabs(model_path):
                model_path = os.path.join(os.getcwd(), model_path)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model checkpoint not found: {model_path}")
            
            logger.info(f"Loading EfficientNet from: {model_path}")
            
            # Try loading as TorchScript first
            try:
                logger.info("Attempting to load as TorchScript model...")
                model = torch.jit.load(model_path, map_location=self.device)
                model.eval()
                self.models[model_id] = model
                self.processors[model_id] = None
                logger.info(f"✅ EfficientNet TorchScript model loaded successfully")
                return
            except Exception as ts_error:
                logger.warning(f"TorchScript load failed: {str(ts_error)}, trying standard checkpoint...")
            
            # Fallback: Try loading as standard PyTorch checkpoint
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            # Create EfficientNet model
            model = models.efficientnet_b0(pretrained=False)
            
            # Adjust classifier if needed (assuming 2 classes: real, fake)
            if isinstance(checkpoint, dict):
                num_classes = checkpoint.get('num_classes', 2)
                if num_classes != 2:
                    in_features = model.classifier[-1].in_features
                    model.classifier[-1] = torch.nn.Linear(in_features, num_classes)
                
                # Load weights
                if 'model_state' in checkpoint:
                    model.load_state_dict(checkpoint['model_state'])
                elif 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                else:
                    # Try loading directly
                    try:
                        model.load_state_dict(checkpoint)
                    except:
                        model.load_state_dict(checkpoint, strict=False)
            else:
                # Might be a direct model object
                model = checkpoint
            
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = None
            
            logger.info(f"✅ EfficientNet model loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading EfficientNet model: {str(e)}")
            raise
    
    def _load_genconvit_model(self, model_id, config):
        """Load GenConViT model for video deepfake detection (custom loader)"""
        try:
            import os
            import re
            import urllib.request
            from models.genconvit.genconvit_ed import GenConViTED
            from torchvision import transforms

            logger.info(f"Instantiating custom GenConViT architecture...")
            
            gen_config = {
                'model': {
                   'backbone': 'convnext_tiny',
                   'embedder': 'swin_tiny_patch4_window7_224',
                   'latent_dims': 12544
                },
                'img_size': 224
            }
            
            # Instantiate model structure
            model = GenConViTED(gen_config, pretrained=False)
            
            # Download weights if missing
            model_path = os.path.join(os.path.dirname(__file__), "genconvit_ed_inference.pth")
            if not os.path.exists(model_path):
                logger.info("Downloading GenConViT weights from HuggingFace (238MB)...")
                url = "https://huggingface.co/Deressa/GenConViT/resolve/main/genconvit_ed_inference.pth"
                urllib.request.urlretrieve(url, model_path)
                
            logger.info("Loading GenConViT state dictionary...")
            checkpoint = torch.load(model_path, map_location=self.device)
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint

            # ── Key remapping ──────────────────────────────────────────────
            # The checkpoint was built with an older timm Swin layout where the
            # downsample module lives inside layers[i] (0-indexed), but the
            # current timm places it at layers[i+1].  We increment every layer
            # index by 1 for "*.layers.<i>.downsample.*" keys so that weights
            # land in the correct submodule (applies to both the standalone
            # `embedder` and the nested `backbone.patch_embed.backbone` paths).
            def _remap_swin_downsample_key(key: str) -> str:
                m = re.match(r'^(.*\.layers\.)(\d+)(\.downsample\..+)$', key)
                if m:
                    return f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}"
                return key

            remapped_state_dict = {}
            remapped_keys = 0
            for k, v in state_dict.items():
                new_k = _remap_swin_downsample_key(k)
                if new_k != k:
                    remapped_keys += 1
                remapped_state_dict[new_k] = v

            if remapped_keys:
                logger.info(
                    f"Remapped {remapped_keys} Swin downsample keys "
                    f"(+1 layer index) to match current timm layout"
                )

            model.load_state_dict(remapped_state_dict, strict=False)
                
            model.to(self.device)
            model.eval()
            
            # Manual image processor
            processor = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            self.models[model_id] = model
            self.processors[model_id] = processor
            logger.info(f"✅ GenConViT custom PyTorch loader initialized successfully")
            
        except Exception as e:
            logger.error(f"Error loading GenConViT manual model: {str(e)}")
            raise

    def _predict_genconvit(self, image, model, processor):
        """Get predictions from GenConViT model using manual transforms"""
        try:
            # Apply torchvision transforms -> [C, H, W]
            input_tensor = processor(image)
            # Add batch dimension -> [1, C, H, W]
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = model(input_batch)
                
                # Apply softmax
                probs = torch.nn.functional.softmax(outputs, dim=-1).squeeze().tolist()
                
                # GenConViT label mapping (verified from pred_func.py):
                # index 0 is FAKE, index 1 is REAL
                if isinstance(probs, list) and len(probs) >= 2:
                    return {
                        "fake": round(float(probs[0]), 3),
                        "real": round(float(probs[1]), 3)
                    }
                else:
                    # Fallback for single-value logit
                    p = float(probs) if not isinstance(probs, list) else float(probs[0])
                    # If it's a sigmoid-like 0-1 result where 0=Fake, 1=Real
                    return {"fake": round(1.0 - p, 3), "real": round(p, 3)}
                    
        except Exception as e:
            logger.error(f"GenConViT prediction error: {str(e)}")
            return None

    def _load_wav2vec2_audio_model(self, model_id, config):
        """Load Wav2Vec2 pretrained audio deepfake detection model (98.8% accuracy)"""
        try:
            from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
            
            model_name = config["model_name"]
            logger.info(f"Loading Wav2Vec2 audio model: {model_name}")
            
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            model = AutoModelForAudioClassification.from_pretrained(model_name)
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = feature_extractor
            logger.info(f"✅ Wav2Vec2 audio deepfake detector loaded")
        except Exception as e:
            logger.error(f"Error loading Wav2Vec2 audio model: {str(e)}")
            raise

    def _predict_wav2vec2(self, audio_path, model, feature_extractor):
        """Get predictions from Wav2Vec2 audio deepfake detection model"""
        try:
            import librosa
            
            # Load audio at 16kHz (required by Wav2Vec2)
            audio, sample_rate = librosa.load(audio_path, sr=16000)
            
            inputs = feature_extractor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
            
            if len(probs.shape) == 0:
                probs = probs.unsqueeze(0)
            probs = probs.tolist()
            if not isinstance(probs, list):
                probs = [probs]
            
            # Determine label mapping from model config
            label_map = model.config.id2label if hasattr(model.config, 'id2label') else {0: 'fake', 1: 'real'}
            
            fake_idx = next((i for i, l in label_map.items() if 'fake' in str(l).lower() or 'spoof' in str(l).lower()), 0)
            real_idx = next((i for i, l in label_map.items() if 'real' in str(l).lower() or 'genuine' in str(l).lower() or 'bonafide' in str(l).lower()), 1)
            
            if len(probs) >= 2:
                result = {
                    "fake": round(float(probs[fake_idx]), 3) if fake_idx < len(probs) else round(float(probs[0]), 3),
                    "real": round(float(probs[real_idx]), 3) if real_idx < len(probs) else round(float(probs[1]), 3),
                }
            else:
                fake_prob = round(float(probs[0]), 3)
                result = {"fake": fake_prob, "real": round(1.0 - fake_prob, 3)}
            
            logger.info(f"🎵 Wav2Vec2 audio prediction: fake={result['fake']}, real={result['real']}")
            return result
        except Exception as e:
            logger.error(f"Error in Wav2Vec2 audio prediction: {str(e)}")
            return None


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
            # IMPORTANT: This model has INVERTED outputs - Index 0=fake, Index 1=real in checkpoint
            # Get id2label from model config
            label_map = model.config.id2label if hasattr(model.config, 'id2label') else {0: 'fake', 1: 'real'}
            
            if len(probs) >= 2:
                # Determine which label is fake/real
                labels = list(label_map.values())
                if 'fake' in labels and 'authentic' in labels:
                    fake_idx = [i for i, l in label_map.items() if 'fake' in l.lower()][0] if any('fake' in l.lower() for l in labels) else 0
                    real_idx = [i for i, l in label_map.items() if 'authentic' in l.lower() or 'real' in l.lower()][0] if any('authentic' in l.lower() or 'real' in l.lower() for l in labels) else 1
                else:
                    # CORRECTED: Swap indices from wrong defaults (1,0) to correct (0,1)
                    fake_idx = 0
                    real_idx = 1
                
                return {
                    "fake": round(probs[fake_idx], 3) if fake_idx < len(probs) else round(probs[0], 3),
                    "real": round(probs[real_idx], 3) if real_idx < len(probs) else round(probs[1], 3)
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
    
    def _predict_efficientnet(self, image, model):
        """Get predictions from EfficientNet PyTorch model (supports TorchScript)"""
        try:
            from torchvision import transforms
            
            # Prepare image
            if isinstance(image, Image.Image):
                img_tensor = image
            else:
                img_tensor = Image.fromarray(image) if isinstance(image, np.ndarray) else image
            
            # Standard EfficientNet preprocessing
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            img_tensor = transform(img_tensor).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = model(img_tensor)
                
                # Handle both regular models and TorchScript
                if isinstance(outputs, torch.Tensor):
                    logits = outputs
                else:
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs[0]
                
                # If output has 1 node, use sigmoid, else use softmax
                if len(logits.shape) > 1 and logits.shape[1] == 1:
                    probs = torch.sigmoid(logits).squeeze()
                    probs = [probs.item()]  # convert to list for consistency
                else:
                    probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
                    if len(probs.shape) == 0:
                        probs = probs.unsqueeze(0)
                    probs = probs.cpu().numpy().tolist()
            
            if not isinstance(probs, list):
                probs = [probs]
            
            # For 2-class, handling inverted labels (Index 1=fake, Index 0=real)
            if len(probs) >= 2:
                result = {
                    "fake": round(float(probs[1]), 3),
                    "real": round(float(probs[0]), 3)
                }
                logger.info(f"🚀 EfficientNet prediction: fake={result['fake']}, real={result['real']}")
                return result
            else:
                # Single node output = real class probability (inverted labels)
                real_prob = round(float(probs[0]), 3)
                return {
                    "fake": round(1.0 - real_prob, 3),
                    "real": real_prob
                }
        except Exception as e:
            logger.error(f"Error in EfficientNet prediction: {str(e)}")
            return None
    
    def _predict_vit(self, image, model, processor):
        """Get predictions from ViT model (ai_detector) - INVERTED"""
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
            
            # ViT (ai_detector) model INVERTED mapping based on empirical testing
            # The model shows high "real" probability for both real AND AI images
            # Testing shows: Real=0.992 (wrong bias), AI=0.903 (wrong bias)
            # Solution: INVERT the predictions - swap fake/real values
            if len(probs) >= 2:
                result = {
                    "fake": round(probs[1], 3),      # Index 1 = shows as real, but invert to fake
                    "real": round(probs[0], 3)       # Index 0 = shows as artificial, but invert to real
                }
                logger.info(f"🤖 ViT prediction (INVERTED): fake={result['fake']}, real={result['real']}")
                return result
            else:
                fake_prob = round(probs[0], 3)
                return {
                    "fake": round(1 - fake_prob, 3),
                    "real": fake_prob
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
        Classify image using ensemble of image models.

        Decision priority (AI prediction overrides EfficientNet):
          1. if ai_prob >= 0.45  → verdict: "AI Generated"
          2. elif deepfake_score >= 0.50 → verdict: "Deepfake"
          3. else                → verdict: "Authentic"

        Returns structured dict with verdict, trust_score, ai_prob,
        deepfake_score, real_score, and per-model predictions.
        """
        try:
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(image).convert("RGB")

            all_predictions        = {}
            model_results          = {}
            ai_prob_raw            = None  # raw AI class probability from ai_vs_real model
            ai_vs_real_combined_raw = None  # combined ai+deepfake prob from ai_vs_real model
            ai_vs_real_real_raw    = None  # 'Real one' class probability from ai_vs_real model

            # ── Collect per-model predictions ─────────────────────────────
            for model_id in self.models.keys():
                model     = self.models[model_id]
                processor = self.processors[model_id]

                model_type = self.available_models.get(model_id, {}).get("type", "image")
                if model_type != "image":
                    continue

                if model_id == "efficientnet":
                    prediction = self._predict_efficientnet(image, model)
                elif model_id == "siglip":
                    prediction = self._predict_siglip(image, model, processor)
                elif model_id == "deepfake_v2":
                    prediction = self._predict_deepfake_v2(image, model, processor)
                elif model_id == "ai_detector":
                    prediction = self._predict_vit(image, model, processor)
                elif model_id == "ai_vs_real":
                    prediction = self._predict_ai_vs_real(image, model, processor)
                    if prediction:
                        # Raw AI probability (class 0 = Artificial)
                        ai_prob_raw             = prediction.get("ai",   prediction.get("fake", 0.0))
                        # Combined non-real (ai + deepfake, captured in 'fake' key)
                        ai_vs_real_combined_raw = prediction.get("fake",  0.0)
                        # Real probability from 3-class model
                        ai_vs_real_real_raw     = prediction.get("real",  1.0)
                else:
                    prediction = None

                if prediction:
                    all_predictions[model_id] = prediction
                    model_results[model_id]   = prediction
                    logger.info(f"  {model_id}: Fake={prediction['fake']}, Real={prediction['real']}")
                else:
                    logger.warning(f"  {model_id}: Failed to get prediction")

            if not all_predictions:
                raise ValueError("Could not get predictions from any model")

            # ── Weighted ensemble (binary fake / real) ────────────────────
            fake_scores, real_scores, weights = [], [], []
            for model_id, pred in all_predictions.items():
                w = self.model_weights.get(model_id, 1.0)
                fake_scores.append(pred["fake"] * w)
                real_scores.append(pred["real"] * w)
                weights.append(w)

            total_weight   = sum(weights)
            ensemble_fake  = round(sum(fake_scores) / total_weight, 3)
            ensemble_real  = round(sum(real_scores) / total_weight, 3)

            # ── 3-category decision logic ─────────────────────────────────
            ai_prob            = float(ai_prob_raw)            if ai_prob_raw            is not None else 0.0
            ai_combined        = float(ai_vs_real_combined_raw) if ai_vs_real_combined_raw is not None else 0.0
            ai_real_conf       = float(ai_vs_real_real_raw)    if ai_vs_real_real_raw    is not None else 1.0
            deepfake_score     = round(ensemble_fake, 3)
            real_score         = round(ensemble_real, 3)

            # ── AI GENERATED triggers ────────────────────
            # 1. Model explicitly classifies it as AI (Artificial prob >= 0.40)
            is_ai = (
                ai_prob >= 0.40
            )

            if is_ai:
                verdict     = "AI Generated"
                is_fake     = True
                ref_score   = ai_prob
                trust_score = round((1.0 - ref_score) * 100, 1)
            elif deepfake_score >= 0.50:
                verdict     = "Deepfake"
                is_fake     = True
                trust_score = round((1.0 - deepfake_score) * 100, 1)
            else:
                verdict     = "Authentic"
                is_fake     = False
                trust_score = round(real_score * 100, 1)

            logger.info(
                f"Ensemble: ai={ai_prob:.3f}, ai_combined={ai_combined:.3f}, "
                f"ai_real_conf={ai_real_conf:.3f}, deepfake_score={deepfake_score}, real={real_score}"
            )
            logger.info(f"Verdict: {verdict} | trust_score={trust_score}% | is_fake={is_fake}")

            return {
                "verdict":        verdict,
                "is_fake":        is_fake,
                "trust_score":    trust_score,
                "ai_prob":        ai_prob,
                "deepfake_score": deepfake_score,
                "real_score":     real_score,
                # Backward-compat keys (used by app.py)
                "fake":           ensemble_fake,
                "real":           ensemble_real,
                "ensemble_average": True,
                "models_used":    len(all_predictions),
                "model_predictions": model_results,
            }

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
        """Classify video applying frame-level ensemble + 3-category decision logic."""
        try:
            logger.info(f"Processing video with ensemble: {video_path}")

            all_predictions = {}
            model_results   = {}

            # Compute frame indices
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            if total_frames == 0:
                raise ValueError("Video has no frames")
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

            # GenConViT (disabled by default — kept for future use)
            if "genconvit" in self.models:
                try:
                    genconvit_model     = self.models["genconvit"]
                    genconvit_processor = self.processors["genconvit"]
                    gc_preds = []
                    for frame_idx in frame_indices:
                        try:
                            img = self.extract_frame_from_video(video_path, int(frame_idx))
                            gp  = self._predict_genconvit(img, genconvit_model, genconvit_processor)
                            if gp:
                                gc_preds.append(gp)
                        except Exception as e:
                            logger.warning(f"  GenConViT frame {frame_idx} error: {str(e)}")
                        finally:
                            # Release memory after each GenConViT frame
                            import gc
                            gc.collect()
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()
                    if gc_preds:
                        avg_fake = round(float(np.mean([p["fake"] for p in gc_preds])), 3)
                        avg_real = round(float(np.mean([p["real"] for p in gc_preds])), 3)
                        all_predictions["genconvit"] = {"fake": avg_fake, "real": avg_real}
                        model_results["genconvit"]   = {"fake": avg_fake, "real": avg_real}
                except Exception as e:
                    logger.warning(f"  genconvit error: {str(e)}")

            # ── Frame-level image ensemble ────────────────────────────────
            frame_predictions  = []
            frame_ai_probs     = []   # per-frame raw AI class probability
            frame_ai_combined  = []   # per-frame combined (ai+deepfake) from 3-class model
            frame_ai_real      = []   # per-frame real confidence from 3-class model

            logger.info(f"  📹 Extracting {num_frames} frames for image model analysis...")
            for frame_idx in frame_indices:
                try:
                    img        = self.extract_frame_from_video(video_path, int(frame_idx))
                    frame_pred = self.classify_image_ensemble(img)
                    frame_predictions.append(frame_pred)
                    # Collect per-frame AI probabilities for video-level override
                    if "ai_prob" in frame_pred:
                        frame_ai_probs.append(frame_pred["ai_prob"])
                    if "deepfake_score" in frame_pred:
                        # deepfake_score from image ensemble = weighted fake (proxy for ai_combined)
                        pass  # use ai_prob only for now; ai_combined uses frame_pred model_predictions
                    # Get raw ai_vs_real combined from model_predictions if available
                    mp = frame_pred.get("model_predictions")
                    if isinstance(mp, dict):
                        avr = mp.get("ai_vs_real")
                        if isinstance(avr, dict):
                            if "fake" in avr:
                                frame_ai_combined.append(float(avr["fake"]))
                            if "real" in avr:
                                frame_ai_real.append(float(avr["real"]))

                except Exception as e:
                    logger.warning(f"Could not process frame {frame_idx}: {str(e)}")
                    continue
                finally:
                    # Aggressively release memory after each frame to prevent OOM
                    import gc
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            if not frame_predictions and not all_predictions:
                raise ValueError("Could not analyze any frames")

            # Aggregate per-model across frames
            for model_id in self.available_models.keys():
                if self.available_models[model_id].get("type") != "image":
                    continue
                if model_id not in self.models:
                    continue
                preds = [
                    fp["model_predictions"][model_id]
                    for fp in frame_predictions
                    if "model_predictions" in fp and model_id in fp["model_predictions"]
                ]
                if preds:
                    avg_fake = round(float(np.mean([p["fake"] for p in preds])), 3)
                    avg_real = round(float(np.mean([p["real"] for p in preds])), 3)
                    all_predictions[model_id] = {"fake": avg_fake, "real": avg_real}
                    model_results[model_id]   = {"fake": avg_fake, "real": avg_real}

            if not all_predictions:
                raise ValueError("Could not analyze video with any model")

            # ── Weighted ensemble with Video-Specific weights ─────────────
            fake_scores, real_scores, weights = [], [], []
            
            # Use stronger GenConViT weight / lower EfficientNet weight for video
            video_weights = {
                "genconvit": 2.0,
                "efficientnet": 0.3,
                "deepfake_v2": 0.1,
                "ai_vs_real": 0.3
            }
            
            for model_id, pred in all_predictions.items():
                w = video_weights.get(model_id, self.model_weights.get(model_id, 1.0))
                fake_scores.append(pred["fake"] * w)
                real_scores.append(pred["real"] * w)
                weights.append(w)

            total_weight   = sum(weights)
            ensemble_fake  = round(sum(fake_scores) / total_weight, 3)
            ensemble_real  = round(sum(real_scores) / total_weight, 3)

            # ── 3-category decision (same logic as image) ─────────────────
            ai_prob        = round(float(np.mean(frame_ai_probs)),       3) if frame_ai_probs       else 0.0
            ai_combined    = round(float(np.mean(frame_ai_combined)),    3) if frame_ai_combined    else 0.0
            ai_real_conf   = round(float(np.mean(frame_ai_real)),        3) if frame_ai_real        else 1.0
            deepfake_score = ensemble_fake
            real_score     = ensemble_real

            # 🛠️ Diagnostic Logging: Show exactly what each model thinks in the terminal
            logger.info(f"📊 Video Ensemble results:")
            logger.info(f"   Ensemble Fake: {ensemble_fake} | Real: {ensemble_real}")
            logger.info(f"   AI Prob (3-class mean): {ai_prob}")
            for m_id, m_res in model_results.items():
                logger.info(f"   └─ {m_id}: Fake={m_res['fake']:.3f}, Real={m_res['real']:.3f}")

            # Unified Decision Logic
            # Stricter thresholds for video to avoid false positives on compressed streams
            is_ai = (
                ai_prob >= 0.50   # Regular image is 0.40
            )

            if is_ai:
                verdict     = "AI Generated"
                is_fake     = True
                ref_score   = ai_prob
                trust_score = round((1.0 - ref_score) * 100, 1)
            elif deepfake_score >= 0.65: # Regular image is 0.50
                verdict     = "Deepfake"
                is_fake     = True
                trust_score = round((1.0 - deepfake_score) * 100, 1)
            else:
                verdict     = "Authentic"
                is_fake     = False
                trust_score = round(real_score * 100, 1)

            logger.info(f"Video verdict: {verdict} | ai={ai_prob}, ai_combined={ai_combined}, deepfake={deepfake_score}, real={real_score}")

            return {
                "verdict":        verdict,
                "is_fake":        is_fake,
                "trust_score":    trust_score,
                "ai_prob":        ai_prob,
                "deepfake_score": deepfake_score,
                "real_score":     real_score,
                "fake":           ensemble_fake,
                "real":           ensemble_real,
                "frames_analyzed": len(frame_predictions),
                "ensemble_average": True,
                "models_used":    len(all_predictions),
                "model_predictions": model_results,
            }

        except Exception as e:
            logger.error(f"Error classifying video: {str(e)}")
            raise
    
    def classify_audio_ensemble(self, audio_path):
        """Classify audio using Wav2Vec2 with threshold=0.5."""
        try:
            logger.info(f"Processing audio with Wav2Vec2: {audio_path}")

            if "audio_classifier" not in self.models:
                raise ValueError("Audio classifier (Wav2Vec2) not loaded")

            audio_model           = self.models["audio_classifier"]
            audio_feature_extractor = self.processors["audio_classifier"]
            audio_prediction      = self._predict_wav2vec2(audio_path, audio_model, audio_feature_extractor)

            if not audio_prediction:
                raise ValueError("Wav2Vec2 returned no prediction")

            fake_prob  = audio_prediction["fake"]
            real_prob  = audio_prediction["real"]

            # Apply threshold
            AUDIO_THRESHOLD = 0.60  # Increased from 0.50 to be more conservative
            if fake_prob >= AUDIO_THRESHOLD:
                verdict     = "Deepfake Audio"
                is_fake     = True
                trust_score = round((1.0 - fake_prob) * 100, 1)
            else:
                verdict     = "Authentic"
                is_fake     = False
                trust_score = round(real_prob * 100, 1)

            logger.info(f"Audio verdict: {verdict} | fake={fake_prob}, real={real_prob}")

            return {
                "verdict":     verdict,
                "is_fake":     is_fake,
                "trust_score": trust_score,
                "fake":        round(fake_prob, 3),
                "real":        round(real_prob, 3),
                "ensemble_average": True,
                "models_used": 1,
                "model_predictions": {"audio_classifier": audio_prediction},
            }

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
