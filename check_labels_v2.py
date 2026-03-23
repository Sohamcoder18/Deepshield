import os
import sys
import torch
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from models.multi_model_deepfake_service import get_multi_model_deepfake_service

logging.basicConfig(level=logging.ERROR) # Lower logging to reduce noise

def check_model_labels():
    print("🔍 Checking Model Label Mappings")
    
    try:
        service = get_multi_model_deepfake_service()
        print(f"Total models loaded: {len(service.models)}")
        
        for model_id in service.models.keys():
            model = service.models[model_id]
            print(f"MODEL_ID: {model_id}")
            if hasattr(model, 'config'):
                if hasattr(model.config, 'id2label'):
                    print(f"ID2LABEL: {model.config.id2label}")
                else:
                    print("ID2LABEL: MISSING")
            else:
                print("CONFIG: MISSING")
            print("-" * 20)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_model_labels()
