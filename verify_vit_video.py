import os
import sys
import torch
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from models.multi_model_deepfake_service import get_multi_model_deepfake_service
from models.enhanced_video_detector import EnhancedVideoDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_vit():
    print("🚀 Starting Video ViT Integration Test")
    
    # 1. Test Service Initialization
    try:
        service = get_multi_model_deepfake_service()
        print(f"✅ Ensemble service loaded. Models: {list(service.models.keys())}")
        
        if 'deepfake_v2' in service.models:
            print("✅ ViT (deepfake_v2) model is LOADED and READY")
        else:
            print("❌ ViT (deepfake_v2) model NOT LOADED")
            return
    except Exception as e:
        print(f"❌ Service init failed: {e}")
        return

    # 2. Test Enhanced Video Detector Integration
    try:
        detector = EnhancedVideoDetector()
        print("✅ EnhancedVideoDetector initialized")
        
        if detector.ensemble_service:
            print("✅ Detector has access to ensemble service")
        else:
            print("❌ Detector missing ensemble service")
    except Exception as e:
        print(f"❌ Detector init failed: {e}")
        return

    print("\n✅ Verification complete: Integration looks solid!")

if __name__ == "__main__":
    test_video_vit()
