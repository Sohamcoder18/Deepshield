#!/usr/bin/env python3
"""
Audio Ensemble Detector - Example Usage Script

Demonstrates using both BiGRU+Attention and Pretrained models together
for enhanced deepfake audio detection with ensemble voting
"""

import torch
import torchaudio
from pathlib import Path
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_waveform_preprocessing():
    """Example: Preprocess audio waveform following the provided script pattern"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 1: Audio Preprocessing Pipeline")
    logger.info("="*60)
    
    # This follows the exact pattern from the provided script
    print("""
    # Step 1: Load audio and resample to 16kHz
    waveform, sr = torchaudio.load("example.wav")
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)
    
    # Step 2: Ensure 4 seconds length (pad or truncate)
    target_len = 4 * 16000
    if waveform.shape[1] < target_len:
        pad = target_len - waveform.shape[1]
        waveform = torch.nn.functional.pad(waveform, (0, pad))
    else:
        waveform = waveform[:, :target_len]
    
    # Step 3: Feature extraction (wav2vec2)
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base")
    input_values = feature_extractor(waveform.squeeze(0).numpy(), 
                                     sampling_rate=16000, 
                                     return_tensors="pt").input_values
    
    # Step 4: Forward pass through model
    model.eval()
    with torch.no_grad():
        logits = model(input_values)          # model returns scalar logit
        prob = torch.sigmoid(logits).item()   # probability of fake
    
    prediction = 1 if prob >= 0.5 else 0
    confidence = prob if prediction == 1 else 1 - prob
    """)


def example_ensemble_prediction():
    """Example: Using ensemble prediction with both models"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 2: Ensemble Prediction")
    logger.info("="*60)
    
    print("""
    from models.audio_deepfake_detector import AudioDeepfakeDetector
    
    # Initialize detector with both models
    detector = AudioDeepfakeDetector(
        model_path="checkpoints/audio_bigruattention_model.pt",
        pretrained_checkpoint="checkpoints/audio_pretrained_wav2vec2_checkpoint.pt",
        use_ensemble=True
    )
    
    # Make prediction (automatically uses ensemble if both models available)
    result = detector.predict("audio_sample.wav")
    
    # Result includes ensemble information
    if result['ensemble']:
        print(f"Ensemble Result: {'FAKE' if result['is_fake'] else 'REAL'}")
        print(f"Fake Probability: {result['fake']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Models used: {result['model_types']}")
        
        # Component predictions show individual model outputs
        if 'component_predictions' in result:
            print("\\nComponent Predictions:")
            for model_name, pred in result['component_predictions'].items():
                print(f"  {model_name}:")
                print(f"    Fake: {pred['fake']}, Weight: {pred['weight']}")
    """)


def example_single_model_prediction():
    """Example: Using single model if pretrained checkpoint not available"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 3: Single Model Prediction")
    logger.info("="*60)
    
    print("""
    # If you only have the BiGRU+Attention model:
    detector = AudioDeepfakeDetector(
        model_path="checkpoints/audio_bigruattention_model.pt",
        pretrained_checkpoint=None  # Not using pretrained
    )
    
    result = detector.predict("audio_sample.wav")
    # Result will show 'ensemble': False
    # Uses only BiGRU+Attention model
    
    # Or if you only have the pretrained model:
    detector = AudioDeepfakeDetector(
        model_path=None,  # No BiGRU model
        pretrained_checkpoint="checkpoints/audio_pretrained_wav2vec2_checkpoint.pt"
    )
    
    result = detector.predict("audio_sample.wav")
    # Result will show 'ensemble': False
    # Uses only pretrained model
    """)


def example_batch_prediction():
    """Example: Batch prediction on multiple audio files"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 4: Batch Prediction")
    logger.info("="*60)
    
    print("""
    from pathlib import Path
    import json
    
    detector = AudioDeepfakeDetector(
        model_path="checkpoints/audio_bigruattention_model.pt",
        pretrained_checkpoint="checkpoints/audio_pretrained_wav2vec2_checkpoint.pt"
    )
    
    audio_files = list(Path("audio_samples/").glob("*.wav"))
    results = []
    
    for audio_file in audio_files:
        try:
            result = detector.predict(str(audio_file))
            result['file'] = str(audio_file)
            results.append(result)
            
            status = "FAKE" if result['is_fake'] else "REAL"
            print(f"{audio_file.name}: {status} ({result['confidence']:.3f})")
        except Exception as e:
            print(f"Error processing {audio_file.name}: {e}")
    
    # Save results to JSON
    with open("predictions.json", "w") as f:
        json.dump(results, f, indent=2)
    """)


def example_waveform_direct():
    """Example: Using waveform tensor directly instead of file path"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 5: Predict from Waveform Tensor")
    logger.info("="*60)
    
    print("""
    import torch
    from models.audio_deepfake_detector import AudioDeepfakeDetector
    
    # If you have audio as a waveform tensor (not a file):
    detector = AudioDeepfakeDetector(
        model_path="checkpoints/audio_bigruattention_model.pt",
        pretrained_checkpoint="checkpoints/audio_pretrained_wav2vec2_checkpoint.pt"
    )
    
    # Preprocess your waveform to shape (1, 64000) - 4 seconds at 16kHz
    waveform = torch.randn(1, 64000)  # Example random audio
    
    # Use the pretrained detector directly with waveform
    result = detector.pretrained_model.predict(waveform)
    
    # Or use the detector with a file path
    result = detector.predict("audio.wav")
    """)


def example_api_integration():
    """Example: Integration with backend API"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 6: Backend API Integration")
    logger.info("="*60)
    
    print("""
    # In your Flask/FastAPI backend:
    
    from models.audio_ensemble_config import get_audio_detector_with_ensemble
    
    # Initialize detector at app startup
    audio_detector = get_audio_detector_with_ensemble(use_ensemble=True)
    
    @app.route('/api/audio/analyze', methods=['POST'])
    def analyze_audio():
        audio_file = request.files['audio']
        
        # Save temporarily
        audio_path = f"/tmp/{audio_file.filename}"
        audio_file.save(audio_path)
        
        try:
            # Get ensemble prediction
            result = audio_detector.predict(audio_path)
            
            return jsonify({
                'is_fake': result['is_fake'],
                'confidence': result['confidence'],
                'fake_probability': result['fake'],
                'real_probability': result['real'],
                'ensemble': result['ensemble'],
                'models_used': result['model_types'],
                'component_predictions': result.get('component_predictions')
            })
        finally:
            os.remove(audio_path)
    """)


def example_error_handling():
    """Example: Proper error handling"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 7: Error Handling")
    logger.info("="*60)
    
    print("""
    from models.audio_deepfake_detector import AudioDeepfakeDetector
    
    detector = AudioDeepfakeDetector(
        model_path="checkpoints/audio_bigruattention_model.pt",
        pretrained_checkpoint="checkpoints/audio_pretrained_wav2vec2_checkpoint.pt"
    )
    
    try:
        result = detector.predict("audio_sample.wav")
        print(f"Prediction: {'FAKE' if result['is_fake'] else 'REAL'}")
    except ValueError as e:
        print(f"Invalid audio file: {e}")
    except RuntimeError as e:
        print(f"Model inference error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        # System will fall back to heuristic if models fail
    """)


def example_configuration():
    """Example: Custom configuration"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 8: Custom Configuration")
    logger.info("="*60)
    
    print("""
    from models.audio_ensemble_config import check_model_availability, ENSEMBLE_CONFIG
    
    # Check which models are available
    status = check_model_availability()
    print(f"Ensemble Available: {status['ensemble_available']}")
    
    # Customize ensemble settings
    if status['ensemble_available']:
        from models.audio_deepfake_detector import AudioDeepfakeDetector
        
        detector = AudioDeepfakeDetector(
            model_path=status['bigruattention']['path'],
            pretrained_checkpoint=status['pretrained']['path'],
            use_ensemble=True
        )
        
        # Make predictions
        result = detector.predict("audio.wav", use_ensemble=True)
        
        if result['ensemble'] and result['confidence'] >= ENSEMBLE_CONFIG['high_confidence_threshold']:
            print(f"HIGH CONFIDENCE: {result['is_fake']}")
        elif result['confidence'] >= ENSEMBLE_CONFIG['medium_confidence_threshold']:
            print(f"MEDIUM CONFIDENCE: {result['is_fake']}")
        else:
            print(f"LOW CONFIDENCE: {result['is_fake']}")
    """)


def main():
    """Run all examples"""
    logger.info("\n" + "="*70)
    logger.info("AUDIO DEEPFAKE DETECTION - ENSEMBLE EXAMPLES")
    logger.info("="*70)
    
    logger.info("\nThis guide shows how to use both BiGRU+Attention and Pretrained models")
    logger.info("together for enhanced audio deepfake detection.")
    
    example_waveform_preprocessing()
    example_ensemble_prediction()
    example_single_model_prediction()
    example_batch_prediction()
    example_waveform_direct()
    example_api_integration()
    example_error_handling()
    example_configuration()
    
    logger.info("\n" + "="*70)
    logger.info("For more information, see audio_ensemble_config.py")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()
