#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Training Script - Runs training automatically without prompts
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("\n" + "=" * 70)
    print("DEEPFAKE DETECTION MODEL TRAINING - AUTO MODE")
    print("=" * 70)
    
    # Check dataset
    print("\nChecking dataset...")
    dataset_path = Path("../dataset")
    required_dirs = [
        "DeepFakeDetection",
        "Deepfakes",
        "Face2Face",
        "FaceShifter",
        "FaceSwap",
        "original"
    ]
    
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        if dir_path.exists():
            video_count = len(list(dir_path.glob("*.mp4")))
            print(f"  [OK] {dir_name} ({video_count} videos)")
        else:
            print(f"  [ERROR] {dir_name} - NOT FOUND")
            return False
    
    # Run training
    print("\n" + "=" * 70)
    print("STARTING DEEPFAKE DETECTION MODEL TRAINING")
    print("=" * 70)
    print("\nTraining three deepfake detection models:")
    print("  1. Video Model (XceptionNet)")
    print("  2. Image Model (EfficientNetB3)")
    print("  3. Audio Model (MLP)")
    print("\nThis may take several hours depending on GPU availability...")
    print("Check 'training.log' for detailed progress.\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'train_all_models.py'],
            cwd='.',
            check=False
        )
        
        if result.returncode != 0:
            print("[ERROR] Training failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error running training: {str(e)}")
        return False
    
    # Verify models
    print("\n" + "=" * 70)
    print("VERIFYING TRAINED MODELS")
    print("=" * 70)
    
    models_dir = Path("models")
    required_models = [
        'xceptionnet_model.h5',
        'efficientnet_model.h5',
        'audio_model.h5'
    ]
    
    all_found = True
    for model_name in required_models:
        model_path = models_dir / model_name
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {model_name} ({size_mb:.1f} MB)")
        else:
            print(f"  [MISSING] {model_name}")
            all_found = False
    
    if all_found:
        print("\n" + "=" * 70)
        print("[OK] TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nAll models have been trained and saved!")
        print("The application will use these models for:")
        print("  - Video deepfake detection")
        print("  - Image deepfake detection")
        print("  - Audio manipulation detection")
        return True
    else:
        print("\n[ERROR] Some models were not found after training")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTraining cancelled by user.")
        sys.exit(1)
