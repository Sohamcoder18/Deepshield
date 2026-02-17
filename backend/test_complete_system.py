#!/usr/bin/env python3
"""
Complete Deepfake Detection System Test
Tests image, video, and audio detection with accuracy metrics
"""

import os
import sys
import json
import torch
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image
from scipy.io import wavfile

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print(" COMPLETE DEEPFAKE DETECTION SYSTEM TEST")
print(" Image + Video + Audio Detection with Accuracy Metrics")
print("=" * 80)

# ============================================================================
# PART 1: Initialize Service
# ============================================================================
print("\n[1/8] Initializing Multi-Model Ensemble Service...")
try:
    from models.multi_model_deepfake_service import MultiModelDeepfakeDetectionService
    
    service = MultiModelDeepfakeDetectionService()
    print(f"✅ Service initialized")
    print(f"   Models loaded: {list(service.models.keys())}")
    print(f"   Model weights: {service.model_weights}")
except Exception as e:
    print(f"❌ Failed to initialize service: {e}")
    sys.exit(1)

# ============================================================================
# PART 2: Create Test Data Directory
# ============================================================================
print("\n[2/8] Creating test data directory...")
test_dir = Path("test_complete_system")
test_dir.mkdir(exist_ok=True)

image_dir = test_dir / "images"
video_dir = test_dir / "videos"
audio_dir = test_dir / "audio"

image_dir.mkdir(exist_ok=True)
video_dir.mkdir(exist_ok=True)
audio_dir.mkdir(exist_ok=True)

print(f"✅ Test directories created")

# ============================================================================
# PART 3: Generate Test Images
# ============================================================================
print("\n[3/8] Generating Test Images...")

test_images = {}

# Real image (simple gradient)
real_img = np.zeros((256, 256, 3), dtype=np.uint8)
for i in range(256):
    real_img[i, :] = [i, i, i]  # Grayscale gradient
Image.fromarray(real_img).save(image_dir / "test_real_image.png")
test_images["real_gradient"] = ("test_real_image.png", True)  # True = is real
print("✅ Created real image sample (gradient)")

# Fake image (noise - should differ)
fake_img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
Image.fromarray(fake_img).save(image_dir / "test_fake_image.png")
test_images["fake_noise"] = ("test_fake_image.png", False)  # False = is fake
print("✅ Created fake image sample (noise)")

# Natural image (checkerboard)
natural_img = np.ones((256, 256, 3), dtype=np.uint8) * 128
for i in range(0, 256, 32):
    for j in range(0, 256, 32):
        if (i // 32 + j // 32) % 2 == 0:
            natural_img[i:i+32, j:j+32] = 200
Image.fromarray(natural_img).save(image_dir / "test_pattern_image.png")
test_images["pattern"] = ("test_pattern_image.png", True)
print("✅ Created natural image sample (pattern)")

# ============================================================================
# PART 4: Generate Test Videos
# ============================================================================
print("\n[4/8] Generating Test Videos...")

test_videos = {}

# Create simple video file (8 frames, 256x256)
def create_test_video(filename, is_real=True, fps=8):
    """Create a simple test video"""
    filepath = video_dir / filename
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (256, 256))
    
    for frame_idx in range(8):
        if is_real:
            # Real: natural-looking frames with texture and variation
            frame = np.zeros((256, 256, 3), dtype=np.uint8)
            
            # Create a pattern with multiple colors and gradients
            x = np.linspace(0, 1, 256)
            y = np.linspace(0, 1, 256)
            X, Y = np.meshgrid(x, y)
            
            # Create color channels with smooth gradients
            r = (np.sin(X * 3 + frame_idx * 0.3) * 128 + 128).astype(np.uint8)
            g = (np.cos(Y * 3 + frame_idx * 0.3) * 128 + 128).astype(np.uint8)
            b = ((X + Y) * 128).astype(np.uint8)
            
            frame[:, :, 0] = r
            frame[:, :, 1] = g
            frame[:, :, 2] = b
            
            # Add some texture to make it look more real
            noise = np.random.randint(-10, 10, (256, 256, 3), dtype=np.int16)
            frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        else:
            # Fake: random noise frames (clearly artificial)
            frame = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
        
        out.write(frame)
    
    out.release()
    return filepath

real_video = create_test_video("test_real_video.mp4", is_real=True)
test_videos["real_video"] = ("test_real_video.mp4", True)
print("✅ Created real video sample")

fake_video = create_test_video("test_fake_video.mp4", is_real=False)
test_videos["fake_video"] = ("test_fake_video.mp4", False)
print("✅ Created fake video sample")

# ============================================================================
# PART 5: Generate Test Audio
# ============================================================================
print("\n[5/8] Generating Test Audio Files...")

test_audio = {}

# Real audio: sine wave (natural frequency)
freq = 440  # A4 note
sample_rate = 16000
duration = 4  # seconds
t = np.linspace(0, duration, sample_rate * duration)
sine_wave = np.sin(2 * np.pi * freq * t) * 0.3

# Convert to int16 for WAV file
sine_wave_int16 = np.int16(sine_wave * 32767)
sine_path = audio_dir / "sine_wave.wav"
wavfile.write(str(sine_path), sample_rate, sine_wave_int16)
test_audio["sine_wave"] = ("sine_wave.wav", True)  # True = likely real
print("✅ Created sine wave audio (likely real)")

# Fake audio: white noise
white_noise = np.random.randn(sample_rate * duration) * 0.1
white_noise_int16 = np.int16(white_noise * 32767)
noise_path = audio_dir / "white_noise.wav"
wavfile.write(str(noise_path), sample_rate, white_noise_int16)
test_audio["white_noise"] = ("white_noise.wav", False)  # False = likely fake
print("✅ Created white noise audio (likely fake)")

# Natural audio: modulated signal (simulating speech pattern)
modulation = np.sin(2 * np.pi * 3 * t)  # 3 Hz modulation
modulated = white_noise * (0.5 + 0.5 * modulation)
modulated_int16 = np.int16(modulated * 32767)
modulated_path = audio_dir / "modulated.wav"
wavfile.write(str(modulated_path), sample_rate, modulated_int16)
test_audio["modulated"] = ("modulated.wav", True)  # True = possibly real
print("✅ Created modulated audio (possibly real)")

# ============================================================================
# PART 6: Test Image Detection
# ============================================================================
print("\n[6/8] Testing Image Detection...")
print("-" * 80)

image_results = {}
image_correct = 0

for sample_name, (filename, is_real) in test_images.items():
    filepath = image_dir / filename
    
    try:
        # Load image
        image = Image.open(filepath).convert('RGB')
        
        # Classify
        result = service.process_file(str(filepath), "image")
        
        fake_conf = result.get("fake_confidence", 0)
        is_fake_pred = result.get("is_fake", False)
        
        # Check correctness
        predicted_real = not is_fake_pred  # is_fake=False means predicted real
        actual_real = is_real
        correct = predicted_real == actual_real
        
        if correct:
            image_correct += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
        
        image_results[sample_name] = {
            "actual": "real" if is_real else "fake",
            "predicted": "real" if predicted_real else "fake",
            "fake_confidence": fake_conf,
            "correct": correct
        }
        
        print(f"{sample_name:20} {status:15} | Pred: {'REAL' if predicted_real else 'FAKE':4} | "
              f"Conf: {fake_conf:.2%} | Models: {result.get('models_used', 1)}")
    
    except Exception as e:
        print(f"{sample_name:20} ❌ ERROR: {str(e)[:40]}")
        image_results[sample_name] = {"error": str(e)}

image_accuracy = (image_correct / len(test_images)) * 100
print(f"\nImage Accuracy: {image_correct}/{len(test_images)} = {image_accuracy:.1f}%")

# ============================================================================
# PART 7: Test Video Detection
# ============================================================================
print("\n[7/8] Testing Video Detection...")
print("-" * 80)

video_results = {}
video_correct = 0

for sample_name, (filename, is_real) in test_videos.items():
    filepath = video_dir / filename
    
    try:
        # Classify
        result = service.process_file(str(filepath), "video")
        
        fake_conf = result.get("fake_confidence", 0)
        is_fake_pred = result.get("is_fake", False)
        
        # Check correctness
        predicted_real = not is_fake_pred
        actual_real = is_real
        correct = predicted_real == actual_real
        
        if correct:
            video_correct += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
        
        video_results[sample_name] = {
            "actual": "real" if is_real else "fake",
            "predicted": "real" if predicted_real else "fake",
            "fake_confidence": fake_conf,
            "correct": correct,
            "models_used": result.get('models_used', 0)
        }
        
        print(f"{sample_name:20} {status:15} | Pred: {'REAL' if predicted_real else 'FAKE':4} | "
              f"Conf: {fake_conf:.2%} | Models: {result.get('models_used', 1)}")
    
    except Exception as e:
        print(f"{sample_name:20} ❌ ERROR: {str(e)[:40]}")
        video_results[sample_name] = {"error": str(e)}

video_accuracy = (video_correct / len(test_videos)) * 100
print(f"\nVideo Accuracy: {video_correct}/{len(test_videos)} = {video_accuracy:.1f}%")

# ============================================================================
# PART 8: Test Audio Detection
# ============================================================================
print("\n[8/8] Testing Audio Detection...")
print("-" * 80)

audio_results = {}
audio_correct = 0

for sample_name, (filename, is_real) in test_audio.items():
    filepath = audio_dir / filename
    
    try:
        # Classify
        result = service.process_file(str(filepath), "audio")
        
        fake_conf = result.get("fake_confidence", 0)
        is_fake_pred = result.get("is_fake", False)
        
        # Check correctness
        predicted_real = not is_fake_pred
        actual_real = is_real
        correct = predicted_real == actual_real
        
        if correct:
            audio_correct += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
        
        audio_results[sample_name] = {
            "actual": "real" if is_real else "fake",
            "predicted": "real" if predicted_real else "fake",
            "fake_confidence": fake_conf,
            "correct": correct
        }
        
        print(f"{sample_name:20} {status:15} | Pred: {'REAL' if predicted_real else 'FAKE':4} | "
              f"Conf: {fake_conf:.2%}")
    
    except Exception as e:
        print(f"{sample_name:20} ❌ ERROR: {str(e)[:40]}")
        audio_results[sample_name] = {"error": str(e)}

audio_accuracy = (audio_correct / len(test_audio)) * 100
print(f"\nAudio Accuracy: {audio_correct}/{len(test_audio)} = {audio_accuracy:.1f}%")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SYSTEM ACCURACY SUMMARY")
print("=" * 80)

total_samples = len(test_images) + len(test_videos) + len(test_audio)
total_correct = image_correct + video_correct + audio_correct

print(f"\n📊 BREAKDOWN BY MODALITY:")
print(f"   Image Detection:  {image_correct:2d}/{len(test_images):2d} = {image_accuracy:6.1f}%")
print(f"   Video Detection:  {video_correct:2d}/{len(test_videos):2d} = {video_accuracy:6.1f}%")
print(f"   Audio Detection:  {audio_correct:2d}/{len(test_audio):2d} = {audio_accuracy:6.1f}%")
print(f"   {'─' * 40}")
print(f"   TOTAL ACCURACY:   {total_correct:2d}/{total_samples:2d} = {(total_correct/total_samples)*100:6.1f}%")

print(f"\n🎯 ENSEMBLE INFORMATION:")
print(f"   Active Models: {len(service.models)}")
print(f"   Models: {', '.join(service.models.keys())}")
print(f"   Model Weights: {service.model_weights}")

print(f"\n📈 DETAILED RESULTS:")
print(f"\n   IMAGE RESULTS:")
for name, result in image_results.items():
    if "error" not in result:
        print(f"     {name:20} | Actual: {result['actual']:4} | Predicted: {result['predicted']:4} | {result['correct']}")

print(f"\n   VIDEO RESULTS:")
for name, result in video_results.items():
    if "error" not in result:
        print(f"     {name:20} | Actual: {result['actual']:4} | Predicted: {result['predicted']:4} | {result['correct']}")

print(f"\n   AUDIO RESULTS:")
for name, result in audio_results.items():
    if "error" not in result:
        print(f"     {name:20} | Actual: {result['actual']:4} | Predicted: {result['predicted']:4} | {result['correct']}")

# ============================================================================
# Save Results to JSON
# ============================================================================
results_file = Path("test_complete_system_results.json")
full_results = {
    "timestamp": datetime.now().isoformat(),
    "overall_accuracy": round((total_correct / total_samples) * 100, 2),
    "summary": {
        "image": {
            "correct": image_correct,
            "total": len(test_images),
            "accuracy": round(image_accuracy, 2)
        },
        "video": {
            "correct": video_correct,
            "total": len(test_videos),
            "accuracy": round(video_accuracy, 2)
        },
        "audio": {
            "correct": audio_correct,
            "total": len(test_audio),
            "accuracy": round(audio_accuracy, 2)
        }
    },
    "ensemble": {
        "models": list(service.models.keys()),
        "weights": service.model_weights,
        "version": service.model_version
    },
    "detailed_results": {
        "images": image_results,
        "videos": video_results,
        "audio": audio_results
    }
}

with open(results_file, 'w') as f:
    json.dump(full_results, f, indent=2)

print(f"\n💾 Results saved to: {results_file.resolve()}")

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "=" * 80)
print("🎉 TEST COMPLETE")
print("=" * 80)
print(f"""
✅ System Status:
   • Image Detection:  {image_correct}/{len(test_images)} tests passed ({image_accuracy:.1f}%)
   • Video Detection:  {video_correct}/{len(test_videos)} tests passed ({video_accuracy:.1f}%)
   • Audio Detection:  {audio_correct}/{len(test_audio)} tests passed ({audio_accuracy:.1f}%)
   
🎯 OVERALL SYSTEM ACCURACY: {(total_correct/total_samples)*100:.1f}%

📊 Ensemble Configuration:
   • Total Models: {len(service.models)}
   • Models Used: {', '.join(service.models.keys())}
   • Version: {service.model_version}

🔍 Test Details:
   • Test samples created: {total_samples}
   • Test directory: {test_dir.resolve()}
   • Results file: {results_file.resolve()}

Next Steps:
1. Review test results in {results_file}
2. Test with real deepfake/authentic media
3. Fine-tune model weights if needed
4. Deploy to production
""")

print("=" * 80)
