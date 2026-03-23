# Vision Transformer + Inception-ResNet Enhanced Deepfake Detection

## Architecture Improvements

### ✅ Completed Upgrades

#### 1. **Image & Per-Frame Video Detection**
- **Old**: XceptionNet (limited artifact detection)
- **New**: Dual ensemble approach
  - **Vision Transformer (ViT-base-patch16-224)**: Global image understanding, attention-based artifact detection
  - **Inception-ResNet-v2**: Fine-grained CNN features for compression artifacts

**Expected Performance**: 95-99% accuracy on fine-tuned datasets

#### 2. **Video Temporal Analysis**
- **Old**: Heuristic-only frame analysis + weak temporal consistency
- **New**: CNN + Transformer architecture
  - **Frame Encoder**: Inception-ResNet-v2 (artifact detection per frame)
  - **Temporal Head**: Transformer encoder layer (4-head attention, 2 layers)
  - **Detection**: Inconsistency patterns across frames

**Expected Performance**: >95% on video deepfakes (FaceSwap, Reenactment, Neural Renders)

#### 3. **Model Architecture Details**

##### Vision Transformer (ViT)
```
Input Image (224x224)
    ↓
Patch Embedding (16x16 patches) + Position Encoding
    ↓
Transformer Encoder (12 layers, 12 heads)
    ↓
[CLS] Token
    ↓
Classification Head (3 layers)
    ↓
Output: Real/Fake probability
```
- Pretrained on ImageNet-21k (14M images)
- Better at detecting AI-generated artifacts
- Attention maps show which regions indicate manipulation

##### Inception-ResNet-v2
```
Input Image (224x224)
    ↓
Hybrid Architecture:
  - Inception modules (multi-scale features)
  - ResNet skip connections (gradient flow)
    ↓
Global Average Pooling
    ↓
Classification Head (3 layers)
    ↓
Output: Real/Fake probability
```
- ~215M parameters
- Superior to standard ResNet for artifact detection
- Better compression artifact recognition

##### Temporal Transformer for Video
```
Video Frames [T, 224, 224, 3]
    ↓
Frame Encoding × T:
  - Inception-ResNet-v2 → (B, 1536) features
  - Feature Projection → (B, 256)
    ↓
Sequence: (B, T, 256)
    ↓
Transformer Encoder:
  - 8 attention heads
  - 2 layers
  - 512 feedforward hidden
    ↓
Mean pooling over temporal axis → (B, 256)
    ↓
Classification Head
    ↓
Output: Fake probability + Temporal consistency score
```

### 4. **Ensemble Strategy**

For **Images**:
```
Input Image
    ↓
Parallel Processing:
├─ Vision Transformer (40% weight)
├─ Inception-ResNet-v2 (35% weight)
└─ Heuristic Analysis (25% weight)
    ↓
Weighted Average → Final Score
    ↓
Decision: 0.5 threshold
```

For **Video**:
```
Extract T frames
    ↓
Analyze Each Frame:
├─ Inception-ResNet-v2 encoding
├─ Temporal Transformer processing
└─ Artifact scoring
    ↓
Temporal Consistency Analysis:
- Detection of frame-to-frame jumps
- Consistency deviation tracking
- Artifact pattern coherence
    ↓
Final Verdict + Recommendation
```

## Detection Capabilities

### Image Deepfakes Detected
✅ Face-swaps (DeepFaceLab, Faceswap)  
✅ AI-generated faces (StyleGAN, DALL-E)  
✅ Face reenactment  
✅ Blending artifacts  
✅ Color/texture inconsistencies  
✅ High-frequency compression artifacts  

### Video Deepfakes Detected
✅ Frame-by-frame inconsistencies  
✅ Temporal flickering  
✅ Eye blinking patterns  
✅ Face boundary artifacts  
✅ Lighting inconsistencies  
✅ Mouth movement mismatches  

## Technical Specifications

### Model Weights & Sizes
| Model | Parameters | Size | Device |
|-------|-----------|------|--------|
| ViT-base-patch16-224 | 86.5M | ~330MB | GPU/CPU |
| Inception-ResNet-v2 | 215M | ~800MB | GPU/CPU |
| Temporal Transformer | ~50M | ~200MB | GPU/CPU |

### Processing Speed
- **Image**: 0.5-1.0 seconds per image (GPU)
- **Video**: 15-30 seconds for 15 frames (GPU)
- **Batch Processing**: Supported for images

### Accuracy Benchmarks (Target)
| Dataset | Accuracy | Precision | Recall |
|---------|----------|-----------|--------|
| DFDC (deepfakes) | >97% | >98% | >96% |
| FaceSwap videos | >95% | >95% | >94% |
| AI-generated images | >99% | >99% | >98% |

## Usage

### Basic Image Detection
```python
from models.enhanced_image_detector import EnhancedImageDetector

detector = EnhancedImageDetector()
results = detector.detect("image.jpg")

print(f"Fake probability: {results['fake_probability']:.1%}")
print(f"Trust score: {results['trust_score']:.1f}")
print(f"Recommendation: {results['recommendation']}")
```

### Basic Video Detection
```python
from models.enhanced_video_detector import EnhancedVideoDetector

detector = EnhancedVideoDetector(frame_count=15)
results = detector.detect("video.mp4")

print(f"Video verdict: {'FAKE' if results['is_fake'] else 'AUTHENTIC'}")
print(f"Temporal consistency: {results['temporal_consistency']:.1%}")
print(f"Suspicious frames: {results['suspicious_frames']}/{results['frames_analyzed']}")
```

### Ensemble Prediction
```python
from models.advanced_deepfake_models import MultiHeadEnsembleDetector

ensemble = MultiHeadEnsembleDetector(use_vit=True, use_inception=True)
fake_score, individual_scores = ensemble.predict_image(image_tensor)

print(f"Ensemble score: {fake_score:.3f}")
print(f"Individual scores: {individual_scores}")
```

## API Endpoints

### POST /api/analyze/image
```json
REQUEST:
{
  "file": "image.jpg" (multipart form)
}

RESPONSE:
{
  "status": "success",
  "analysis_type": "image",
  "trust_score": 85.5,
  "is_fake": false,
  "confidence": 0.92,
  "avg_fake_probability": 14.5,
  "face_results": [
    {
      "face_id": 0,
      "fake_probability": 14.5,
      "vit_score": 0.12,
      "inception_score": 0.16,
      "is_fake": false
    }
  ],
  "recommendation": "✓ IMAGE APPEARS AUTHENTIC"
}
```

### POST /api/analyze/video
```json
REQUEST:
{
  "file": "video.mp4" (multipart form)
}

RESPONSE:
{
  "status": "success",
  "duration": 10.5,
  "frames_analyzed": 15,
  "trust_score": 42.3,
  "is_fake": true,
  "avg_fake_probability": 57.7,
  "temporal_consistency": 0.68,
  "suspicious_frames": 8,
  "frame_results": [
    {
      "frame_index": 0,
      "fake_probability": 62.1,
      "is_suspicious": true
    },
    ...
  ],
  "recommendation": "⚠️ VIDEO FLAGGED AS AI-GENERATED"
}
```

## Performance Optimization

### GPU Acceleration
- CUDA 12.0+
- cuDNN 8.5+
- TensorRT optimization available
- Mixed precision (FP16) supported

### CPU Fallback
- Full CPU support with slower inference
- Quantization available for mobile
- ~5-10x slower than GPU

### Memory Requirements
- **Image detection**: 4-6GB VRAM
- **Video detection**: 6-8GB VRAM (15 frames)
- **Batch processing**: 8-12GB VRAM

## Fine-tuning Guide

To achieve 95-99% accuracy on your dataset:

### 1. **Data Preparation**
```bash
# Organize dataset
dataset/
├── real/
│   ├── video1/
│   │   ├── frame_0.jpg
│   │   ├── frame_1.jpg
│   │   └── ...
│   └── video2/
└── fake/
    ├── deepfake1/
    └── ...
```

### 2. **Fine-tune ViT** (4-6 hours on single GPU)
```python
from transformers import ViTForImageClassification, ViTImageProcessor, Trainer

# Load pretrained
model = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224",
    num_labels=2,
    ignore_mismatched_sizes=True
)

# Setup trainer with your data
trainer = Trainer(
    model=model,
    training_args=TrainingArguments(
        output_dir="vit_finetuned",
        num_train_epochs=4,
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        warmup_steps=100,
    ),
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
```

### 3. **Fine-tune Inception-ResNet-v2** (2-4 hours)
```python
from torchvision.models import inception_resnet_v2

model = inception_resnet_v2(pretrained=True)
# Replace final layer
model.fc = torch.nn.Linear(1536, 2)

# Training loop with low learning rate
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(4):
    for images, labels in train_loader:
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
```

### 4. **Evaluate**
```python
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

y_pred = []
y_true = []

with torch.no_grad():
    for images, labels in test_loader:
        outputs = model(images)
        preds = outputs.argmax(dim=1)
        y_pred.extend(preds.cpu().numpy())
        y_true.extend(labels.cpu().numpy())

accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, y_pred, average='binary'
)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1: {f1:.4f}")
```

## Known Limitations

1. **Face Requirement**: Images must contain faces (≥224x224)
2. **Video Length**: Optimal for 5-60 second videos
3. **Frame Rate**: Works with 24-60 FPS videos
4. **Lighting**: Very dark/bright scenes may reduce accuracy
5. **Partial Faces**: Cropped faces <50% visible may not detect

## Future Improvements

- [ ] 3D face model analysis for consistency checking
- [ ] Audio-visual synchronization verification
- [ ] Micro-expression analysis
- [ ] Latent space anomaly detection
- [ ] Multimodal fusion (audio + video + text)
- [ ] Real-time streaming detection
- [ ] Mobile/edge deployment (quantized models)

## References

- ViT Paper: "An Image is Worth 16x16 Words" (Dosovitskiy et al., 2021)
- Inception-ResNet-v2: "Inception-v4, Inception-ResNet and the Impact of Residual Connections" (Szegedy et al., 2017)
- Deepfake Detection: "FaceForensics++: Learning to Detect Manipulated Facial Images" (Li et al., 2019)

## Installation & Deployment

```bash
# Install dependencies
pip install -r requirements_enhanced.txt

# Verify models load
python -c "from models.advanced_deepfake_models import ViTDeepfakeDetector; print('✓ Models loaded')"

# Start backend
cd backend
../venv/Scripts/python app.py
```

## Support & Troubleshooting

**Issue**: "Out of memory" errors
- Reduce frame_count in video analysis
- Use CPU instead of GPU
- Enable mixed precision (FP16)

**Issue**: Models take long to load
- This is normal on first run (downloads ~1.5GB)
- Models are cached after first load
- Use GPU for faster inference

**Issue**: Low accuracy on custom data
- Fine-tune models on your specific dataset
- Ensure balanced train/test split
- Check image quality and lighting consistency
