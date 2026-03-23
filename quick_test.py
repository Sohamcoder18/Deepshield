import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import numpy as np

# Load model
print("Loading AI detector model...")
model = AutoModelForImageClassification.from_pretrained("umm-maybe/AI-image-detector")
processor = AutoImageProcessor.from_pretrained("umm-maybe/AI-image-detector")
model.eval()

print(f"Model ID to label: {model.config.id2label}")
print()

# Test with white image (should be AI-like - smooth, uniform)
white = Image.new('RGB', (224, 224), color=(255, 255, 255))
with torch.no_grad():
    inp = processor(white, return_tensors="pt")
    out = model(**inp)
    prob = torch.nn.functional.softmax(out.logits, dim=1)[0].numpy()

print(f"WHITE IMAGE (AI-like):")
print(f"  probs[0]={prob[0]:.4f}")
print(f"  probs[1]={prob[1]:.4f}")
print(f"  Winner: probs[{np.argmax(prob)}]")
print()

# What this means:
if prob[0] > prob[1]:
    print("-> Model thinks it's MORE artificial at index 0")
    print("-> Standard config mapping is CORRECT")
else:
    print("-> Model thinks it's MORE artificial at index 1")
    print("-> Checkpoint is INVERTED from config!")
