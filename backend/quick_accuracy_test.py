#!/usr/bin/env python3
"""
Quick System Accuracy Test with Model-by-Model Breakdown
Fast testing with detailed confidence metrics
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 90)
print(" QUICK DEEPFAKE DETECTION ACCURACY TEST")
print(" Shows per-model predictions and confidence metrics")
print("=" * 90)

# Initialize service
print("\n[1/3] Initializing Service...")
try:
    from models.multi_model_deepfake_service import MultiModelDeepfakeDetectionService
    service = MultiModelDeepfakeDetectionService()
    print(f"✅ Service ready with {len(service.models)} models")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test with existing test files
print("\n[2/3] Testing with Available Test Files...")
print("-" * 90)

test_dir = Path("test_complete_system")
if not test_dir.exists():
    print("⚠️  Test files not found. Run: python test_complete_system.py first")
    print("   Or use: python test_audio_detection.py")
    sys.exit(0)

# Collect results
results_summary = {
    "images": [],
    "videos": [],
    "audio": []
}

# Test images
image_dir = test_dir / "images"
if image_dir.exists():
    print("\n📷 IMAGE DETECTION:")
    print("-" * 90)
    for img_file in sorted(image_dir.glob("*.png")):
        try:
            result = service.process_file(str(img_file), "image")
            fake_conf = result.get("fake_confidence", 0)
            is_fake = "FAKE" if result.get("is_fake") else "REAL"
            
            print(f"{img_file.name:30} | {is_fake:4} | Fake confidence: {fake_conf:6.2%} | Models: {result.get('models_used', 1)}")
            
            results_summary["images"].append({
                "file": img_file.name,
                "prediction": is_fake,
                "confidence": fake_conf
            })
        except Exception as e:
            print(f"{img_file.name:30} | ❌ Error: {str(e)[:50]}")

# Test videos
video_dir = test_dir / "videos"
if video_dir.exists():
    print("\n🎬 VIDEO DETECTION:")
    print("-" * 90)
    for vid_file in sorted(video_dir.glob("*.mp4")):
        try:
            result = service.process_file(str(vid_file), "video")
            fake_conf = result.get("fake_confidence", 0)
            is_fake = "FAKE" if result.get("is_fake") else "REAL"
            
            print(f"{vid_file.name:30} | {is_fake:4} | Fake confidence: {fake_conf:6.2%} | Models: {result.get('models_used', 1)}")
            
            results_summary["videos"].append({
                "file": vid_file.name,
                "prediction": is_fake,
                "confidence": fake_conf
            })
        except Exception as e:
            print(f"{vid_file.name:30} | ❌ Error: {str(e)[:50]}")

# Test audio
audio_dir = test_dir / "audio"
if audio_dir.exists():
    print("\n🔊 AUDIO DETECTION:")
    print("-" * 90)
    for aud_file in sorted(audio_dir.glob("*.wav")):
        try:
            result = service.process_file(str(aud_file), "audio")
            fake_conf = result.get("fake_confidence", 0)
            is_fake = "FAKE" if result.get("is_fake") else "REAL"
            
            print(f"{aud_file.name:30} | {is_fake:4} | Fake confidence: {fake_conf:6.2%}")
            
            results_summary["audio"].append({
                "file": aud_file.name,
                "prediction": is_fake,
                "confidence": fake_conf
            })
        except Exception as e:
            print(f"{aud_file.name:30} | ❌ Error: {str(e)[:50]}")

# Print summary
print("\n[3/3] System Summary...")
print("=" * 90)

total_tests = len(results_summary["images"]) + len(results_summary["videos"]) + len(results_summary["audio"])

if total_tests > 0:
    print(f"\n📊 CONFIDENCE STATISTICS:")
    
    for modality, results in results_summary.items():
        if results:
            confidences = [r["confidence"] for r in results]
            avg_conf = sum(confidences) / len(confidences)
            min_conf = min(confidences)
            max_conf = max(confidences)
            
            fake_count = sum(1 for r in results if r["prediction"] == "FAKE")
            real_count = sum(1 for r in results if r["prediction"] == "REAL")
            
            print(f"\n   {modality.upper()}:")
            print(f"      Tests: {len(results)}")
            print(f"      Fake detected: {fake_count}, Real detected: {real_count}")
            print(f"      Avg Confidence: {avg_conf:.1%}")
            print(f"      Min Confidence: {min_conf:.1%}")
            print(f"      Max Confidence: {max_conf:.1%}")

print(f"\n🎯 ENSEMBLE CONFIGURATION:")
print(f"   Active Models: {len(service.models)}")
print(f"   {', '.join(service.models.keys())}")
print(f"\n   Model Weights:")
for model_id, weight in service.model_weights.items():
    print(f"      {model_id:20} : {weight:5.0%}")

print(f"\n   Version: {service.model_version}")

# Save summary
summary_file = Path("quick_test_results.json")
with open(summary_file, 'w') as f:
    json.dump(results_summary, f, indent=2)

print(f"\n💾 Results saved to: {summary_file}")
print("\n" + "=" * 90)
