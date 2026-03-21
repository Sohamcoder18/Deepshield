"""
Wav2Vec2 Audio Detection Model
Direct integration of facebook/wav2vec2-base for audio analysis and deepfake detection
"""

import torch
import torchaudio
import numpy as np
import librosa
from transformers import AutoProcessor, AutoModelForPreTraining, AutoModel
import logging
from typing import Union, Tuple, Dict
import warnings

logger = logging.getLogger(__name__)

class Wav2Vec2AudioDetector:
    """
    Advanced Audio Deepfake Detection using Wav2Vec2-base
    Directly loads pretrained model from HuggingFace for feature extraction and analysis
    """
    
    def __init__(self, model_name: str = "facebook/wav2vec2-base", device: str = None):
        """
        Initialize Wav2Vec2 Audio Detector
        
        Args:
            model_name: HuggingFace model identifier (default: facebook/wav2vec2-base)
            device: Device to use ('cuda' or 'cpu'). Auto-detects if None
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.target_sr = 16000  # Wav2Vec2 expects 16kHz
        
        logger.info(f"[AUDIO] Initializing Wav2Vec2 Audio Detector")
        logger.info(f"   Model: {model_name}")
        logger.info(f"   Device: {self.device}")
        
        self._load_model()
    
    def _load_model(self):
        """Load processor and model from HuggingFace"""
        try:
            logger.info("[MODEL] Loading Wav2Vec2 processor...")
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            logger.info("[OK] Processor loaded successfully")
            
            # Try to load the main model instead of PreTraining
            logger.info("[MODEL] Loading Wav2Vec2 model...")
            try:
                from transformers import AutoModel
                self.model = AutoModel.from_pretrained(self.model_name)
            except:
                # Fallback to PreTraining model if AutoModel fails
                logger.info("[MODEL] Using AutoModelForPreTraining (output_hidden_states=True)")
                self.model = AutoModelForPreTraining.from_pretrained(self.model_name)
            
            self.model.to(self.device)
            self.model.eval()
            logger.info("[OK] Model loaded successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to load Wav2Vec2 model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def load_audio(self, audio_input: Union[str, np.ndarray], sr: int = None) -> Tuple[np.ndarray, int]:
        """
        Load and resample audio to 16kHz
        
        Args:
            audio_input: Path to audio file or numpy array
            sr: Sample rate (if audio_input is array)
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            if isinstance(audio_input, str):
                logger.debug(f"Loading audio file: {audio_input}")
                y, sr = librosa.load(audio_input, sr=self.target_sr)
            else:
                y = audio_input
                if sr is None:
                    raise ValueError("Sample rate must be provided for numpy array input")
                if sr != self.target_sr:
                    logger.debug(f"Resampling from {sr}Hz to {self.target_sr}Hz")
                    y = librosa.resample(y, orig_sr=sr, target_sr=self.target_sr)
            
            return y, self.target_sr
            
        except Exception as e:
            logger.error(f"[ERROR] Audio loading failed: {e}")
            raise
    
    def extract_features(self, audio_input: Union[str, np.ndarray], sr: int = None) -> Dict:
        """
        Extract Wav2Vec2 features from audio
        
        Args:
            audio_input: Path to audio file or numpy array
            sr: Sample rate (if audio_input is array)
            
        Returns:
            Dictionary containing:
            - last_hidden_state: Wav2Vec2 hidden representations
            - hidden_states: All layer outputs
            - features: Acoustic features
            - embeddings: Final embeddings
        """
        try:
            # Load audio
            audio_array, sr = self.load_audio(audio_input, sr)
            
            # Process with Wav2Vec2 processor
            inputs = self.processor(audio_array, sampling_rate=sr, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model outputs
            with torch.no_grad():
                # Try to get outputs with hidden_states
                try:
                    outputs = self.model(**inputs, output_hidden_states=True)
                    features_dict = {
                        'last_hidden_state': outputs.last_hidden_state.cpu().numpy(),
                        'hidden_states': [h.cpu().numpy() for h in outputs.hidden_states],
                        'embeddings': outputs.last_hidden_state.cpu().numpy(),
                        'audio_length_seconds': len(audio_array) / sr,
                        'sample_rate': sr
                    }
                except (AttributeError, TypeError):
                    # Fallback: if model output doesn't have last_hidden_state
                    outputs = self.model(**inputs)
                    
                    # Try to extract from different output formats
                    if hasattr(outputs, 'hidden_states') and outputs.hidden_states:
                        last_hidden = outputs.hidden_states[-1]
                    elif hasattr(outputs, 'last_hidden_state'):
                        last_hidden = outputs.last_hidden_state
                    elif isinstance(outputs, tuple):
                        last_hidden = outputs[0]  # First element is usually the main output
                    else:
                        # Fallback to processing input directly
                        last_hidden = inputs['input_values']
                    
                    if isinstance(last_hidden, torch.Tensor):
                        last_hidden = last_hidden.cpu().numpy()
                    
                    features_dict = {
                        'last_hidden_state': last_hidden,
                        'hidden_states': [],
                        'embeddings': last_hidden,
                        'audio_length_seconds': len(audio_array) / sr,
                        'sample_rate': sr
                    }
            
            logger.debug(f"[OK] Features extracted - Shape: {features_dict['embeddings'].shape}")
            return features_dict
            
        except Exception as e:
            logger.error(f"[ERROR] Feature extraction failed: {e}")
            raise
    
    def analyze_audio_deepfake(self, audio_input: Union[str, np.ndarray], sr: int = None) -> Dict:
        """
        Analyze audio for deepfake characteristics using Wav2Vec2 features
        
        Args:
            audio_input: Path to audio file or numpy array
            sr: Sample rate (if audio_input is array)
            
        Returns:
            Dictionary containing:
            - verdict: 'real', 'fake', 'suspicious'
            - confidence: 0.0-1.0 confidence score
            - risk_score: 0.0-1.0 risk score
            - analysis: Detailed analysis
            - features_used: Which features triggered detection
        """
        try:
            # Extract features
            features = self.extract_features(audio_input, sr)
            embeddings = features['embeddings']
            
            # Analyze embeddings for deepfake indicators
            analysis_results = self._analyze_embeddings(embeddings, features)
            
            # Calculate verdict
            risk_score = analysis_results['risk_score']
            confidence = analysis_results['confidence']
            
            if risk_score >= 0.75:
                verdict = 'fake'
            elif risk_score >= 0.55:
                verdict = 'suspicious'
            else:
                verdict = 'real'
            
            result = {
                'verdict': verdict,
                'confidence': float(confidence),
                'risk_score': float(risk_score),
                'audio_duration': features['audio_length_seconds'],
                'sample_rate': features['sample_rate'],
                'analysis': analysis_results,
                'features_used': self._get_features_used(analysis_results)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Audio deepfake analysis failed: {e}")
            return {
                'verdict': 'error',
                'confidence': 0.0,
                'risk_score': 0.0,
                'error': str(e)
            }
    
    def _analyze_embeddings(self, embeddings: np.ndarray, features: Dict) -> Dict:
        """
        Analyze Wav2Vec2 embeddings for deepfake characteristics
        
        Args:
            embeddings: Shape (batch, time_steps, hidden_dim)
            features: Feature dictionary from extraction
            
        Returns:
            Analysis results with risk indicators
        """
        batch_size, time_steps, hidden_dim = embeddings.shape
        
        # Calculate statistical features
        mean_embedding = np.mean(embeddings, axis=1)  # (batch, hidden_dim)
        std_embedding = np.std(embeddings, axis=1)
        
        # Feature 1: Embedding variation (humans have more natural variation)
        variation_score = np.mean(std_embedding)
        too_smooth = 1.0 if variation_score < 0.1 else 0.0
        
        # Feature 2: Temporal consistency (deepfakes often have artifacts)
        temporal_diffs = np.diff(embeddings, axis=1)
        temporal_variance = np.mean(np.std(temporal_diffs, axis=1))
        inconsistent_temporal = 1.0 if temporal_variance < 0.05 else 0.0
        
        # Feature 3: Energy distribution
        energy = np.linalg.norm(embeddings, axis=2)  # (batch, time_steps)
        energy_mean = np.mean(energy)
        energy_std = np.std(energy)
        unnatural_energy = 1.0 if energy_std < 0.05 or energy_mean > 15 else 0.0
        
        # Feature 4: Frequency characteristics from MFCC
        # Skip MFCC check if audio array not available
        unusual_mfcc = 0.0
        
        # Aggregate risk indicators
        risk_indicators = [
            too_smooth * 0.25,
            inconsistent_temporal * 0.25,
            unnatural_energy * 0.25,
            unusual_mfcc * 0.25
        ]
        
        risk_score = np.mean(risk_indicators)
        confidence = 0.7 + (0.3 * abs(0.5 - risk_score) * 2)  # Higher confidence at extremes
        confidence = min(1.0, confidence)
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'indicators': {
                'too_smooth': float(too_smooth),
                'inconsistent_temporal': float(inconsistent_temporal),
                'unnatural_energy': float(unnatural_energy),
                'unusual_mfcc': float(unusual_mfcc)
            },
            'measurements': {
                'embedding_variation': float(variation_score),
                'temporal_variance': float(temporal_variance),
                'energy_mean': float(energy_mean),
                'energy_std': float(energy_std)
            }
        }
    
    def _get_features_used(self, analysis: Dict) -> list:
        """Extract features that triggered detection"""
        features = []
        indicators = analysis.get('indicators', {})
        
        if indicators.get('too_smooth', 0) > 0.5:
            features.append('Embedding too smooth (lacks natural variation)')
        if indicators.get('inconsistent_temporal', 0) > 0.5:
            features.append('Temporal inconsistency detected')
        if indicators.get('unnatural_energy', 0) > 0.5:
            features.append('Unnatural energy distribution')
        if indicators.get('unusual_mfcc', 0) > 0.5:
            features.append('Unusual frequency characteristics')
        
        return features if features else ['Standard audio characteristics']
    
    def batch_analyze(self, audio_paths: list) -> list:
        """
        Analyze multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            
        Returns:
            List of analysis results
        """
        results = []
        for audio_path in audio_paths:
            try:
                logger.info(f"Analyzing: {audio_path}")
                result = self.analyze_audio_deepfake(audio_path)
                results.append({
                    'file': audio_path,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Failed to analyze {audio_path}: {e}")
                results.append({
                    'file': audio_path,
                    'result': {'error': str(e)}
                })
        
        return results
    
    def compare_models(self, audio_input: Union[str, np.ndarray], sr: int = None) -> Dict:
        """
        Compare analysis with other detectors (if available)
        
        Args:
            audio_input: Path to audio file or numpy array
            sr: Sample rate
            
        Returns:
            Comparison results
        """
        try:
            wav2vec2_result = self.analyze_audio_deepfake(audio_input, sr)
            
            comparison = {
                'wav2vec2_audio_detector': wav2vec2_result,
                'timestamp': str(np.datetime64('now'))
            }
            
            # Try to compare with other detectors if available
            try:
                from models.audio_detector import AudioDetector
                audio_detector = AudioDetector()
                if isinstance(audio_input, str):
                    audio_path = audio_input
                else:
                    # Save temp file for librosa
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
                        torchaudio.save(f.name, torch.from_numpy(audio_input).unsqueeze(0), sr)
                        audio_path = f.name
                
                standard_result = audio_detector.detect(audio_path)
                if standard_result:
                    comparison['audio_detector'] = standard_result
            except Exception as e:
                logger.debug(f"Could not load standard AudioDetector for comparison: {e}")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Model comparison failed: {e}")
            return {'error': str(e)}


# Convenience function for quick usage
def create_wav2vec2_detector() -> Wav2Vec2AudioDetector:
    """Create and return a Wav2Vec2 audio detector instance"""
    return Wav2Vec2AudioDetector()


if __name__ == "__main__":
    # Example usage
    detector = Wav2Vec2AudioDetector()
    
    # Example: Analyze a single audio file
    # result = detector.analyze_audio_deepfake("path/to/audio.wav")
    # print(result)
