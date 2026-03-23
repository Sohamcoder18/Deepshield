# Image Detection Model Label Fix

## Issue Summary
The image detection model was showing **inverted/opposite behavior**:
- ❌ **Real images** → Classified as deepfakes (high fake probability)
- ❌ **AI images** → Classified as low risk (low fake probability)

This is **180° backwards from expected behavior**.

## Root Cause Analysis

### Model Information
- **Model Name:** `umm-maybe/AI-image-detector` (from Hugging Face)
- **Type:** Swin Vision Transformer (Image Classification)
- **Output Classes:** 2 classes
  - Index 0 = **"artificial"** (AI-generated content)
  - Index 1 = **"human"** (Real human content)

### The Bug
In the file `backend/models/multi_model_deepfake_service.py`, method `_predict_vit()`:

**INCORRECT CODE:**
```python
# ViT: label 0=real, 1=fake (may vary)
if len(probs) >= 2:
    return {
        "real": round(probs[0], 3),    # ❌ probs[0] is "artificial"!
        "fake": round(probs[1], 3)     # ❌ probs[1] is "human"!
    }
```

The comment claimed labels were 0=real and 1=fake, but the actual model has:
- probs[0] = probability of "artificial" (AI-generated)
- probs[1] = probability of "human" (real)

### Why This Breaks Detection
Given a **REAL image** (human generated):
1. Model correctly outputs: probs[0]=0.05 (low artificial), probs[1]=0.95 (high human)
2. Code incorrectly maps: "real"=0.05, "fake"=0.95
3. **Result:** fake_probability = 0.95 → Flagged as DEEPFAKE ❌

Given an **AI-GENERATED image**:
1. Model correctly outputs: probs[0]=0.95 (high artificial), probs[1]=0.05 (low human)  
2. Code incorrectly maps: "real"=0.95, "fake"=0.05
3. **Result:** fake_probability = 0.05 → Marked as LOW RISK ❌

## Solution

### Files Changed
- **File:** `backend/models/multi_model_deepfake_service.py`
- **Method:** `_predict_vit()` (lines 325-357)

### The Fix
Swap the label mapping to correctly interpret the model's output:

```python
def _predict_vit(self, image, model, processor):
    """Get predictions from ViT model"""
    try:
        inputs = processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
        
        if len(probs.shape) == 0:
            probs = probs.unsqueeze(0)
        
        probs = probs.tolist()
        
        if not isinstance(probs, list):
            probs = [probs]
        
        # FIX: AI-image-detector model has INVERTED labels!
        # Index 0 = "artificial" (AI-generated content)
        # Index 1 = "human" (Real human content)
        # Previous code incorrectly assumed Index 0 = real!
        if len(probs) >= 2:
            return {
                "real": round(probs[1], 3),      # Index 1 = "human" = REAL
                "fake": round(probs[0], 3)       # Index 0 = "artificial" = AI/FAKE
            }
        else:
            fake_prob = round(probs[0], 3)
            return {
                "fake": fake_prob,
                "real": round(1 - fake_prob, 3)
            }
    except Exception as e:
        logger.error(f"Error in ViT prediction: {str(e)}")
        return None
```

### Key Changes
1. **Changed:** `"real": round(probs[0], 3)` → `"real": round(probs[1], 3)`
2. **Changed:** `"fake": round(probs[1], 3)` → `"fake": round(probs[0], 3)`
3. **Added:** Detailed comments explaining the label mapping

## Result After Fix

### Real Images
- Model: probs[0] ≈ 0.0-0.3 (low artificial), probs[1] ≈ 0.7-1.0 (high human)
- Detection: "fake" ≈ 0.05-0.30 → **is_fake = False** ✅
- Trust Score: **70-95%** ✅

### AI-Generated Images  
- Model: probs[0] ≈ 0.7-1.0 (high artificial), probs[1] ≈ 0.0-0.3 (low human)
- Detection: "fake" ≈ 0.70-0.95 → **is_fake = True** ✅
- Trust Score: **5-30%** ✅

## Testing
The fix has been verified to work correctly with the actual model predictions.

## Related Configuration Notes
- Model is enabled in `MultiModelDeepfakeDetectionService` with weight=1.0
- Uses threshold of 0.40 for is_fake designation
- Trust score calculated as: `(1 - fake_probability) * 100`
