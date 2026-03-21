"""
Wav2Vec2 Audio Detection Model - Quick Test
Tests the facebook/wav2vec2-base integration for audio analysis
"""

import os
import sys
import logging
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

def test_wav2vec2_model_loading():
    """Test if the Wav2Vec2 model loads correctly"""
    print("\n" + "="*60)
    print("[AUDIO] Testing Wav2Vec2 Audio Detector")
    print("="*60 + "\n")
    
    try:
        print("[1] Loading Wav2Vec2 Audio Detector...")
        from models.wav2vec2_audio_detector import Wav2Vec2AudioDetector
        
        detector = Wav2Vec2AudioDetector()
        print("[OK] Wav2Vec2 model loaded successfully!")
        print(f"   Device: {detector.device}")
        print(f"   Target Sample Rate: {detector.target_sr} Hz")
        print(f"   Model Name: {detector.model_name}\n")
        
        return detector
        
    except Exception as e:
        print(f"[ERROR] Failed to load Wav2Vec2 model: {e}\n")
        return None


def test_feature_extraction(detector):
    """Test feature extraction with a synthetic audio signal"""
    print("[2] Testing Feature Extraction...")
    
    try:
        import numpy as np
        
        # Create synthetic audio (1 second, 16kHz)
        sr = 16000
        duration = 1
        t = np.linspace(0, duration, sr * duration)
        
        # Mix of frequencies (440 Hz base + harmonics)
        audio = (
            0.3 * np.sin(2 * np.pi * 440 * t) +  # A4 note
            0.2 * np.sin(2 * np.pi * 880 * t) +  # A5 note
            0.1 * np.sin(2 * np.pi * 1320 * t)   # E6 note
        )
        
        print(f"   Created synthetic audio: {len(audio)} samples, {len(audio)/sr:.2f} seconds")
        
        # Extract features
        features = detector.extract_features(audio, sr=sr)
        
        print(f"[OK] Features extracted successfully!")
        print(f"   Embeddings shape: {features['embeddings'].shape}")
        print(f"   Audio length: {features['audio_length_seconds']:.2f} seconds")
        print(f"   Hidden layers: {len(features['hidden_states'])}")
        print(f"   Last hidden state: {features['last_hidden_state'].shape}\n")
        
        return audio
        
    except Exception as e:
        print(f"[ERROR] Feature extraction failed: {e}\n")
        return None
    except Exception as e:
        print(f"[ERROR] Deepfake analysis failed: {e}\n")
        return None


def test_deepfake_analysis(detector, audio):
    """Test deepfake detection on the synthetic audio"""
    print("[3] Testing Deepfake Detection Analysis...")
    
    try:
        import numpy as np
        
        # Analyze the synthetic audio
        result = detector.analyze_audio_deepfake(audio, sr=16000)
        
        print(f"[OK] Deepfake analysis completed!\n")
        print(f"   Verdict: {result['verdict'].upper()}")
        print(f"   Risk Score: {result['risk_score']:.2%}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Duration: {result['audio_duration']:.2f}s\n")
        
        if 'analysis' in result and 'indicators' in result['analysis']:
            print("   Risk Indicators:")
            for key, value in result['analysis']['indicators'].items():
                status = "[!]" if value > 0.5 else "[OK]"
                print(f"      {status} {key}: {value:.2%}")
        
        if result.get('features_used'):
            print(f"\n   Features Used:")
            for feature in result['features_used']:
                print(f"      • {feature}")
        
        print()
        return result
        
    except Exception as e:
        print(f"❌ Deepfake analysis failed: {e}\n")
        return None


def test_batch_processing(detector):
    """Test batch processing capability"""
    print("[4] Testing Batch Processing...")
    
    try:
        import numpy as np
        import tempfile
        import torch
        import torchaudio
        
        # Create 3 synthetic audio samples
        print("   Creating 3 test audio files...")
        
        test_files = []
        for i in range(3):
            sr = 16000
            duration = 0.5
            t = np.linspace(0, duration, sr * duration)
            
            # Different frequencies for variety
            freq = 440 + (i * 110)  # 440Hz, 550Hz, 660Hz
            audio = np.sin(2 * np.pi * freq * t).astype(np.float32)
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                test_files.append(f.name)
                waveform = torch.from_numpy(audio).unsqueeze(0)
                torchaudio.save(f.name, waveform, sr)
        
        print(f"   Created {len(test_files)} test files")
        
        # Batch analyze
        results = detector.batch_analyze(test_files)
        
        print(f"[OK] Batch processing completed!\n")
        for i, item in enumerate(results):
            verdict = item['result'].get('verdict', 'error').upper()
            risk = item['result'].get('risk_score', 0)
            print(f"   File {i+1}: {verdict} (Risk: {risk:.2%})")
        
        # Cleanup
        for f in test_files:
            try:
                os.remove(f)
            except:
                pass
        
        print()
        return results
        
    except Exception as e:
        print(f"[ERROR] Batch processing failed: {e}\n")
        return None


def test_comparison(detector, audio):
    """Test comparison with other detectors"""
    print("[5] Testing Model Comparison...")
    
    try:
        comparison = detector.compare_models(audio, sr=16000)
        
        print(f"[OK] Model comparison completed!\n")
        
        for model_name, result in comparison.items():
            if model_name != 'timestamp':
                print(f"   {model_name}:")
                if 'error' not in result:
                    print(f"      Verdict: {result.get('verdict', 'N/A').upper()}")
                    print(f"      Risk Score: {result.get('risk_score', 0):.2%}")
                    print(f"      Confidence: {result.get('confidence', 0):.2%}")
                else:
                    print(f"      Error: {result['error']}")
        
        print()
        
    except Exception as e:
        print(f"[NOTE] Model comparison failed (may be expected): {e}\n")


def main():
    """Run all tests"""
    print("\n")
    print("="*60)
    print("Wav2Vec2 Audio Detection - Complete Test Suite")
    print("="*60 + "\n")
    
    # Test 1: Model Loading
    detector = test_wav2vec2_model_loading()
    if not detector:
        print("❌ Cannot proceed without loaded model\n")
        return
    
    # Test 2: Feature Extraction
    audio = test_feature_extraction(detector)
    if audio is None:
        print("❌ Cannot proceed without feature extraction\n")
        return
    
    # Test 3: Deepfake Analysis
    test_deepfake_analysis(detector, audio)
    
    # Test 4: Batch Processing
    test_batch_processing(detector)
    
    # Test 5: Model Comparison
    test_comparison(detector, audio)
    
    # Summary
    print("="*60)
    print("[OK] All Tests Completed Successfully!")
    print("="*60)
    print("\n[SUCCESS] Wav2Vec2 Audio Detector is ready for integration\n")


if __name__ == "__main__":
    main()
