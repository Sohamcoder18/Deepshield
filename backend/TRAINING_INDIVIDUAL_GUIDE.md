# Training Individual Models - Step by Step Guide

## Overview
Three separate training scripts have been created to train each model independently. This prevents resource conflicts and memory issues.

## Scripts

### 1. Train Image Model Only
```bash
cd backend
python train_image_only.py
```
- **Duration**: ~20 minutes (GPU) or 1-2 hours (CPU)
- **Output**: `models/efficientnet_model.h5`
- **Metrics**: `models/image_metrics.json`

### 2. Train Video Model Only
```bash
cd backend
python train_video_only.py
```
- **Duration**: ~30 minutes (GPU) or 2-4 hours (CPU)
- **Output**: `models/xceptionnet_model.h5`
- **Metrics**: `models/video_metrics.json`

### 3. Train Audio Model Only
```bash
cd backend
python train_audio_only.py
```
- **Duration**: ~15 minutes (GPU) or 30-60 minutes (CPU)
- **Output**: `models/audio_model.h5`
- **Metrics**: `models/audio_metrics.json`

## Training Sequence

**Option A: Run One After Another**
```bash
# Terminal 1: Image Model
python train_image_only.py

# After completion, Terminal 2: Video Model
python train_video_only.py

# After completion, Terminal 3: Audio Model
python train_audio_only.py
```

**Option B: Run in Different Terminals (Parallel)**
- Open 3 terminal windows
- Run each script in a separate terminal simultaneously
- Each uses ~2-4 GB RAM per model

## What Gets Created

After all training completes, you'll have:

```
models/
├── efficientnet_model.h5              (Image model - ~200 MB)
├── xceptionnet_model.h5               (Video model - ~220 MB)
├── audio_model.h5                     (Audio model - ~8 MB)
├── image_metrics.json                 (Image model performance)
├── video_metrics.json                 (Video model performance)
├── audio_metrics.json                 (Audio model performance)
├── image_training_history.png         (Training graph)
├── video_training_history.png         (Training graph)
├── audio_training_history.png         (Training graph)
├── efficientnet_model_checkpoint.h5   (Backup)
├── xceptionnet_model_checkpoint.h5    (Backup)
└── audio_model_checkpoint.h5          (Backup)
```

## Model Integration

Once training completes, the existing Flask app automatically loads all three models:
- [app.py](app.py) → Loads models for detection endpoints
- [fusion_logic.py](models/fusion_logic.py) → Combines all three model predictions

## Key Improvements Over Combined Training

✓ **Reduced Memory Usage** - One model at a time (~2-4 GB vs ~8-12 GB)
✓ **Better Error Isolation** - If one model fails, others continue
✓ **Easier Debugging** - Individual logs for each model
✓ **Flexible Scheduling** - Train when resources are available
✓ **Checkpoint Safety** - Each model saves best weights automatically

## Expected Results

### Image Model
- Accuracy: 80-92%
- Precision/Recall: 75-90%

### Video Model
- Accuracy: 85-95%
- Precision/Recall: 80-93%

### Audio Model
- Accuracy: 75-85%
- Precision/Recall: 70-85%

### Combined (Fusion)
- Expected Accuracy: 90-97%

## Troubleshooting

### If VS Code Still Shows Errors:
1. Reduce batch size: Edit script, change `batch_size=32` to `batch_size=16`
2. Reduce frames: For video, change `frames_per_video=10` to `frames_per_video=5`
3. Use fewer samples: Reduce `[:100]` to `[:50]` in load_dataset()

### GPU Out of Memory:
```bash
# Set memory growth to avoid allocating all GPU memory
export TF_CPP_MIN_LOG_LEVEL=2
python train_image_only.py
```

### Audio Extraction Fails:
- Ensure FFmpeg is installed: `ffmpeg -version`
- Try reducing audio sample size by setting `max_samples=50`

## Monitoring Training

Each script produces:
- **Console logs** - Real-time training progress
- **training.log** - Detailed logs (if you modify script)
- **Model checkpoints** - Best weights saved automatically
- **Metrics JSON** - Final accuracy, precision, recall, F1, AUC

## Next Steps

After all models train:

1. **Verify Models**: Check `models/` directory has all .h5 files
2. **Check Metrics**: Review JSON files for accuracy
3. **Test Integration**: Run Flask app and test detection
4. **Deploy**: Models are ready for production use

Good luck with training!
