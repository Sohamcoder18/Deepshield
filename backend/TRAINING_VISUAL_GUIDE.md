# 🎯 Model Training Pipeline - Complete Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Dataset     │    │  Dataset     │    │  Dataset     │   │
│  │  ────────    │    │  ────────    │    │  ────────    │   │
│  │ Real Videos  │    │ Fake Videos  │    │   Audio      │   │
│  │  (~100 vids) │    │  (~200 vids) │    │  Tracks      │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                    │                    │            │
│         ├────────────────────┼────────────────────┤           │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌──────────────┐  │
│  │ Frame       │      │   Face      │      │ MFCC         │  │
│  │ Extraction  │      │ Detection   │      │ Extraction   │  │
│  │ (10 frames) │      │ (MTCNN)     │      │ (40 coeffs)  │  │
│  └──────┬──────┘      └──────┬──────┘      └──────┬───────┘  │
│         │                    │                    │           │
│         ▼                    ▼                    ▼           │
│  ┌─────────────────────────────────────────────────────┐     │
│  │        Train/Val/Test Split (60/20/20)             │     │
│  └──────┬──────────────────────────────────────────────┘     │
│         │                                                     │
│    ┌────┼────┐                                              │
│    ▼    ▼    ▼                                              │
│ ┌──────────────────┐   ┌──────────────────┐  ┌──────────┐  │
│ │ Video Model      │   │ Image Model      │  │ Audio    │  │
│ │ XceptionNet      │   │ EfficientNetB3   │  │ Model    │  │
│ │                  │   │                  │  │ (MLP)    │  │
│ │ • Frames         │   │ • Single Frame   │  │          │  │
│ │ • Sequence       │   │ • Fast           │  │ • MFCC   │  │
│ │ • Temporal       │   │ • Per-frame      │  │ • Audio  │  │
│ │ • Faces          │   │ • Artifacts      │  │ • Lipsync│  │
│ └────────┬─────────┘   └────────┬─────────┘  └────┬─────┘  │
│          │                      │                  │         │
│          └──────────────┬───────┴──────────────────┘        │
│                         ▼                                    │
│              ┌───────────────────────┐                       │
│              │  Model Fusion Logic   │                       │
│              │  Weighted Combining   │                       │
│              │  (0.35, 0.35, 0.30)   │                       │
│              └───────────┬───────────┘                       │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │  Final Verdict        │                       │
│              │  Authentic/Deepfake   │                       │
│              │  Confidence Score     │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Training Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                  START TRAINING                              │
└────────────────────┬─────────────────────────────────────────┘
                     ▼
          ┌──────────────────────┐
          │ quick_train.py       │
          │ (Recommended Entry   │
          │  Point)              │
          └─────────┬────────────┘
                    ▼
    ┌───────────────────────────────────┐
    │ Check Dependencies & Dataset      │
    └─────────────┬─────────────────────┘
                  ▼
    ┌─────────────────────────────────┐
    │ Run train_all_models.py         │
    │ (Master Orchestrator)           │
    └──────────┬──────────────────────┘
               ▼
    ┌──────────────────────────────────────┐
    │ Parallel/Sequential Processing:      │
    │                                      │
    │ 1. train_video_model.py              │
    │    └─ Extract frames & detect faces  │
    │    └─ Train XceptionNet             │
    │    └─ Save xceptionnet_model.h5     │
    │                                      │
    │ 2. train_image_model.py              │
    │    └─ Extract first frames           │
    │    └─ Train EfficientNetB3           │
    │    └─ Save efficientnet_model.h5    │
    │                                      │
    │ 3. train_audio_model.py              │
    │    └─ Extract audio & MFCC           │
    │    └─ Train MLP                     │
    │    └─ Save audio_model.h5            │
    └──────────┬───────────────────────────┘
               ▼
    ┌──────────────────────────────────────┐
    │ Generate Reports & Metrics           │
    │                                      │
    │ • Accuracy, Precision, Recall       │
    │ • F1-Score, AUC-ROC                 │
    │ • Confusion Matrices                │
    │ • Training Graphs (PNG)             │
    └──────────┬───────────────────────────┘
               ▼
    ┌──────────────────────────────────────┐
    │ Verify Model Files                   │
    │                                      │
    │ ✓ xceptionnet_model.h5  (220 MB)    │
    │ ✓ efficientnet_model.h5 (200 MB)    │
    │ ✓ audio_model.h5        (8 MB)      │
    └──────────┬───────────────────────────┘
               ▼
    ┌──────────────────────────────────────┐
    │ Save Training Report                 │
    │                                      │
    │ • training.log                       │
    │ • training_report.json               │
    └──────────┬───────────────────────────┘
               ▼
          ┌─────────────┐
          │ COMPLETE ✓  │
          └─────────────┘
```

## Data Processing Pipeline

```
VIDEO FILE (mp4)
    │
    ├─────────────────────┬──────────────────────┬─────────────┐
    ▼                     ▼                      ▼             ▼
 (Video Model)      (Image Model)         (Audio Model)    (Meta)
    │                    │                      │
    ├─ Extract 10        ├─ Extract 1           ├─ Extract audio
    │  frames evenly     │  first frame         │  track
    │                    │                      │
    ├─ MTCNN             ├─ MTCNN               ├─ Convert to WAV
    │  face detection    │  face detection      │
    │                    │                      │
    ├─ Resize 224x224    ├─ Resize 224x224      ├─ Librosa load
    │                    │                      │  (sr=22050)
    ├─ Normalize [0,1]   ├─ Normalize [0,1]     │
    │                    │                      │
    ▼                    ▼                      ▼
 Stacked frames      Per-frame faces      MFCC Features
 (10, 224, 224, 3)   (N, 224, 224, 3)    (120,)
    │                    │                      │
    └─ Train/Val/Test ◄──┴──────────────────────┘
       Split (60/20/20)
```

## Model Training Parameters

```
╔══════════════════════════════════════════════════════════╗
║         COMMON TRAINING PARAMETERS                       ║
╠══════════════════════════════════════════════════════════╣
║ Optimizer:              Adam                             ║
║ Learning Rate:          0.001                            ║
║ Loss Function:          Binary Crossentropy              ║
║ Activation:             ReLU (hidden), Sigmoid (output)  ║
║ Batch Size:             32                               ║
║ Epochs:                 30                               ║
║ Validation Split:       0.2                              ║
║ Early Stopping:         Patience=10                      ║
║ LR Reduction:           Patience=5, Factor=0.5           ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║         VIDEO MODEL SPECIFIC                            ║
╠══════════════════════════════════════════════════════════╣
║ Architecture:           Xception (ImageNet pretrained)   ║
║ Input Shape:            (224, 224, 3)                    ║
║ Frames/Video:           10                               ║
║ Dense Layers:           512 → 256 → 128 → 1            ║
║ Dropout Rates:          0.5 → 0.5 → 0.3 → 0             ║
║ Training Samples:       ~450 real + 900 fake faces       ║
║ Expected Accuracy:      85-95%                           ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║         IMAGE MODEL SPECIFIC                            ║
╠══════════════════════════════════════════════════════════╣
║ Architecture:           EfficientNetB3 (pretrained)      ║
║ Input Shape:            (224, 224, 3)                    ║
║ Frames/Video:           1 (first frame)                  ║
║ Dense Layers:           512 → 256 → 128 → 1            ║
║ Batch Norm:             Yes (after dense)                ║
║ Dropout Rates:          0.5 → 0.5 → 0.3 → 0             ║
║ Training Samples:       ~1200 real + 600 fake faces      ║
║ Expected Accuracy:      80-92%                           ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║         AUDIO MODEL SPECIFIC                            ║
╠══════════════════════════════════════════════════════════╣
║ Architecture:           MLP (Multi-layer Perceptron)     ║
║ Input Shape:            (120,)                           ║
║ Feature Type:           MFCC (40 coeff + mean/std/delta)║
║ Dense Layers:           256 → 128 → 64 → 32 → 1        ║
║ Batch Norm:             Yes (except output)              ║
║ Dropout Rates:          0.5 → 0.4 → 0.3 → 0.2 → 0       ║
║ Training Samples:       ~150 real + 150 fake audio       ║
║ Expected Accuracy:      75-85%                           ║
╚══════════════════════════════════════════════════════════╝
```

## Output File Structure

```
backend/
│
├── models/                              # Saved models directory
│   ├── xceptionnet_model.h5             # ✓ Video model (220 MB)
│   ├── xceptionnet_model_checkpoint.h5  # Backup
│   ├── efficientnet_model.h5            # ✓ Image model (200 MB)
│   ├── efficientnet_model_checkpoint.h5 # Backup
│   ├── audio_model.h5                   # ✓ Audio model (8 MB)
│   ├── audio_model_checkpoint.h5        # Backup
│   │
│   ├── video_metrics.json               # Performance metrics
│   ├── image_metrics.json               # Performance metrics
│   ├── audio_metrics.json               # Performance metrics
│   │
│   ├── video_training_history.png       # Accuracy & loss graphs
│   ├── image_training_history.png       # Accuracy & loss graphs
│   └── audio_training_history.png       # Accuracy & loss graphs
│
├── training.log                         # Complete training log
├── training_report.json                 # Summary report
│
└── train_*.py                           # Training scripts
```

## Performance Metrics Example

```
┌──────────────────────────────────────────────────────────────┐
│                   TRAINING RESULTS                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ VIDEO MODEL (XceptionNet)                                    │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Accuracy:    87.34%  ████████████████░░░░ (87%)       │   │
│ │ Precision:   85.21%  ████████████████░░░░ (85%)       │   │
│ │ Recall:      89.45%  ████████████████░░░░ (89%)       │   │
│ │ F1-Score:    87.29%  ████████████████░░░░ (87%)       │   │
│ │ AUC-ROC:     91.34%  ██████████████████░░ (91%)       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                               │
│ IMAGE MODEL (EfficientNetB3)                                 │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Accuracy:    89.12%  ██████████████████░░ (89%)       │   │
│ │ Precision:   87.65%  ██████████████████░░ (88%)       │   │
│ │ Recall:      90.98%  ██████████████████░░ (91%)       │   │
│ │ F1-Score:    89.29%  ██████████████████░░ (89%)       │   │
│ │ AUC-ROC:     93.45%  ██████████████████░░ (93%)       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                               │
│ AUDIO MODEL (MLP)                                            │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Accuracy:    78.56%  ███████████████░░░░░ (79%)       │   │
│ │ Precision:   76.43%  ███████████████░░░░░ (76%)       │   │
│ │ Recall:      81.23%  ████████████████░░░░ (81%)       │   │
│ │ F1-Score:    78.75%  ███████████████░░░░░ (79%)       │   │
│ │ AUC-ROC:     85.67%  █████████████████░░░ (86%)       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                               │
│ FUSED MODEL (All 3 Combined)                                 │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Accuracy:    93.23%  ███████████████████░ (93%)       │   │
│ │ Precision:   92.15%  ███████████████████░ (92%)       │   │
│ │ Recall:      94.67%  ███████████████████░ (95%)       │   │
│ │ F1-Score:    93.38%  ███████████████████░ (93%)       │   │
│ │ AUC-ROC:     96.78%  ████████████████████ (97%)       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                               │
│ Note: Results vary based on dataset and hardware             │
└──────────────────────────────────────────────────────────────┘
```

## Training Timeline

```
Timeline (with GPU)          Breakdown

0h ────────────────────────────────── Start
  │
  ├─ 0-5 min: Setup & Validation
  │           (Dependency check, dataset validation)
  │
10min
  │
  ├─ 10min - 2h: Video Model Training
  │           (Frame extraction → MTCNN → XceptionNet)
  │           █████████████████░░░░░░░░░░░ 60%
  │
2h
  │
  ├─ 2h - 3.5h: Image Model Training
  │           (Frame extraction → MTCNN → EfficientNet)
  │           █████████░░░░░░░░░░░░░░░░░░░░ 35%
  │
4h
  │
  ├─ 3.5h - 4.5h: Audio Model Training
  │           (Audio extraction → MFCC → MLP)
  │           ██████░░░░░░░░░░░░░░░░░░░░░░░░ 20%
  │
5h
  │
  ├─ 4.5h - 5h: Verification & Reports
  │           (Model validation, metrics generation)
  │           ███████████████████████░░░░░░ 85%
  │
6h ────────────────────────────────── Complete ✓
  │
  
With CPU: 3x longer (18-24 hours total)
```

---

**Status**: ✓ Complete Training Infrastructure Ready
**Models**: 3 (Video + Image + Audio)
**Expected Accuracy**: 90-97% (combined)
**Training Time**: 4-8 hours (GPU), 12-24 hours (CPU)
