import torch
import re
from backend.models.genconvit.genconvit_ed import GenConViTED

config = {
    'model': {
        'backbone': 'convnext_tiny',
        'embedder': 'swin_tiny_patch4_window7_224',
        'latent_dims': 12544
    },
    'img_size': 224
}

device = torch.device("cpu")
model = GenConViTED(config, pretrained=False).to(device)

model_path = "backend/models/genconvit_ed_inference.pth"
checkpoint = torch.load(model_path, map_location=device)
state_dict = checkpoint.get('state_dict', checkpoint)

def _remap_swin_downsample_key(key: str) -> str:
    m = re.match(r'^(.*\.layers\.)(\d+)(\.downsample\..+)$', key)
    if m:
        return f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}"
    return key

remapped_state_dict = {}
remapped_keys = 0
for k, v in state_dict.items():
    new_k = _remap_swin_downsample_key(k)
    if new_k != k:
        remapped_keys += 1
    remapped_state_dict[new_k] = v

print(f"Remapped {remapped_keys} keys")

try:
    result = model.load_state_dict(remapped_state_dict, strict=False)
    print(f"✅ Loaded successfully!")
    if result.missing_keys:
        print(f"Missing keys ({len(result.missing_keys)}): {result.missing_keys[:5]}...")
    if result.unexpected_keys:
        print(f"Unexpected keys ({len(result.unexpected_keys)}): {result.unexpected_keys[:5]}...")
    print("NO SIZE MISMATCH ERRORS!")
except RuntimeError as e:
    print(f"❌ Still has RuntimeError: {e}")
