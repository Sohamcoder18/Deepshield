#!/usr/bin/env python
"""
Quick Start Training Script - One-command model training
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'tensorflow',
        'keras',
        'numpy',
        'opencv-python',
        'librosa',
        'mtcnn',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'soundfile'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_dataset():
    """Check if dataset exists"""
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
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        exists = dir_path.exists()
        status = "✓" if exists else "✗"
        
        if exists:
            video_count = len(list(dir_path.glob("*.mp4")))
            print(f"  {status} {dir_name} ({video_count} videos)")
        else:
            print(f"  {status} {dir_name} - MISSING")
            all_exist = False
    
    return all_exist

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    print("\nChecking ffmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("  ✓ ffmpeg is installed")
            return True
        else:
            print("  ✗ ffmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("  ✗ ffmpeg is not installed")
        print("    Install with: pip install ffmpeg-python")
        return False
    except Exception as e:
        print(f"  ✗ Error checking ffmpeg: {str(e)}")
        return False

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\nInstalling missing packages: {', '.join(packages)}")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install'] + packages,
            check=True
        )
        print("✓ Packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install packages")
        return False

def run_training():
    """Run the training pipeline"""
    print("\n" + "=" * 70)
    print("STARTING DEEPFAKE DETECTION MODEL TRAINING")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, 'train_all_models.py'],
            cwd='.',
            check=False
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running training: {str(e)}")
        return False

def verify_models():
    """Verify trained models"""
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
        exists = model_path.exists()
        status = "✓" if exists else "✗"
        
        if exists:
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  {status} {model_name} ({size_mb:.1f} MB)")
        else:
            print(f"  {status} {model_name} - NOT FOUND")
            all_found = False
    
    return all_found

def main():
    """Main entry point"""
    
    print("\n" + "=" * 70)
    print("DEEPFAKE DETECTION MODEL TRAINING - QUICK START")
    print("=" * 70)
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print("\nMissing packages detected!")
        response = input("Install missing packages? (y/n): ").lower()
        if response == 'y':
            if not install_missing_packages(missing):
                print("Failed to install packages. Exiting.")
                return False
        else:
            print("Cannot proceed without required packages.")
            return False
    
    # Check dataset
    if not check_dataset():
        print("\n✗ Dataset not found!")
        print("Please ensure the dataset folder structure is correct:")
        print("  ../dataset/DeepFakeDetection/")
        print("  ../dataset/Deepfakes/")
        print("  ../dataset/Face2Face/")
        print("  ../dataset/FaceShifter/")
        print("  ../dataset/FaceSwap/")
        print("  ../dataset/original/")
        return False
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("\n⚠ ffmpeg not found - audio training may fail")
        print("Install ffmpeg to enable audio model training")
    
    # Confirm training
    print("\n" + "=" * 70)
    print("READY TO START TRAINING")
    print("=" * 70)
    print("\nThis will train three deepfake detection models:")
    print("  1. Video Model (XceptionNet)")
    print("  2. Image Model (EfficientNetB3)")
    print("  3. Audio Model (MLP)")
    print("\nTraining may take several hours depending on GPU availability.")
    print("A log file will be saved to 'training.log'")
    
    response = input("\nContinue with training? (y/n): ").lower()
    if response != 'y':
        print("Training cancelled.")
        return True
    
    # Run training
    if not run_training():
        print("\n✗ Training failed!")
        print("Check 'training.log' for details.")
        return False
    
    # Verify models
    if verify_models():
        print("\n" + "=" * 70)
        print("✓ TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nAll models have been trained and saved in the 'models/' directory.")
        print("\nModels will be automatically loaded by the application for:")
        print("  - Video deepfake detection")
        print("  - Image deepfake detection")
        print("  - Audio manipulation detection")
        print("\nYou can now run the application with these trained models!")
        return True
    else:
        print("\n✗ Some models were not found after training")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTraining cancelled by user.")
        sys.exit(1)
