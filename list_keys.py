import torch

model_path = "backend/models/genconvit_ed_inference.pth"
checkpoint = torch.load(model_path, map_location="cpu")
state_dict = checkpoint.get('state_dict', checkpoint)

for key in state_dict.keys():
    if "layers" in key and "downsample" in key:
        print(key)
