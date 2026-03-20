"""
Audio Ensemble Configuration Guide
Enables using both BiGRU+Attention and Pretrained models together
"""

import os
import logging

logger = logging.getLogger(__name__)

# Default model paths
DEFAULT_BIGRU_ATTENTION_MODEL = os.path.join(
    os.path.dirname(__file__), 
    'checkpoints/audio_bigruattention_model.pt'
)

DEFAULT_PRETRAINED_MODEL = os.path.join(
    os.path.dirname(__file__),
    'checkpoints/audio_pretrained_wav2vec2_checkpoint.pt'
)

# Ensemble configuration
ENSEMBLE_CONFIG = {
    # Use ensemble voting when both models available
    'use_ensemble': True,
    
    # Weighting strategy:
    # 'confidence': Weight by prediction confidence (recommended)
    # 'equal': Give equal weight to both models
    # 'priority': Prioritize one model over the other
    'weighting_strategy': 'confidence',
    
    # Confidence threshold for binary classification
    'confidence_threshold': 0.5,
    
    # Dictionary confidence threshold for reporting high/medium/low confidence
    'high_confidence_threshold': 0.75,
    'medium_confidence_threshold': 0.55,
    
    # CPU/GPU settings
    'device': 'cuda',  # or 'cpu'
}


def check_model_availability():
    """
    Check which audio detection models are available
    
    Returns:
        dict: Available models and their status
    """
    status = {
        'bigruattention': {
            'available': os.path.exists(DEFAULT_BIGRU_ATTENTION_MODEL),
            'path': DEFAULT_BIGRU_ATTENTION_MODEL
        },
        'pretrained': {
            'available': os.path.exists(DEFAULT_PRETRAINED_MODEL),
            'path': DEFAULT_PRETRAINED_MODEL
        },
        'ensemble_available': False
    }
    
    # Ensemble available only if both models exist
    status['ensemble_available'] = (
        status['bigruattention']['available'] and 
        status['pretrained']['available']
    )
    
    logger.info(f"Model Status: {status}")
    return status


def get_audio_detector_with_ensemble(
    bigruattention_path=None,
    pretrained_path=None,
    use_ensemble=True
):
    """
    Factory function to create AudioDeepfakeDetector with ensemble support
    
    Args:
        bigruattention_path: Path to BiGRU+Attention model (None = use default)
        pretrained_path: Path to pretrained model (None = use default)
        use_ensemble: Whether to enable ensemble voting
    
    Returns:
        AudioDeepfakeDetector: Detector instance with loaded models
    """
    from audio_deepfake_detector import AudioDeepfakeDetector
    
    # Use defaults if not provided
    if bigruattention_path is None:
        bigruattention_path = DEFAULT_BIGRU_ATTENTION_MODEL if os.path.exists(DEFAULT_BIGRU_ATTENTION_MODEL) else None
    
    if pretrained_path is None:
        pretrained_path = DEFAULT_PRETRAINED_MODEL if os.path.exists(DEFAULT_PRETRAINED_MODEL) else None
    
    detector = AudioDeepfakeDetector(
        model_path=bigruattention_path,
        pretrained_checkpoint=pretrained_path,
        use_ensemble=use_ensemble
    )
    
    return detector


if __name__ == "__main__":
    """Quick test of model availability"""
    status = check_model_availability()
    
    print("=" * 60)
    print("Audio Ensemble Model Status")
    print("=" * 60)
    print(f"BiGRU+Attention Available: {status['bigruattention']['available']}")
    print(f"Pretrained Model Available: {status['pretrained']['available']}")
    print(f"Ensemble Available: {status['ensemble_available']}")
    print("=" * 60)
    
    if status['ensemble_available']:
        print("\n✅ Both models available - Ensemble enabled!")
        print("\nEnsemble Configuration:")
        for key, value in ENSEMBLE_CONFIG.items():
            print(f"  {key}: {value}")
    else:
        print("\n⚠️  Not all models available for ensemble")
        if status['bigruattention']['available']:
            print("  ✓ BiGRU+Attention model available")
        if status['pretrained']['available']:
            print("  ✓ Pretrained model available")
