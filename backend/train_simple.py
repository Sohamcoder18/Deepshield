#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Direct Training Script - Trains all models without subprocess complications
Directly imports and runs training functions
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Direct training execution"""
    
    logger.info("\n" + "=" * 70)
    logger.info("DIRECT TRAINING PIPELINE - ALL MODELS")
    logger.info("=" * 70)
    logger.info(f"Start Time: {datetime.now().isoformat()}")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'video_model': None,
        'image_model': None,
        'audio_model': None
    }
    
    # Video Model Training
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING VIDEO MODEL (XceptionNet)")
    logger.info("=" * 70)
    try:
        from train_video_model import main as train_video
        train_video()
        results['video_model'] = 'completed'
        logger.info("[OK] VIDEO MODEL TRAINING COMPLETED")
    except Exception as e:
        logger.error(f"[ERROR] VIDEO MODEL TRAINING FAILED: {e}")
        results['video_model'] = f'failed: {str(e)}'
    
    # Image Model Training
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING IMAGE MODEL (EfficientNet)")
    logger.info("=" * 70)
    try:
        from train_image_model import main as train_image
        train_image()
        results['image_model'] = 'completed'
        logger.info("[OK] IMAGE MODEL TRAINING COMPLETED")
    except Exception as e:
        logger.error(f"[ERROR] IMAGE MODEL TRAINING FAILED: {e}")
        results['image_model'] = f'failed: {str(e)}'
    
    # Audio Model Training
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING AUDIO MODEL (MLP)")
    logger.info("=" * 70)
    try:
        from train_audio_model import main as train_audio
        train_audio()
        results['audio_model'] = 'completed'
        logger.info("[OK] AUDIO MODEL TRAINING COMPLETED")
    except Exception as e:
        logger.error(f"[ERROR] AUDIO MODEL TRAINING FAILED: {e}")
        results['audio_model'] = f'failed: {str(e)}'
    
    # Final verification
    logger.info("\n" + "=" * 70)
    logger.info("VERIFYING TRAINED MODELS")
    logger.info("=" * 70)
    
    models_dir = Path("models")
    expected_models = {
        'xceptionnet_model.h5': 'VIDEO',
        'efficientnet_model.h5': 'IMAGE',
        'audio_model.h5': 'AUDIO'
    }
    
    for model_file, model_type in expected_models.items():
        model_path = models_dir / model_file
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            logger.info(f"[OK] {model_type}: {model_file} ({size_mb:.2f} MB)")
        else:
            logger.warning(f"[MISSING] {model_type}: {model_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING PIPELINE COMPLETED")
    logger.info("=" * 70)
    
    # Save results
    with open('training_results_simple.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: training_results_simple.json\n")


if __name__ == "__main__":
    main()
