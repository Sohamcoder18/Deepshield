#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct training wrapper - directly runs training without subprocess complications
"""

import sys
import os
from pathlib import Path

# Set working directory to script location
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

print(f"Working directory: {os.getcwd()}")

# Import and run training
from train_video_model import main as train_video
from train_image_model import main as train_image
from train_audio_model import main as train_audio

print("\n" + "="*70)
print("DIRECT TRAINING - NO SUBPROCESS")
print("="*70)

# Train all models
print("\nTraining VIDEO model...")
train_video()

print("\nTraining IMAGE model...")
train_image()

print("\nTraining AUDIO model...")
train_audio()

print("\n" + "="*70)
print("ALL MODELS TRAINED")
print("="*70)
