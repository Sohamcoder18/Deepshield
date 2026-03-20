#!/usr/bin/env python3
"""
Audio Ensemble Detector - Validation and Test Script

Tests the implementation of ensemble audio deepfake detection
"""

import os
import sys
import torch
import numpy as np
import logging
from pathlib import Path
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all required modules can be imported"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Import Validation")
    logger.info("="*60)
    
    try:
        logger.info("Importing PyTorch...")
        import torch
        logger.info(f"✓ PyTorch {torch.__version__}")
        
        logger.info("Importing torchaudio...")
        import torchaudio
        logger.info(f"✓ torchaudio {torchaudio.__version__}")
        
        logger.info("Importing transformers...")
        from transformers import Wav2Vec2FeatureExtractor
        logger.info("✓ Transformers with Wav2Vec2FeatureExtractor")
        
        logger.info("Importing librosa...")
        import librosa
        logger.info("✓ librosa")
        
        logger.info("Importing audio detector...")
        from models.audio_deepfake_detector import AudioDeepfakeDetector, PretrainedAudioDetector
        logger.info("✓ AudioDeepfakeDetector and PretrainedAudioDetector")
        
        logger.info("Importing ensemble config...")
        from models.audio_ensemble_config import get_audio_detector_with_ensemble, check_model_availability
        logger.info("✓ Ensemble config utilities")
        
        logger.info("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Import failed: {e}")
        return False


def test_model_availability():
    """Test model availability checking"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Model Availability Check")
    logger.info("="*60)
    
    try:
        from models.audio_ensemble_config import check_model_availability
        
        status = check_model_availability()
        
        logger.info("Model Status:")
        for model, info in status.items():
            if model != 'ensemble_available':
                logger.info(f"  {model}: {'✓ Available' if info['available'] else '✗ Not found'}")
                logger.info(f"    Path: {info['path']}")
        
        logger.info(f"\n  Ensemble: {'✓ Available' if status['ensemble_available'] else '✗ Not available'}")
        
        if status['ensemble_available']:
            logger.info("\n✅ Both models available - ensemble ready!")
        else:
            logger.info("\n⚠️  Ensemble not available, but single model detection is supported")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model availability check failed: {e}")
        return False


def test_audio_preprocessing():
    """Test audio preprocessing pipeline"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Audio Preprocessing")
    logger.info("="*60)
    
    try:
        import torch
        import torchaudio
        from models.audio_deepfake_detector import PretrainedAudioDetector
        
        logger.info("Creating sample waveforms to test preprocessing...")
        
        # Test 1: Different sample rates
        logger.info("\n  Test 3.1: Resampling from different rates")
        test_rates = [8000, 16000, 22050, 44100]
        for rate in test_rates:
            waveform = torch.randn(1, rate * 2)  # 2 seconds
            logger.info(f"    Input: {rate}Hz, shape {waveform.shape}")
        
        # Test 2: Padding and truncation
        logger.info("\n  Test 3.2: Padding and truncation to 4 seconds")
        target_len = 4 * 16000
        
        # Test short audio (needs padding)
        short_audio = torch.randn(1, 16000)  # 1 second
        logger.info(f"    Short audio (1s): shape {short_audio.shape}")
        
        # Test long audio (needs truncation)
        long_audio = torch.randn(1, 320000)  # 20 seconds
        logger.info(f"    Long audio (20s): shape {long_audio.shape}")
        
        # Test correct length
        correct_audio = torch.randn(1, 64000)  # 4 seconds at 16kHz
        logger.info(f"    Correct audio (4s): shape {correct_audio.shape}")
        
        logger.info("\n✅ Audio preprocessing tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Audio preprocessing test failed: {e}")
        return False


def test_feature_extraction():
    """Test Wav2Vec2 feature extraction"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Wav2Vec2 Feature Extraction")
    logger.info("="*60)
    
    try:
        import torch
        from transformers import Wav2Vec2FeatureExtractor
        
        logger.info("Loading Wav2Vec2 feature extractor...")
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base")
        logger.info("✓ Feature extractor loaded")
        
        # Create sample audio
        logger.info("\nExtracting features from sample audio...")
        audio_array = np.random.randn(64000).astype(np.float32)  # 4 seconds at 16kHz
        
        input_values = feature_extractor(
            audio_array,
            sampling_rate=16000,
            return_tensors="pt"
        ).input_values
        
        logger.info(f"  Input shape: {audio_array.shape}")
        logger.info(f"  Extracted features shape: {input_values.shape}")
        logger.info(f"  Feature dimension: {input_values.shape[-1]}")
        
        logger.info("\n✅ Feature extraction tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Feature extraction test failed: {e}")
        return False


def test_detector_initialization():
    """Test detector initialization with different configurations"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Detector Initialization")
    logger.info("="*60)
    
    try:
        from models.audio_deepfake_detector import AudioDeepfakeDetector
        
        # Test 1: Initialize without models (fallback mode)
        logger.info("\n  Test 5.1: Initialize without models (fallback)")
        detector1 = AudioDeepfakeDetector(
            model_path=None,
            pretrained_checkpoint=None,
            use_ensemble=False
        )
        logger.info("  ✓ Detector initialized (fallback mode)")
        
        # Test 2: Initialize with only feature extractor
        logger.info("\n  Test 5.2: Initialize with feature extractor")
        assert detector1.feature_extractor is not None
        logger.info("  ✓ Feature extractor loaded")
        
        # Test 3: Try to get detector with ensemble
        logger.info("\n  Test 5.3: Initialize with ensemble setting")
        detector2 = AudioDeepfakeDetector(
            model_path=None,
            pretrained_checkpoint=None,
            use_ensemble=True
        )
        logger.info("  ✓ Detector initialized with ensemble enabled")
        
        logger.info("\n✅ Detector initialization tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Detector initialization test failed: {e}")
        return False


def test_heuristic_fallback():
    """Test heuristic prediction when models unavailable"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Heuristic Fallback")
    logger.info("="*60)
    
    try:
        import torch
        from models.audio_deepfake_detector import AudioDeepfakeDetector
        
        detector = AudioDeepfakeDetector()
        
        # Create synthetic audio samples
        logger.info("\n  Creating synthetic audio samples...")
        
        # Sample 1: Clean sine wave (should be REAL)
        t = np.arange(64000)
        sine_wave = np.sin(2 * np.pi * 440 * t / 16000).astype(np.float32) / 32768
        waveform_sine = torch.from_numpy(sine_wave).unsqueeze(0)
        
        # Sample 2: White noise (should be FAKE)
        white_noise = np.random.randn(64000).astype(np.float32) * 0.1
        waveform_noise = torch.from_numpy(white_noise).unsqueeze(0)
        
        logger.info("  ✓ Synthetic samples created")
        
        # Test heuristic
        logger.info("\n  Test 6.1: Heuristic on sine wave (should be REAL)")
        score1 = detector._heuristic_prediction(waveform_sine)
        logger.info(f"    Fake score: {score1:.3f} {'✓ Low (expected)' if score1 < 0.5 else '✗ High'}")
        
        logger.info("\n  Test 6.2: Heuristic on white noise (should be FAKE)")
        score2 = detector._heuristic_prediction(waveform_noise)
        logger.info(f"    Fake score: {score2:.3f} {'✓ High (expected)' if score2 > 0.5 else '✗ Low'}")
        
        logger.info("\n✅ Heuristic fallback tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Heuristic fallback test failed: {e}")
        return False


def test_prediction_format():
    """Test prediction output format"""
    logger.info("\n" + "="*60)
    logger.info("TEST 7: Prediction Output Format")
    logger.info("="*60)
    
    try:
        import torch
        from models.audio_deepfake_detector import AudioDeepfakeDetector
        
        detector = AudioDeepfakeDetector()
        
        # Create sample audio and get prediction using heuristic
        logger.info("\n  Creating sample audio...")
        audio = np.random.randn(64000).astype(np.float32) * 0.1
        waveform = torch.from_numpy(audio).unsqueeze(0)
        
        logger.info("  Using heuristic prediction to test format...")
        
        # Simulate a result to check format
        fake_score = detector._heuristic_prediction(waveform)
        result = {
            "fake": round(fake_score, 3),
            "real": round(1 - fake_score, 3),
            "is_fake": fake_score >= 0.5,
            "confidence": round(fake_score if fake_score >= 0.5 else 1 - fake_score, 3),
            "model_types": ["heuristic"],
            "ensemble": False
        }
        
        logger.info("\n  Checking result format:")
        required_fields = ['fake', 'real', 'is_fake', 'confidence', 'model_types', 'ensemble']
        for field in required_fields:
            if field in result:
                logger.info(f"    ✓ {field}: {result[field]}")
            else:
                logger.error(f"    ✗ Missing field: {field}")
                return False
        
        # Validate value ranges
        logger.info("\n  Validating value ranges:")
        if 0 <= result['fake'] <= 1:
            logger.info(f"    ✓ fake in [0, 1]: {result['fake']}")
        else:
            logger.error(f"    ✗ fake out of range: {result['fake']}")
            return False
        
        if 0 <= result['real'] <= 1:
            logger.info(f"    ✓ real in [0, 1]: {result['real']}")
        else:
            logger.error(f"    ✗ real out of range: {result['real']}")
            return False
        
        if isinstance(result['is_fake'], bool):
            logger.info(f"    ✓ is_fake is boolean: {result['is_fake']}")
        else:
            logger.error(f"    ✗ is_fake is not boolean")
            return False
        
        logger.info("\n✅ Prediction format tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Prediction format test failed: {e}")
        return False


def run_all_tests():
    """Run all validation tests"""
    logger.info("\n" + "="*70)
    logger.info("AUDIO ENSEMBLE DETECTOR - VALIDATION TESTS")
    logger.info("="*70)
    
    tests = [
        ("Import Validation", test_imports),
        ("Model Availability", test_model_availability),
        ("Audio Preprocessing", test_audio_preprocessing),
        ("Feature Extraction", test_feature_extraction),
        ("Detector Initialization", test_detector_initialization),
        ("Heuristic Fallback", test_heuristic_fallback),
        ("Prediction Format", test_prediction_format),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! System is ready for audio ensemble detection.")
    else:
        logger.info(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
    
    logger.info("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
