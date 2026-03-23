import os
import sys
import torch
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from models.multi_model_deepfake_service import get_multi_model_deepfake_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_model_labels():
    print("🔍 Checking Model Label Mappings")
    
    try:
        service = get_multi_model_deepfake_service()
        
        for model_id, model in service.models.items():
            print(f"\n--- Model: {model_id} ---")
            if hasattr(model, 'config'):
                if hasattr(model.config, 'id2label'):
                    print(f"id2label: {model.config.id2label}")
                else:
                    print("No id2label in config")
            else:
                print("No config attribute")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_model_labels()
