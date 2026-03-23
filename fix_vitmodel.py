#!/usr/bin/env python
"""Fix the corrupted _load_vit_model function"""

with open('backend/models/multi_model_deepfake_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the corrupted _load_vit_model section
broken_start = 'def _load_vit_model(self, model_id, config):'
broken_end = 'def _load_video_classifier(self, model_id, config):'

# Find the positions
start_pos = content.find(broken_start)
end_pos = content.find(broken_end)

if start_pos != -1 and end_pos != -1:
    # Get everything before _load_vit_model and from _load_video_classifier onwards
    before = content[:start_pos]
    after = content[end_pos:]
    
    # Create the correct _load_vit_model function
    correct_function = '''def _load_vit_model(self, model_id, config):
        """Load generic ViT-based image classification model"""
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        try:
            model = AutoModelForImageClassification.from_pretrained(config["model_name"])
            processor = AutoImageProcessor.from_pretrained(config["model_name"])
            
            model.to(self.device)
            model.eval()
            
            self.models[model_id] = model
            self.processors[model_id] = processor
            logger.info(f"✅ ViT model {model_id} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading ViT model {model_id}: {str(e)}")
            raise
    
    '''
    
    # Reconstruct the file
    new_content = before + correct_function + after
    
    with open('backend/models/multi_model_deepfake_service.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed _load_vit_model function")
else:
    print("❌ Could not find function markers")
