"""
Check actual label configuration of pretrained models
"""
from transformers import AutoModelForImageClassification, AutoConfig

models_to_check = [
    "umm-maybe/AI-image-detector",
    "prithivMLmods/Deep-Fake-Detector-v2-Model",
]

for model_name in models_to_check:
    print(f"\n{'='*60}")
    print(f"Model: {model_name}")
    print('='*60)
    
    try:
        config = AutoConfig.from_pretrained(model_name)
        model = AutoModelForImageClassification.from_pretrained(model_name)
        
        print(f"\nId2Label mapping:")
        if hasattr(config, 'id2label'):
            for idx, label in config.id2label.items():
                print(f"  Index {idx} -> '{label}'")
        else:
            print("  No id2label in config")
        
        print(f"\nLabel2Id mapping:")
        if hasattr(config, 'label2id'):
            for label, idx in config.label2id.items():
                print(f"  '{label}' -> Index {idx}")
        else:
            print("  No label2id in config")
        
        print(f"\nModel num_labels: {config.num_labels}")
        
    except Exception as e:
        print(f"Error loading {model_name}: {str(e)}")

print(f"\n{'='*60}")
print("Analysis:")
print('='*60)
print("""
If ai_detector has id2label like:
  Index 0 -> 'real' or 'human'
  Index 1 -> 'artificial' or 'fake'

Then output[0] = real probability, output[1] = fake probability - CORRECT MAPPING

If it's reversed:
  Index 0 -> 'artificial' or 'fake'  
  Index 1 -> 'real' or 'human'

Then output[0] = fake probability, output[1] = real probability - NEEDS INVERSION
""")
