# Enhanced Multi-Model Deepfake Detection System

## 📊 Current Ensemble Configuration

Successfully integrated **3 models** (2 image + 1 video) with weighted ensemble voting:

### Model Overview

| Model | Type | Weight | Status | Purpose |
|-------|------|--------|--------|---------|
| **SIGLIP** | Image (Frame) | 35% | ✅ Active | Pretrained deepfake detector v1 |
| **DeepFake v2** | Image (Frame) | 35% | ✅ Active | Newer ViT-based detector |
| **Naman712/Deep-fake-detection** | Video | 30% | ✅ Active `[Authenticated]` | Direct video classification |

**Total Weight:** 1.0 (100%)

---

## 🎬 Video Processing Pipeline

### Architecture

```
Input Video
    ↓
┌───────────────────────────────────────────┐
│  Parallel Processing                      │
├────────────────────────────────┬──────────┤
│                                │          │
│ Branch 1: Video Model          │         │
│ (30% weight)                   │         │
│ ├─ Feed full video             │  Branch 2: Image Models
│ ├─ Naman712/Deep-fake-detection│  (35% each, 5 frames)
│ └─ Get direct prediction       │  ├─ Extract 5 frames
│                                │  ├─ SIGLIP analysis
│                                │  ├─ DeepFake v2 analysis
│                                │  └─ Average across frames
│                                │
└────────────────────────────────┴──────────┘
                    ↓
        Combine All Predictions
                    ↓
        Weighted Ensemble Average
                    ↓
        Final Result: FAKE/REAL + Confidence
```

### Processing Sequence

1. **Video Model Analysis** (Parallel)
   - Direct video classification via pipeline
   - Returns: `{"fake": 0.X, "real": 0.Y}`
   - Weight: 30%

2. **Image Frame Analysis** (Parallel)
   - Extract 5 frames at even intervals
   - SIGLIP predicts on each frame
   - DeepFake v2 predicts on each frame
   - Average predictions across 5 frames
   - Weights: 35% each

3. **Ensemble Voting**
   ```python
   ensemble_fake = (video_fake * 0.30) + (siglip_avg_fake * 0.35) + (v2_avg_fake * 0.35)
   ensemble_real = (video_real * 0.30) + (siglip_avg_real * 0.35) + (v2_avg_real * 0.35)
   
   is_fake = ensemble_fake > ensemble_real
   confidence = max(ensemble_fake, ensemble_real)
   ```

---

## 🔌 API Integration

### Video Analysis Endpoint

```bash
POST /api/deepfake/analyze/video
Content-Type: multipart/form-data

file: <video_file>
```

### Response Format

```json
{
  "status": "success",
  "is_fake": true,
  "fake_confidence": 0.876,
  "real_confidence": 0.124,
  "prediction": {
    "fake": 0.876,
    "real": 0.124,
    "frames_analyzed": 5,
    "ensemble_average": true,
    "models_used": 3,
    "model_predictions": {
      "video_classifier": {
        "fake": 0.92,
        "real": 0.08
      },
      "siglip": {
        "fake": 0.84,
        "real": 0.16
      },
      "deepfake_v2": {
        "fake": 0.83,
        "real": 0.17
      }
    }
  },
  "processing_time": 4.231,
  "model_version": "multi-model-ensemble-v1",
  "models_used": 3
}
```

### Image Analysis Endpoint

```bash
POST /api/deepfake/analyze/image
Content-Type: multipart/form-data

file: <image_file>
```

Response includes predictions from SIGLIP and DeepFake v2 (video model not used for images).

---

## 📋 Implementation Details

### File Structure

```
backend/
├── models/
│   ├── multi_model_deepfake_service.py      ← Main ensemble service
│   ├── deepfake_result.py                   ← Database ORM
│   └── [other models...]
├── routes/
│   └── deepfake_routes.py                   ← API endpoints
├── app.py                                    ← Flask app initialization
└── VIDEO_MODEL_INTEGRATION.md                ← Documentation
```

### Key Methods

**Service Initialization:**
```python
from models.multi_model_deepfake_service import get_multi_model_deepfake_service

service = get_multi_model_deepfake_service()
# Loads all 3 models automatically
```

**Video Classification:**
```python
result = service.classify_video_ensemble(video_path, num_frames=5)
# Returns ensemble prediction with all model scores
```

**Image Classification:**
```python
result = service.classify_image_ensemble(image_path)
# Returns ensemble prediction (video model skipped for images)
```

---

## ⚙️ Configuration

### Model Weights

Located in `models/multi_model_deepfake_service.py`:

```python
self.available_models = {
    "siglip": {
        "model_name": "prithivMLmods/deepfake-detector-model-v1",
        "weight": 0.35,
        "type": "image",
        "enabled": True
    },
    "deepfake_v2": {
        "model_name": "prithivMLmods/Deep-Fake-Detector-v2-Model",
        "weight": 0.35,
        "type": "image",
        "enabled": True
    },
    "video_classifier": {
        "model_name": "Naman712/Deep-fake-detection",
        "weight": 0.30,
        "type": "video",
        "enabled": True
    }
}
```

### Adjusting Weights

To change model weights:
1. Edit the `weight` values in `available_models` dict
2. Ensure total weight = 1.0 for balanced ensemble
3. Restart Flask app to apply changes

---

## 🔐 Authentication Requirements

### HuggingFace Authentication

The video model `Naman712/Deep-fake-detection` is gated and requires HuggingFace authentication:

```bash
# Authenticate once (prompts for HF token)
huggingface-cli login

# Or set token via environment
export HF_TOKEN=<your_token>
```

Once authenticated, the model loads automatically in the ensemble.

---

## 📊 Performance Characteristics

### Processing Times (CPU)

| Task | Time |
|------|------|
| Initialize ensemble | 30-60s (first run, downloads models) |
| Initialize ensemble | 5-10s (subsequent runs, cached) |
| Analyze image | 1-2s |
| Analyze video (5 frames) | 3-5s |

### Model Coverage

- **Deepfake Videos**: ✅ Excellent (trained on deepfake dataset)
- **AI-Generated Images**: ⚠️ Limited (train data focused on deepfakes)
- **Synthetic Videos**: ⚠️ Limited (not primary focus)
- **Real Content**: ✅ Generally accurate

---

## 🔄 Fallback Behavior

### Model Loading Failures

If any model fails to load:
1. Service logs a warning
2. Continues with remaining models
3. Adjusts weights proportionally for ensemble
4. System remains functional with reduced accuracy

Example: If video model unavailable
```python
# Ensemble continues with 2 image models
# Weights recalculated: 50% SIGLIP, 50% DeepFake v2
```

---

## 📈 Future Enhancements

### Short Term
- [ ] Monitor accuracy per model type
- [ ] Collect prediction statistics
- [ ] Benchmark against baseline

### Medium Term
- [ ] Dynamic weight adjustment based on accuracy
- [ ] Add more video-specific models
- [ ] Implement frame caching for repeated uploads

### Long Term
- [ ] Fine-tune models on custom dataset
- [ ] Add specialized detectors for specific deepfake types
- [ ] Implement real-time video stream processing
- [ ] Add confidence calibration

---

## 🚀 Deployment Checklist

- [x] SIGLIP model loads successfully
- [x] DeepFake v2 model loads successfully
- [x] Video model authenticated and loads
- [x] API endpoints return ensemble predictions
- [x] Database persistence working
- [x] Error handling and graceful fallback
- [x] Response includes individual model predictions
- [x] Frame extraction functional for videos

**Status:** ✅ Production Ready

---

## 📞 Troubleshooting

### Video Model Access Error

```
Error: Access to model Naman712/Deep-fake-detection is restricted
Solution: Run `huggingface-cli login` and provide token
```

### Model Download Timeout

```
Error: Connection timeout downloading model
Solution: Increase timeout or pre-download models manually
```

### Low Accuracy on Specific Content

```
Action: Check which model performs best for your use case
Review: Individual model predictions in API response
Fine-tune: Adjust weights or add specialized model
```

---

## 📚 References

- **SIGLIP Model**: https://huggingface.co/prithivMLmods/deepfake-detector-model-v1
- **DeepFake v2**: https://huggingface.co/prithivMLmods/Deep-Fake-Detector-v2-Model
- **Video Model**: https://huggingface.co/Naman712/Deep-fake-detection (Gated)
- **Transformers Docs**: https://huggingface.co/docs/transformers
- **Video Classification Task**: https://huggingface.co/docs/transformers/en/tasks/video_classification
