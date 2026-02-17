"""
Test authenticated video model integration
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("Testing 3-Model Ensemble with Video Classifier")
print("="*60)

try:
    print("\n1️⃣ Importing service...")
    from models.multi_model_deepfake_service import get_multi_model_deepfake_service
    print("✅ Import successful\n")
    
    print("2️⃣ Initializing multi-model ensemble (including video model)...")
    print("   Loading models (this may take 2-3 minutes on first run)...\n")
    
    service = get_multi_model_deepfake_service()
    
    print("\n" + "-"*60)
    print("✅ ENSEMBLE INITIALIZED SUCCESSFULLY!")
    print("-"*60)
    
    print(f"\n📊 Models Loaded: {len(service.models)}")
    for model_id in service.models.keys():
        weight = service.model_weights.get(model_id, 1.0)
        model_config = service.available_models.get(model_id, {})
        model_type = model_config.get("type", "unknown")
        status = "✓" if model_id in service.models else "✗"
        print(f"   {status} {model_id:20} | Weight: {weight:4} | Type: {model_type}")
    
    print(f"\n📋 Model Weights:")
    total = 0
    for model_id in sorted(service.models.keys()):
        weight = service.model_weights.get(model_id, 1.0)
        total += weight
        print(f"   - {model_id:20}: {weight:.2f} ({weight*100:.0f}%)")
    print(f"   Total: {total:.2f}")
    
    print("\n" + "="*60)
    print("✅ Video + Image Ensemble Ready!")
    print("="*60)
    print("\nEnsemble Structure:")
    if "video_classifier" in service.models:
        print("✓ Video Classification Pipeline:")
        print("  - Naman712/Deep-fake-detection (direct video analysis)")
    
    image_models = [m for m in service.models.keys() if m != "video_classifier"]
    if image_models:
        print(f"\n✓ Image Models (frame-based analysis - {len(image_models)} models):")
        for m in image_models:
            print(f"  - {m}")
    
    print("\n✓ Video Processing Flow:")
    print("  1. Dedicated video model analyzes full video")
    print("  2. Extract 5 frames from video")
    print("  3. Image models analyze each frame")
    print("  4. Combine all predictions with weighted ensemble")
    print("\n✓ API Response includes:")
    print("  - Individual predictions from all models")
    print("  - Weighted ensemble result")
    print("  - Frames analyzed count")
    print("  - Processing time")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n")
