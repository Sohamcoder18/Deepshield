import torch
import os
from backend.models.genconvit.genconvit_ed import GenConViTED

config = {
    'model': {
        'backbone': 'convnext_tiny',
        'embedder': 'swin_tiny_patch4_window7_224',
        'latent_dims': 12544
    },
    'img_size': 224
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = GenConViTED(config, pretrained=False).to(device)

model_path = "backend/models/genconvit_ed_inference.pth"
if not os.path.exists(model_path):
    print(f"Error: {model_path} not found")
else:
    checkpoint = torch.load(model_path, map_location=device)
    state_dict = checkpoint.get('state_dict', checkpoint)
    
    try:
        model.load_state_dict(state_dict, strict=True)
        print("Model loaded successfully!")
    except RuntimeError as e:
        print("Mismatches found:")
        print(e)
