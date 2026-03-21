import sys
print("Step 1: Testing Wav2Vec2 model import...")
try:
    from models.wav2vec2_audio_detector import Wav2Vec2AudioDetector
    print("[OK] Successfully imported Wav2Vec2AudioDetector")
except Exception as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

print("\nStep 2: Initializing Wav2Vec2 detector...")
try:
    detector = Wav2Vec2AudioDetector()
    print("[OK] Detector created successfully")
    print(f"   Device: {detector.device}")
    print(f"   Model: {detector.model_name}")
    print(f"   Sample Rate: {detector.target_sr}Hz")
except Exception as e:
    print(f"[ERROR] Failed to create detector: {e}")
    sys.exit(1)

print("\nStep 3: Creating synthetic audio for testing...")
try:
    import numpy as np
    sr = 16000
    duration = 1  
    t = np.linspace(0, duration, sr * duration)
    audio = (
        0.3 * np.sin(2 * np.pi * 440 * t) +
        0.2 * np.sin(2 * np.pi * 880 * t) +
        0.1 * np.sin(2 * np.pi * 1320 * t)
    )
    print(f"[OK] Created synthetic audio: {len(audio)} samples, {duration}s")
except Exception as e:
    print(f"[ERROR] Failed to create audio: {e}")
    sys.exit(1)

print("\nStep 4: Extracting features...")
try:
    features = detector.extract_features(audio, sr=sr)
    print("[OK] Features extracted")
    print(f"   Embeddings: {features['embeddings'].shape}")
    print(f"   Hidden states: {len(features['hidden_states'])} layers")
except Exception as e:
    print(f"[ERROR] Failed to extract features: {e}")
    sys.exit(1)

print("\nStep 5: Running deepfake analysis...")
try:
    result = detector.analyze_audio_deepfake(audio, sr=sr)
    print("[OK] Analysis completed")
    print(f"   Verdict: {result['verdict'].upper()}")
    print(f"   Risk Score: {result['risk_score']:.2%}")
    print(f"   Confidence: {result['confidence']:.2%}")
except Exception as e:
    print(f"[ERROR] Failed to analyze: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("SUCCESS: Wav2Vec2 Audio Detector works perfectly!")
print("="*60 + "\n")
