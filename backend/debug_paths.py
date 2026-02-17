#!/usr/bin/env python
"""Debug script to check dataset path construction"""

from pathlib import Path

dataset_root = Path("../dataset")
real_dir = "DeepFakeDetection"

print(f"Current working directory: {Path.cwd()}")
print(f"dataset_root: {dataset_root}")
print(f"dataset_root (absolute): {dataset_root.resolve()}")

real_path = dataset_root / real_dir
print(f"\nreal_path: {real_path}")
print(f"real_path (absolute): {real_path.resolve()}")
print(f"real_path.exists(): {real_path.exists()}")

if real_path.exists():
    video_files = sorted(real_path.glob("*.mp4"))
    print(f"Found {len(video_files)} videos")
    print(f"First few: {[f.name for f in video_files[:3]]}")
else:
    print("\n!!! PATH DOES NOT EXIST !!!")
    
    # Check what exists
    print(f"\nChecking parent: {Path.cwd().parent}")
    print(f"  dataset dir: {(Path.cwd().parent / 'dataset').exists()}")
    if (Path.cwd().parent / 'dataset').exists():
        print(f"  DeepFakeDetection: {(Path.cwd().parent / 'dataset' / 'DeepFakeDetection').exists()}")
