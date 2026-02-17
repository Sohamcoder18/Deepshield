# Model Training Guide

## Overview
This guide explains how to train the deepfake detection models using the provided video dataset.

## Dataset Structure
```
dataset/
├── DeepFakeDetection/     # ~900+ authentic videos (label: 1)
│   └── *.mp4
├── Deepfakes/             # Deepfake videos (label: 0)
│   └── *.mp4
├── Face2Face/             # Face2Face manipulated videos (label: 0)
│   └── *.mp4
├── FaceShifter/           # FaceShifter manipulated videos (label: 0)
│   └── *.mp4
├── FaceSwap/              # FaceSwap manipulated videos (label: 0)
│   └── *.mp4
├── NeuralTextures/        # NeuralTextures manipulated videos (label: 0)
│   └── *.mp4
└── original/              # 1000 original videos (label: 1)
    └── *.mp4
```

## Models to be Trained

### 1. **Video Model (XceptionNet)**
- **Purpose**: Detect deepfakes in video frames
- **Architecture**: XceptionNet pretrained on ImageNet
- **Input**: Frame sequences extracted from videos
- **Output**: Authenticity score (0-1)
- **Features**:
  - Frame extraction from videos
  - Face detection using MTCNN
  - Transfer learning from ImageNet
  - Binary classification (real vs fake)

### 2. **Image Model (EfficientNetB3)**
- **Purpose**: Detect deepfakes in individual frames
- **Architecture**: EfficientNetB3 pretrained on ImageNet
- **Input**: Single frames from videos
- **Output**: Authenticity score (0-1)
- **Features**:
  - First frame extraction from videos
  - Face detection and alignment
  - Advanced image classification
  - Efficient neural architecture

### 3. **Audio Model (MLP)**
- **Purpose**: Detect audio manipulation and lip-sync inconsistencies
- **Architecture**: Deep neural network with batch normalization
- **Input**: MFCC (Mel-frequency cepstral coefficients) features
- **Output**: Authenticity score (0-1)
- **Features**:
  - MFCC feature extraction (40 coefficients)
  - Delta and acceleration features
  - Audio-visual consistency detection

## Prerequisites

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

### 2. Additional Dependencies
The training scripts require ffmpeg for audio extraction:
```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

## Training Methods

### Method 1: Train All Models (Recommended)
Run the complete training pipeline:
```bash
cd backend
python train_all_models.py
```

### Method 2: Train Individual Models
Train specific models:
```bash
cd backend

# Train video model only
python train_video_model.py

# Train image model only
python train_image_model.py

# Train audio model only
python train_audio_model.py
```

### Method 3: Skip Specific Models
```bash
cd backend

# Skip audio model
python train_all_models.py --skip-audio

# Skip video and audio models
python train_all_models.py --skip-video --skip-audio
```

## Training Parameters

### Video Model
- **Frames per video**: 10
- **Face size**: 224×224 pixels
- **Batch size**: 32
- **Epochs**: 30
- **Learning rate**: 0.001
- **Train/Val/Test split**: 60%/20%/20%
- **Data limit**: 100 real videos, 50 per fake category

### Image Model
- **Frames per video**: 1 (first frame only)
- **Face size**: 224×224 pixels
- **Batch size**: 32
- **Epochs**: 30
- **Learning rate**: 0.001
- **Train/Val/Test split**: 60%/20%/20%
- **Data limit**: 200 real videos, 100 per fake category

### Audio Model
- **MFCC coefficients**: 40
- **Sample rate**: 22050 Hz
- **Feature vector size**: 120 (40 mean + 40 std + 40 delta)
- **Batch size**: 32
- **Epochs**: 30
- **Learning rate**: 0.001
- **Train/Val/Test split**: 60%/20%/20%

## Training Output

After training completes, the following files are generated:

### Models
```
models/
├── xceptionnet_model.h5              # Video detection model
├── xceptionnet_model_checkpoint.h5   # Video model checkpoint
├── efficientnet_model.h5             # Image detection model
├── efficientnet_model_checkpoint.h5  # Image model checkpoint
├── audio_model.h5                    # Audio detection model
└── audio_model_checkpoint.h5         # Audio model checkpoint
```

### Metrics and Reports
```
models/
├── video_metrics.json                # Video model performance metrics
├── image_metrics.json                # Image model performance metrics
├── audio_metrics.json                # Audio model performance metrics
├── video_training_history.png        # Video training graphs
├── image_training_history.png        # Image training graphs
└── audio_training_history.png        # Audio training graphs
```

### Logs
```
training.log                          # Complete training log
training_report.json                  # Training summary report
```

## Understanding the Metrics

Each model's performance is measured with the following metrics:

- **Accuracy**: Overall percentage of correct predictions
- **Precision**: Of predicted fakes, how many were actually fake
- **Recall**: Of actual fakes, how many were detected
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under receiver operating characteristic curve
- **Confusion Matrix**: True positives, false positives, true negatives, false negatives

Example metrics output:
```
Video Model Metrics:
  Accuracy: 0.8734
  Precision: 0.8521
  Recall: 0.8945
  F1-Score: 0.8729
  AUC-ROC: 0.9134
```

## Training Tips

### 1. **GPU Acceleration**
For faster training, use GPU:
```python
import tensorflow as tf
print(f"GPUs available: {len(tf.config.list_physical_devices('GPU'))}")
```

### 2. **Monitor Training**
Watch the training log to detect overfitting:
- If validation loss increases while training loss decreases → overfitting
- Early stopping will automatically halt training

### 3. **Data Augmentation**
To improve model robustness, consider adding data augmentation:
```python
# Random brightness, contrast, and rotation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
```

### 4. **Hyperparameter Tuning**
Adjust these parameters for better performance:
```python
# In training scripts, modify:
epochs = 50              # Increase for longer training
batch_size = 16          # Smaller batch for more updates
learning_rate = 0.0001   # Lower for finer tuning
```

### 5. **Class Imbalance**
If datasets are imbalanced, use class weights:
```python
class_weights = {0: 1.0, 1: 1.5}  # Increase weight for minority class
model.fit(X_train, y_train, class_weight=class_weights, ...)
```

## Troubleshooting

### Issue: Out of Memory (OOM)
**Solution**: Reduce batch size or frame extraction rate
```python
batch_size = 16  # Reduce from 32
frames_per_video = 5  # Reduce from 10
```

### Issue: MTCNN Face Detection Fails
**Solution**: Skip frames with no faces detected
```python
# Already handled in data processor
if faces is None:
    continue
```

### Issue: Audio Extraction Fails
**Solution**: Ensure ffmpeg is installed and in PATH
```bash
# Verify ffmpeg installation
ffmpeg -version
```

### Issue: Model Not Converging
**Solution**: Adjust learning rate or reduce data
```python
# Use smaller learning rate
learning_rate = 0.0001

# Use subset of data for testing
video_files = sorted(real_path.glob("*.mp4"))[:50]  # Reduce sample size
```

## Next Steps

1. **Verify Models**: Check that all three model files exist in `models/` directory
2. **Update Detectors**: Models are automatically loaded by:
   - `ImageDetector`: Loads `efficientnet_model.h5`
   - `VideoDetector`: Loads `xceptionnet_model.h5`
   - `AudioDetector`: Loads `audio_model.h5`
3. **Test Models**: Use `test_models.py` to validate performance
4. **Deploy**: Transfer models to production environment

## Performance Expectations

Based on standard deepfake datasets:

- **Video Model**: 85-95% accuracy
- **Image Model**: 80-92% accuracy
- **Audio Model**: 75-85% accuracy
- **Fused Result**: 90-97% accuracy

Actual performance depends on:
- Dataset size and quality
- Model architecture and hyperparameters
- Hardware and training duration
- Deepfake generation method (Face2Face vs FaceSwap, etc.)

## References

- [XceptionNet Paper](https://arxiv.org/abs/1610.02357)
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [FaceForensics++ Dataset](https://github.com/ondyari/FaceForensics)
- [MTCNN Face Detection](https://arxiv.org/abs/1604.02878)
- [MFCC Features](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum)
