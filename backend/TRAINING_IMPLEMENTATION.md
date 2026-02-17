# Model Training Pipeline - Implementation Summary

## Overview
Complete training infrastructure for deepfake detection models using your video dataset has been created.

## Files Created

### 1. **train_video_model.py**
- Trains XceptionNet for video frame deepfake detection
- Extracts 10 frames per video using MTCNN face detection
- Processes ~100 real videos + ~50 per fake category
- Output: `xceptionnet_model.h5` (~200-300 MB)

### 2. **train_image_model.py**
- Trains EfficientNetB3 for image-based detection
- Extracts first frame from videos for processing
- Higher sample count (~200 real + ~100 per fake category)
- Output: `efficientnet_model.h5` (~150-250 MB)

### 3. **train_audio_model.py**
- Trains MLP for audio manipulation detection
- Extracts MFCC features (40 coefficients) from audio tracks
- Detects lip-sync inconsistencies and audio anomalies
- Output: `audio_model.h5` (~5-10 MB)

### 4. **train_all_models.py** (Master Orchestrator)
- Coordinates training of all three models
- Generates unified training logs and reports
- Verifies model integrity after training
- Features:
  - Sequential model training
  - Error handling and recovery
  - Performance metrics aggregation
  - JSON training report

### 5. **quick_train.py** (Quick Start Script)
- One-command training interface
- Dependency and dataset validation
- Interactive user prompts
- Automatic error checking

### 6. **TRAINING_GUIDE.md**
- Comprehensive documentation
- Usage examples and tutorials
- Troubleshooting guide
- Performance expectations
- Hyperparameter reference

## Dataset Utilization

### Real Videos (Authentic - Label: 1)
```
DeepFakeDetection/: ~100 videos ──┐
original/: Limited subset         ├─→ 60% Train, 20% Val, 20% Test
                                  └──→ Extract faces for training
```

### Fake Videos (Manipulated - Label: 0)
```
Deepfakes/: ~50 videos     ┐
Face2Face/: ~50 videos     ├─→ 60% Train, 20% Val, 20% Test
FaceShifter/: ~50 videos   ├─→ Extract faces for training
FaceSwap/: ~50 videos      │
NeuralTextures/: ~50 videos└──→ Detect manipulation artifacts
```

## Model Architecture Overview

### Video Model (XceptionNet)
```
Input (224×224×3)
    ↓
Xception Pre-trained Backbone [ImageNet weights]
    ↓
Global Average Pooling
    ↓
Dense(512) + ReLU + Dropout(0.5)
    ↓
Dense(256) + ReLU + Dropout(0.5)
    ↓
Dense(128) + ReLU + Dropout(0.3)
    ↓
Dense(1) + Sigmoid
    ↓
Output (0-1): Authenticity Score
```

### Image Model (EfficientNetB3)
```
Input (224×224×3)
    ↓
EfficientNetB3 Pre-trained Backbone [ImageNet weights]
    ↓
Global Average Pooling
    ↓
Dense(512) + BatchNorm + Dropout(0.5)
    ↓
Dense(256) + BatchNorm + Dropout(0.5)
    ↓
Dense(128) + BatchNorm + Dropout(0.3)
    ↓
Dense(1) + Sigmoid
    ↓
Output (0-1): Authenticity Score
```

### Audio Model (MLP)
```
MFCC Features (120-dimensional)
    ↓
Dense(256) + ReLU + BatchNorm + Dropout(0.5)
    ↓
Dense(128) + ReLU + BatchNorm + Dropout(0.4)
    ↓
Dense(64) + ReLU + BatchNorm + Dropout(0.3)
    ↓
Dense(32) + ReLU + Dropout(0.2)
    ↓
Dense(1) + Sigmoid
    ↓
Output (0-1): Authenticity Score
```

## Training Parameters

### Unified Settings
- **Optimizer**: Adam (learning rate: 0.001)
- **Loss Function**: Binary Crossentropy
- **Batch Size**: 32
- **Epochs**: 30 (with early stopping at patience=10)
- **Validation Split**: 20% of training data
- **Test Split**: 20% of total data

### Face Detection
- **Method**: MTCNN (Multi-task Cascaded CNN)
- **Face Size**: 224×224 pixels
- **Input Normalization**: [0, 1] range

### Audio Feature Extraction
- **Sample Rate**: 22,050 Hz
- **MFCC Coefficients**: 40
- **Feature Dimensions**: 120 (mean + std + delta)

## Quick Start Guide

### Option 1: Automated Training
```bash
cd backend
python quick_train.py
```
Interactive setup that validates dependencies and dataset.

### Option 2: Master Script
```bash
cd backend
python train_all_models.py
```
Train all three models sequentially.

### Option 3: Individual Models
```bash
cd backend

# Video model only
python train_video_model.py

# Image model only
python train_image_model.py

# Audio model only
python train_audio_model.py
```

## Expected Outputs

### After Successful Training

#### Model Files (in `models/` directory)
```
models/
├── xceptionnet_model.h5                 (220 MB) ✓
├── xceptionnet_model_checkpoint.h5      (220 MB)
├── efficientnet_model.h5                (200 MB) ✓
├── efficientnet_model_checkpoint.h5     (200 MB)
├── audio_model.h5                       (8 MB) ✓
└── audio_model_checkpoint.h5            (8 MB)
```

#### Performance Reports
```
models/
├── video_metrics.json          Sample: {"accuracy": 0.87, "f1": 0.86, ...}
├── image_metrics.json          Sample: {"accuracy": 0.89, "f1": 0.88, ...}
└── audio_metrics.json          Sample: {"accuracy": 0.78, "f1": 0.76, ...}
```

#### Training Visualizations
```
models/
├── video_training_history.png   (Accuracy & Loss graphs)
├── image_training_history.png   (Accuracy & Loss graphs)
└── audio_training_history.png   (Accuracy & Loss graphs)
```

#### Logs and Reports
```
training.log                      (Detailed training transcript)
training_report.json              (JSON summary of all training)
```

## Performance Metrics Explained

For each model, you'll see:

```json
{
  "accuracy": 0.8734,           // Percentage of correct predictions
  "precision": 0.8521,          // True positives / (TP + FP)
  "recall": 0.8945,             // True positives / (TP + FN)
  "f1": 0.8729,                 // Harmonic mean of precision & recall
  "auc": 0.9134,                // Area under ROC curve
  "confusion_matrix": [          // Classification breakdown
    [TN, FP],
    [FN, TP]
  ]
}
```

## Integration with Application

### Automatic Model Loading
The trained models are automatically loaded by detectors:

```python
# app.py automatically uses trained models
video_detector = VideoDetector('models/xceptionnet_model.h5')
image_detector = ImageDetector('models/efficientnet_model.h5')
audio_detector = AudioDetector('models/audio_model.h5')
```

### Model Fusion
Results are combined using weighted fusion:

```python
fusion_logic = FusionLogic(
    image_weight=0.35,
    video_weight=0.35,
    audio_weight=0.30
)

fused_score = fusion_logic.fuse_results(
    image_score=85,
    video_score=88,
    audio_score=72
)
# Output: Combined verdict with confidence
```

## System Requirements

### Hardware
- **GPU**: NVIDIA with CUDA support (recommended, but CPU-compatible)
- **RAM**: Minimum 8GB, 16GB+ recommended
- **Storage**: 2-3 GB for models and training data

### Software
- Python 3.8+
- TensorFlow 2.13+
- CUDA 11.8 (for GPU acceleration)
- cuDNN 8.6 (for GPU acceleration)

### Training Time Estimates
- **Video Model**: 2-4 hours (with GPU)
- **Image Model**: 1-2 hours (with GPU)
- **Audio Model**: 30-60 minutes (with GPU)
- **Total**: 4-8 hours (sequential training)

With CPU only: 2-3x longer

## Troubleshooting Checklist

✓ Dataset exists and has video files
✓ ffmpeg installed (for audio extraction)
✓ GPU drivers updated (if using GPU)
✓ Required Python packages installed
✓ Sufficient disk space (3+ GB)
✓ Sufficient RAM (8+ GB)
✓ No corrupted video files
✓ Write permissions in `models/` directory

## Next Steps

1. **Run Training**
   ```bash
   python quick_train.py
   ```

2. **Monitor Progress**
   - Watch console output
   - Check `training.log` for detailed logs

3. **Verify Results**
   - Check `models/` directory for saved models
   - Review metrics in JSON files
   - Check training graphs (PNG files)

4. **Deploy Models**
   - Models are auto-loaded by the application
   - Run the Flask server with trained models
   - Start making predictions!

## Model Update Schedule

Models can be retrained:
- **Monthly**: With new deepfake samples
- **Quarterly**: With new deepfake techniques
- **Annually**: With larger dataset updates

Use the same training scripts with updated dataset paths.

## Support and Reference

- **TensorFlow/Keras**: https://www.tensorflow.org/
- **XceptionNet**: https://arxiv.org/abs/1610.02357
- **EfficientNet**: https://arxiv.org/abs/1905.11946
- **MTCNN**: https://arxiv.org/abs/1604.02878
- **FaceForensics**: https://github.com/ondyari/FaceForensics

---

**Status**: ✓ Complete and Ready for Training
**Last Updated**: 2026-02-03
