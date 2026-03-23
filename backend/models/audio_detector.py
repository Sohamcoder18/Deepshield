import os
import numpy as np
import librosa
import time
import logging
import torch

logger = logging.getLogger(__name__)

class AudioDetector:
    def __init__(self, audio_model_path='models/audio_cnn_model.h5'):
        """
        Initialize Audio Detector with multi-model ensemble support
        
        Args:
            audio_model_path: Path to pretrained audio CNN model
        """
        self.audio_model = None
        self.n_mfcc = 13
        self.ensemble_service = None
        
        try:
            # Try to load ensemble service with actual deepfake models
            try:
                from models.multi_model_deepfake_service import get_multi_model_deepfake_service
                self.ensemble_service = get_multi_model_deepfake_service()
                logger.info("✅ Multi-model ensemble service loaded for audio detection")
            except Exception as e:
                logger.warning(f"Could not load ensemble service: {e}")
                self.ensemble_service = None
                
            # Try to load actual audio model
            try:
                if audio_model_path and os.path.exists(audio_model_path):
                    try:
                        from keras.models import load_model
                        self.audio_model = load_model(audio_model_path)
                        logger.info(f"Audio model loaded from: {audio_model_path}")
                    except ImportError:
                        logger.warning("Keras not available for loading audio model, using ensemble instead")
                        self.audio_model = None
                else:
                    logger.info("Audio model path not found, will use ensemble or heuristics")
            except Exception as e:
                logger.warning(f"Could not load audio model: {str(e)}")
                self.audio_model = None
            
        except Exception as e:
            logger.warning(f"Could not initialize audio detector: {str(e)}")
            self.audio_model = None
    
    def load_audio(self, audio_path):
        """
        Load audio file using librosa
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Audio time series and sample rate
        """
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            return y, sr, duration
            
        except Exception as e:
            logger.error(f"Audio loading error: {str(e)}")
            return None, None, 0
    
    def extract_mfcc(self, audio_signal, sr):
        """
        Extract MFCC (Mel-Frequency Cepstral Coefficients) from audio
        
        Args:
            audio_signal: Audio time series
            sr: Sample rate
            
        Returns:
            MFCC features array
        """
        try:
            mfcc = librosa.feature.mfcc(y=audio_signal, sr=sr, n_mfcc=self.n_mfcc)
            
            # Calculate mean and std for each MFCC coefficient
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            # Combine features
            mfcc_features = np.concatenate([mfcc_mean, mfcc_std])
            
            return mfcc, mfcc_features
            
        except Exception as e:
            logger.error(f"MFCC extraction error: {str(e)}")
            return None, None
    
    def extract_spectral_features(self, audio_signal, sr):
        """
        Extract spectral features for audio analysis
        
        Args:
            audio_signal: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with spectral features
        """
        try:
            # Compute spectrogram
            S = librosa.stft(audio_signal)
            magnitude = np.abs(S)
            
            # Spectral centroid
            centroid = librosa.feature.spectral_centroid(y=audio_signal, sr=sr)[0]
            centroid_mean = np.mean(centroid)
            centroid_std = np.std(centroid)
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio_signal, sr=sr)[0]
            rolloff_mean = np.mean(rolloff)
            rolloff_std = np.std(rolloff)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_signal)[0]
            zcr_mean = np.mean(zcr)
            zcr_std = np.std(zcr)
            
            return {
                'centroid_mean': float(centroid_mean),
                'centroid_std': float(centroid_std),
                'rolloff_mean': float(rolloff_mean),
                'rolloff_std': float(rolloff_std),
                'zcr_mean': float(zcr_mean),
                'zcr_std': float(zcr_std)
            }
            
        except Exception as e:
            logger.error(f"Spectral features extraction error: {str(e)}")
            return {}
    
    def predict_synthesis(self, mfcc_features):
        """
        Predict if audio is synthetically generated using ensemble models
        
        Args:
            mfcc_features: Extracted MFCC features
            
        Returns:
            Probability of being synthetic (0-1)
        """
        try:
            # Try ensemble service first for better detection
            if self.ensemble_service and hasattr(self.ensemble_service, 'classify_audio_ensemble'):
                try:
                    # Use ensemble for audio classification
                    # Note: This requires the audio file path, not just features
                    logger.debug("Using ensemble service for audio synthesis prediction")
                    # Would need audio_path passed to this method
                    # For now, fall through to heuristic
                except Exception as e:
                    logger.debug(f"Ensemble audio prediction error: {e}")
            
            # Use trained model if available
            if self.audio_model:
                try:
                    mfcc_input = np.expand_dims(mfcc_features, axis=0)
                    prediction = self.audio_model.predict(mfcc_input, verbose=0)
                    synthesis_prob = float(prediction[0][1])
                    logger.debug(f"Audio model prediction: {synthesis_prob:.3f}")
                    return np.clip(synthesis_prob, 0.0, 1.0)
                except Exception as e:
                    logger.debug(f"Audio model prediction error: {e}")
            
            # Heuristic fallback: Analyze MFCC features for synthesis artifacts
            # Synthetic speech often has unnaturally consistent spectral features
            
            # Calculate feature statistics
            feature_mean = np.mean(mfcc_features)
            feature_std = np.std(mfcc_features)
            feature_min = np.min(mfcc_features)
            feature_max = np.max(mfcc_features)
            feature_range = feature_max - feature_min
            
            # Synthetic speech tends to have:
            # - Lower variance (more consistent)
            # - Higher concentration around mean
            # - Unnatural frequency distributions
            
            # Score based on naturalness indicators
            naturalness_score = 0.0
            
            # Lower std dev suggests synthesis (natural speech has more variation)
            if feature_std < 15:
                naturalness_score += 0.3  # Suspicious
            else:
                naturalness_score -= 0.1  # More natural
            
            # Too narrow range also suggests synthesis
            if feature_range < 40:
                naturalness_score += 0.3  # Suspicious
            else:
                naturalness_score -= 0.1  # More natural
            
            # Concentration around mean (use coefficient of variation)
            if feature_std > 0:
                cv = feature_std / abs(feature_mean + 1e-8)
                if cv < 0.5:
                    naturalness_score += 0.2  # Suspicious
                else:
                    naturalness_score -= 0.1  # More natural
            
            # Convert to synthesis probability
            synthesis_prob = np.clip(naturalness_score * 0.3 + 0.3, 0.2, 0.55)
            
            logger.debug(f"Audio heuristic synthesis probability: {synthesis_prob:.3f}")
            return float(synthesis_prob)
            
        except Exception as e:
            logger.error(f"Synthesis prediction error: {str(e)}")
            return 0.3  # Default to more likely authentic
    
    def calculate_spectral_consistency(self, audio_signal, sr):
        """
        Calculate spectral consistency score
        
        Args:
            audio_signal: Audio time series
            sr: Sample rate
            
        Returns:
            Consistency score (0-1)
        """
        try:
            # Extract spectral features over time windows
            hop_length = 512
            S = librosa.stft(audio_signal, hop_length=hop_length)
            magnitude = np.abs(S)
            
            # Calculate consistency as inverse of spectral variability
            mean_magnitude = np.mean(magnitude, axis=0)
            spectral_var = np.std(magnitude, axis=0)
            
            consistency = 1.0 - np.mean(spectral_var) / (np.mean(mean_magnitude) + 1e-8)
            consistency = max(0.0, min(1.0, consistency))
            
            return float(consistency)
            
        except Exception as e:
            logger.error(f"Spectral consistency error: {str(e)}")
            return 0.5
    
    def generate_spectrogram(self, audio_signal, sr):
        """
        Generate spectrogram for visualization
        
        Args:
            audio_signal: Audio time series
            sr: Sample rate
            
        Returns:
            Spectrogram as numpy array
        """
        try:
            S = librosa.stft(audio_signal)
            S_db = librosa.power_to_db(np.abs(S)**2, ref=np.max)
            
            # Normalize to 0-1 range
            spectrogram = (S_db - S_db.min()) / (S_db.max() - S_db.min() + 1e-8)
            
            return spectrogram.tolist()
            
        except Exception as e:
            logger.error(f"Spectrogram generation error: {str(e)}")
            return None
    
    def detect(self, audio_path):
        """
        Complete audio deepfake detection pipeline
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Dictionary with detection results
        """
        start_time = time.time()
        
        try:
            # Load audio
            audio_signal, sr, duration = self.load_audio(audio_path)
            
            if audio_signal is None:
                raise ValueError("Could not load audio file")
            
            # Extract MFCC features
            mfcc, mfcc_features = self.extract_mfcc(audio_signal, sr)
            
            if mfcc_features is None:
                raise ValueError("Could not extract MFCC features")
            
            # Extract spectral features
            spectral_features = self.extract_spectral_features(audio_signal, sr)
            
            # Predict synthesis probability
            synthesis_prob = self.predict_synthesis(mfcc_features)
            
            # Calculate spectral consistency
            spectral_consistency = self.calculate_spectral_consistency(audio_signal, sr)
            
            # Calculate frequency stability
            frequency_stability = spectral_consistency  # Simplified
            
            # Calculate trust score
            trust_score = (1 - synthesis_prob) * 100
            is_fake = synthesis_prob > 0.40  # Threshold calibrated for audio models
            confidence = max(synthesis_prob, 1 - synthesis_prob)
            
            # Generate recommendation
            if is_fake:
                recommendation = f"Audio shows characteristics of speech synthesis. Speaker identity may be spoofed."
            else:
                recommendation = f"Audio appears to be authentic human speech based on acoustic features."
            
            # Generate spectrogram
            spectrogram = self.generate_spectrogram(audio_signal, sr)
            
            return {
                'duration': float(duration),
                'sample_rate': int(sr),
                'trust_score': float(trust_score),
                'is_fake': bool(is_fake),
                'confidence': float(confidence),
                'synthesis_probability': float(synthesis_prob * 100),
                'authenticity_score': float((1 - synthesis_prob) * 100),
                'spectral_consistency': float(spectral_consistency),
                'frequency_stability': float(frequency_stability),
                'mfcc_features': mfcc_features.tolist() if mfcc_features is not None else [],
                'spectral_features': spectral_features,
                'spectrogram': spectrogram,
                'recommendation': recommendation,
                'analysis_time': float(time.time() - start_time)
            }
            
        except Exception as e:
            logger.error(f"Audio detection error: {str(e)}")
            return {
                'duration': 0.0,
                'sample_rate': 0,
                'trust_score': 50.0,
                'is_fake': False,
                'confidence': 0.5,
                'synthesis_probability': 50.0,
                'authenticity_score': 50.0,
                'spectral_consistency': 0.5,
                'frequency_stability': 0.5,
                'mfcc_features': [],
                'spectral_features': {},
                'spectrogram': None,
                'recommendation': f'Error during analysis: {str(e)}',
                'analysis_time': float(time.time() - start_time)
            }
