import torch

model_path = "backend/models/genconvit_ed_inference.pth"
checkpoint = torch.load(model_path, map_location="cpu")
state_dict = checkpoint.get('state_dict', checkpoint)

layers = sorted(list(set([k.split('.')[2] for k in state_dict.keys() if 'embedder.layers' in k])))
print(f"Embedder layers in checkpoint: {layers}")

for i in layers:
    has_downsample = any(f'layers.{i}.downsample' in k for k in state_dict.keys())
    print(f"Layer {i} has downsample: {has_downsample}")
