"""
Advanced Deepfake Detection Models
Implements Vision Transformer (ViT) + Temporal Modeling for state-of-the-art detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import ViTModel, ViTImageProcessor
import logging
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ViTDeepfakeDetector(nn.Module):
    """
    Vision Transformer-based Deepfake Detector
    Uses ViT-base-patch16-224 from Google's pretrained models
    Superior to CNN-based approaches for artifact detection
    """
    
    def __init__(self, pretrained: bool = True, num_classes: int = 2, dropout: float = 0.3):
        """
        Initialize ViT-based detector
        
        Args:
            pretrained: Load pretrained ImageNet-21k weights
            num_classes: Number of classes (2: real/fake)
            dropout: Dropout rate for regularization
        """
        super().__init__()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # Load Vision Transformer base model
            logger.info("Loading Vision Transformer (ViT-base-patch16-224)...")
            self.vit = ViTModel.from_pretrained(
                "google/vit-base-patch16-224",
                num_labels=num_classes,
                ignore_mismatched_sizes=True
            )
            self.vit.to(self.device)
            logger.info("✅ ViT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ViT model: {e}")
            self.vit = None
        
        # Classification head
        hidden_size = 768  # ViT-base hidden dimension
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
        
        self.classifier.to(self.device)
    
    def forward(self, images: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for batch of images
        
        Args:
            images: Tensor of shape (B, 3, 224, 224)
            
        Returns:
            Tuple of (logits, probabilities)
        """
        if self.vit is None:
            raise RuntimeError("ViT model not loaded")
        
        # Extract features from ViT
        with torch.no_grad():
            vit_output = self.vit(images, output_hidden_states=True)
            # Use [CLS] token representation
            cls_token = vit_output.last_hidden_state[:, 0, :]  # (B, 768)
        
        # Classification
        logits = self.classifier(cls_token)
        probs = F.softmax(logits, dim=1)
        
        return logits, probs
    
    def predict(self, image_tensor: torch.Tensor) -> float:
        """
        Predict fake probability for a single image
        
        Args:
            image_tensor: Single image tensor (3, 224, 224)
            
        Returns:
            Probability of being fake (0-1)
        """
        self.eval()
        with torch.no_grad():
            image_batch = image_tensor.unsqueeze(0).to(self.device)
            _, probs = self.forward(image_batch)
            # Index 1 is fake class
            fake_prob = float(probs[0, 1].cpu().numpy())
        return fake_prob


class InceptionResNetV2Detector(nn.Module):
    """
    Inception-ResNet-v2 Backbone for Deepfake Detection
    Superior feature extraction compared to XceptionNet
    """
    
    def __init__(self, pretrained: bool = True, num_classes: int = 2, dropout: float = 0.3):
        """
        Initialize Inception-ResNet-v2 detector
        
        Args:
            pretrained: Load pretrained ImageNet weights
            num_classes: Number of classes (2: real/fake)
            dropout: Dropout rate
        """
        super().__init__()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            from torchvision.models import inception_resnet_v2
            logger.info("Loading Inception-ResNet-v2 backbone...")
            
            self.backbone = inception_resnet_v2(
                pretrained=pretrained,
                num_classes=num_classes
            )
            self.backbone.to(self.device)
            
            # Replace final layer with enhanced classifier
            in_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()  # Remove original classifier
            
            self.classifier = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(in_features, 512),
                nn.ReLU(),
                nn.BatchNorm1d(512),
                nn.Dropout(dropout),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.BatchNorm1d(256),
                nn.Dropout(dropout),
                nn.Linear(256, num_classes)
            )
            
            self.classifier.to(self.device)
            logger.info("✅ Inception-ResNet-v2 loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Inception-ResNet-v2: {e}")
            self.backbone = None
    
    def forward(self, images: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        if self.backbone is None:
            raise RuntimeError("Backbone not loaded")
        
        features = self.backbone(images)  # (B, in_features)
        logits = self.classifier(features)
        probs = F.softmax(logits, dim=1)
        
        return logits, probs
    
    def predict(self, image_tensor: torch.Tensor) -> float:
        """Predict fake probability"""
        self.eval()
        with torch.no_grad():
            image_batch = image_tensor.unsqueeze(0).to(self.device)
            _, probs = self.forward(image_batch)
            fake_prob = float(probs[0, 1].cpu().numpy())
        return fake_prob


class TemporalDeepfakeDetector(nn.Module):
    """
    Video Deepfake Detector with Temporal Modeling
    Combines CNN frame encoder with LSTM/Transformer for temporal consistency
    Detects inconsistencies across frames that indicate manipulation
    """
    
    def __init__(self, num_classes: int = 2, use_transformer: bool = True, dropout: float = 0.3):
        """
        Initialize temporal detector
        
        Args:
            num_classes: Real/Fake classes
            use_transformer: Use Transformer instead of LSTM
            dropout: Dropout rate
        """
        super().__init__()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_transformer = use_transformer
        
        try:
            # Use Inception-ResNet-v2 as frame encoder
            from torchvision.models import inception_resnet_v2
            logger.info("Loading frame encoder (Inception-ResNet-v2)...")
            
            self.frame_encoder = inception_resnet_v2(pretrained=True)
            self.frame_encoder.fc = nn.Identity()  # Remove classifier
            self.feature_dim = self.frame_encoder.fc.in_features if hasattr(self.frame_encoder, 'fc') else 1536
            
            self.frame_encoder.to(self.device)
            logger.info("✅ Frame encoder loaded")
            
        except Exception as e:
            logger.error(f"Failed to load frame encoder: {e}")
            self.frame_encoder = None
        
        # Temporal modeling head
        if use_transformer:
            logger.info("Using Transformer for temporal modeling")
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=256,
                nhead=8,
                dim_feedforward=512,
                dropout=dropout,
                batch_first=True
            )
            self.temporal_encoder = nn.TransformerEncoder(encoder_layer, num_layers=2)
            temporal_out_dim = 256
        else:
            logger.info("Using LSTM for temporal modeling")
            self.temporal_encoder = nn.LSTM(
                input_size=256,
                hidden_size=256,
                num_layers=2,
                dropout=dropout,
                batch_first=True,
                bidirectional=True
            )
            temporal_out_dim = 512  # bidirectional
        
        # Feature projection
        self.feature_projection = nn.Sequential(
            nn.Linear(self.feature_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(dropout)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(temporal_out_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
        
        self.feature_projection.to(self.device)
        self.temporal_encoder.to(self.device)
        self.classifier.to(self.device)
    
    def forward(self, frames: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for video frames
        
        Args:
            frames: Tensor of shape (B, T, 3, 224, 224) where T is number of frames
            
        Returns:
            Tuple of (logits, probabilities)
        """
        if self.frame_encoder is None:
            raise RuntimeError("Frame encoder not loaded")
        
        batch_size, num_frames, c, h, w = frames.shape
        
        # Encode each frame
        frame_features = []
        self.frame_encoder.eval()
        with torch.no_grad():
            for t in range(num_frames):
                frame = frames[:, t, :, :, :].to(self.device)
                feat = self.frame_encoder(frame)  # (B, feature_dim)
                frame_features.append(feat)
        
        frame_features = torch.stack(frame_features, dim=1)  # (B, T, feature_dim)
        
        # Project features
        B, T, F = frame_features.shape
        frame_features_flat = frame_features.view(B * T, F)
        projected = self.feature_projection(frame_features_flat)  # (B*T, 256)
        projected = projected.view(B, T, -1)  # (B, T, 256)
        
        # Temporal encoding
        if self.use_transformer:
            temporal_out = self.temporal_encoder(projected)
            # Use [CLS] equivalent (mean pooling)
            temporal_features = temporal_out.mean(dim=1)  # (B, 256)
        else:
            _, (hidden, _) = self.temporal_encoder(projected)
            # Use final hidden state from bidirectional LSTM
            temporal_features = hidden[-1]  # (B, 512)
        
        # Classification
        logits = self.classifier(temporal_features)
        probs = F.softmax(logits, dim=1)
        
        return logits, probs
    
    def predict(self, frame_tensors: List[torch.Tensor]) -> float:
        """
        Predict fake probability for video frames
        
        Args:
            frame_tensors: List of frame tensors (3, 224, 224)
            
        Returns:
            Probability of being fake (0-1)
        """
        self.eval()
        with torch.no_grad():
            # Stack frames into batch
            frames_batch = torch.stack(frame_tensors, dim=1)  # (1, T, 3, 224, 224)
            frames_batch = frames_batch.to(self.device)
            _, probs = self.forward(frames_batch)
            fake_prob = float(probs[0, 1].cpu().numpy())
        return fake_prob


class MultiHeadEnsembleDetector(nn.Module):
    """
    Ensemble of multiple model architectures for robust detection
    Combines ViT, Inception-ResNet-v2, and Temporal modeling
    """
    
    def __init__(self, use_vit: bool = True, use_inception: bool = True, 
                 use_temporal: bool = True, weights: Optional[dict] = None):
        """
        Initialize ensemble
        
        Args:
            use_vit: Include Vision Transformer
            use_inception: Include Inception-ResNet-v2
            use_temporal: Include Temporal detector for video
            weights: Custom weights for model averaging
        """
        super().__init__()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        
        if use_vit:
            logger.info("[ENSEMBLE] Loading Vision Transformer...")
            try:
                self.models['vit'] = ViTDeepfakeDetector(pretrained=True)
                self.models['vit'].to(self.device)
            except Exception as e:
                logger.warning(f"[ENSEMBLE] Failed to load ViT: {e}")
        
        if use_inception:
            logger.info("[ENSEMBLE] Loading Inception-ResNet-v2...")
            try:
                self.models['inception'] = InceptionResNetV2Detector(pretrained=True)
                self.models['inception'].to(self.device)
            except Exception as e:
                logger.warning(f"[ENSEMBLE] Failed to load Inception: {e}")
        
        if use_temporal:
            logger.info("[ENSEMBLE] Loading Temporal detector...")
            try:
                self.models['temporal'] = TemporalDeepfakeDetector(use_transformer=True)
                self.models['temporal'].to(self.device)
            except Exception as e:
                logger.warning(f"[ENSEMBLE] Failed to load Temporal: {e}")
        
        # Set default weights if not provided
        self.weights = weights or {
            'vit': 0.4,
            'inception': 0.35,
            'temporal': 0.25
        }
        
        logger.info(f"[ENSEMBLE] Models loaded: {list(self.models.keys())}")
        logger.info(f"[ENSEMBLE] Weights: {self.weights}")
    
    def predict_image(self, image_tensor: torch.Tensor) -> Tuple[float, dict]:
        """
        Ensemble prediction for single image
        
        Args:
            image_tensor: Single image tensor (3, 224, 224)
            
        Returns:
            Tuple of (ensemble_score, individual_scores)
        """
        scores = {}
        total_weight = 0
        weighted_score = 0
        
        if 'vit' in self.models:
            try:
                score = self.models['vit'].predict(image_tensor)
                weight = self.weights.get('vit', 0)
                scores['vit'] = score
                weighted_score += score * weight
                total_weight += weight
            except Exception as e:
                logger.debug(f"ViT prediction failed: {e}")
        
        if 'inception' in self.models:
            try:
                score = self.models['inception'].predict(image_tensor)
                weight = self.weights.get('inception', 0)
                scores['inception'] = score
                weighted_score += score * weight
                total_weight += weight
            except Exception as e:
                logger.debug(f"Inception prediction failed: {e}")
        
        ensemble_score = weighted_score / total_weight if total_weight > 0 else 0.5
        
        return ensemble_score, scores
    
    def predict_video(self, frame_tensors: List[torch.Tensor]) -> Tuple[float, dict]:
        """
        Ensemble prediction for video frames
        
        Args:
            frame_tensors: List of frame tensors
            
        Returns:
            Tuple of (ensemble_score, individual_scores)
        """
        scores = {}
        total_weight = 0
        weighted_score = 0
        
        if 'temporal' in self.models:
            try:
                score = self.models['temporal'].predict(frame_tensors)
                weight = self.weights.get('temporal', 0)
                scores['temporal'] = score
                weighted_score += score * weight
                total_weight += weight
            except Exception as e:
                logger.debug(f"Temporal prediction failed: {e}")
        
        # Fall back to image-based prediction if temporal fails
        if total_weight == 0 and frame_tensors:
            center_frame = frame_tensors[len(frame_tensors) // 2]
            return self.predict_image(center_frame)
        
        ensemble_score = weighted_score / total_weight if total_weight > 0 else 0.5
        
        return ensemble_score, scores
