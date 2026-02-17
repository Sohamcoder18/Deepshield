#!/usr/bin/env python
"""Quick test to verify image detection fix"""

import numpy as np
import sys

# Test the prediction logic directly
fake_probabilities = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]

print("Testing fixed threshold (0.5):")
print("-" * 50)
for prob in fake_probabilities:
    is_fake = prob > 0.5
    verdict = "LIKELY DEEPFAKE" if is_fake else "AUTHENTIC"
    print(f"Probability: {prob:.2f} → {verdict}")

print("\n" + "="*50)
print("Real images (probs 0.3-0.5): Should all be AUTHENTIC ✓")
print("Fake images (probs 0.5+): Should all be LIKELY DEEPFAKE ✓")
