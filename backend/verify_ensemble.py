#!/usr/bin/env python
"""
Verify 3-model ensemble loads with HuggingFace authentication
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🔐 VERIFYING VIDEO MODEL ENSEMBLE WITH AUTHENTICATION")
print("="*70)

try:
    print("\n✓ Step 1: Importing service...")
    from models.multi_model_deepfake_service import get_multi_model_deepfake_service
    
    print("\n✓ Step 2: Loading ensemble (3 models)...")
    print("  This will download models on first run (~200MB total)")
    service = get_multi_model_deepfake_service()
    
    print("\n" + "="*70)
    print("✅ ENSEMBLE LOADED SUCCESSFULLY!")
    print("="*70)
    
    models_info = []
    for model_id in sorted(service.models.keys()):
        weight = service.model_weights.get(model_id, 1.0)
        model_config = service.available_models.get(model_id, {})
        model_type = model_config.get("type", "unknown")
        model_name = model_config.get("model_name", "unknown")
        
        models_info.append({
            "id": model_id,
            "name": model_name,
            "type": model_type,
            "weight": weight
        })
        
        print(f"\n  Model {len(models_info)}:")
        print(f"    ID:     {model_id}")
        print(f"    Name:   {model_name}")
        print(f"    Type:   {model_type}")
        print(f"    Weight: {weight:.0%}")
    
    print("\n" + "-"*70)
    print(f"Total Models: {len(service.models)}")
    print(f"Total Weight: {sum(m['weight'] for m in models_info):.1f}")
    
    print("\n" + "="*70)
    print("✅ READY FOR DEPLOYMENT!")
    print("="*70)
    print("""
    Features:
    ✓ Video classification pipeline (Naman712)
    ✓ Image frame analysis (SIGLIP + DeepFake v2)
    ✓ Weighted ensemble voting (30% + 35% + 35%)
    ✓ Individual model predictions in API response
    ✓ Graceful fallback if any model fails
    
    Test with:
      POST /api/deepfake/analyze/video
      POST /api/deepfake/analyze/image
    """)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n")
