import torch
import timm
from backend.models.genconvit.genconvit_ed import GenConViTED

config = {
    'model': {
        'backbone': 'convnext_tiny',
        'embedder': 'swin_tiny_patch4_window7_224',
        'latent_dims': 12544
    },
    'img_size': 224
}

try:
    model = GenConViTED(config, pretrained=False)
    print("Model instantiated successfully")
    
    print(f"Embedder layers: {len(model.embedder.layers)}")
    if hasattr(model.embedder, 'depths'):
        print(f"Embedder depths: {model.embedder.depths}")
    
    # Check backbone shapes
    with open("d:\\hackethon\\shapes_output.txt", "w") as f:
        # Check backbone shapes
        f.write("Backbone shapes:\n")
        for name, param in model.backbone.named_parameters():
            if "downsample" in name:
                f.write(f"{name}: {param.shape}\n")
                
        # Check embedder shapes
        f.write("\nEmbedder shapes:\n")
        for name, param in model.embedder.named_parameters():
            if "downsample" in name:
                f.write(f"{name}: {param.shape}\n")
    print("Shapes written to shapes_output.txt")
            
except Exception as e:
    print(f"Error: {e}")
