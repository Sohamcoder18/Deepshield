#!/usr/bin/env python3
"""
Voice Assistant Integration with Audio Ensemble Detector

Integrates the new ensemble audio detection with voice chat
to analyze audio in real-time for deepfake detection
"""

import logging
import os
from flask import Flask, request, jsonify
import tempfile

logger = logging.getLogger(__name__)

# Audio detection integration
from models.audio_ensemble_config import get_audio_detector_with_ensemble, check_model_availability
from models.audio_deepfake_detector import AudioDeepfakeDetector


class VoiceAssistantWithAudioAnalysis:
    """
    Enhanced Voice Assistant with integrated audio deepfake detection
    """
    
    def __init__(self):
        """Initialize voice assistant with audio detection"""
        self.audio_detector = None
        self.detector_available = False
        self._initialize_audio_detector()
    
    def _initialize_audio_detector(self):
        """Initialize audio detector with ensemble if available"""
        try:
            # Check model availability
            status = check_model_availability()
            
            if status['ensemble_available']:
                logger.info("✅ Both audio models available - initializing ensemble detector")
                self.audio_detector = get_audio_detector_with_ensemble(use_ensemble=True)
                self.detector_available = True
            else:
                logger.info("⚠️  Not all audio models available")
                
                if status['bigruattention']['available']:
                    logger.info("   Loading BiGRU+Attention model only")
                    self.audio_detector = get_audio_detector_with_ensemble(
                        bigruattention_path=status['bigruattention']['path'],
                        pretrained_path=None,
                        use_ensemble=False
                    )
                    self.detector_available = True
                elif status['pretrained']['available']:
                    logger.info("   Loading Pretrained model only")
                    self.audio_detector = get_audio_detector_with_ensemble(
                        bigruattention_path=None,
                        pretrained_path=status['pretrained']['path'],
                        use_ensemble=False
                    )
                    self.detector_available = True
                else:
                    logger.warning("   No audio detection models available - detection disabled")
                    self.detector_available = False
        
        except Exception as e:
            logger.warning(f"Failed to initialize audio detector: {e}")
            self.detector_available = False
    
    def analyze_voice_input(self, audio_blob_or_path, language='en-US'):
        """
        Analyze voice input for deepfake detection
        
        Args:
            audio_blob_or_path: Audio as bytes/blob or file path
            language: Language code (e.g., 'en-US')
        
        Returns:
            dict: Analysis results including transcription and deepfake detection
        """
        try:
            if not self.detector_available:
                logger.warning("Audio detector not available - skipping audio analysis")
                return {
                    'audio_analysis_available': False,
                    'message': 'Audio analysis not available'
                }
            
            # Save audio temporarily if blob provided
            if isinstance(audio_blob_or_path, bytes):
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(audio_blob_or_path)
                    audio_path = f.name
            else:
                audio_path = audio_blob_or_path
            
            try:
                # Perform audio analysis
                logger.info(f"Analyzing audio for deepfake detection: {audio_path}")
                result = self.audio_detector.predict(audio_path)
                
                analysis = {
                    'audio_analysis_available': True,
                    'deepfake_detected': result['is_fake'],
                    'fake_probability': result['fake'],
                    'real_probability': result['real'],
                    'confidence': result['confidence'],
                    'ensemble': result.get('ensemble', False),
                    'models_used': result.get('model_types', []),
                }
                
                # Add component predictions if ensemble
                if result.get('ensemble') and 'component_predictions' in result:
                    analysis['component_analysis'] = result['component_predictions']
                
                # Add confidence level assessment
                if result['confidence'] >= 0.75:
                    analysis['confidence_level'] = 'HIGH'
                elif result['confidence'] >= 0.55:
                    analysis['confidence_level'] = 'MEDIUM'
                else:
                    analysis['confidence_level'] = 'LOW'
                
                logger.info(f"Audio analysis complete: {'FAKE' if result['is_fake'] else 'REAL'} "
                           f"({result['confidence']:.1%} confidence)")
                
                return analysis
            
            finally:
                # Clean up temporary file if created
                if isinstance(audio_blob_or_path, bytes) and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {
                'audio_analysis_available': True,
                'error': str(e),
                'message': 'Audio analysis failed'
            }
    
    def voice_chat_with_detection(self, audio_blob, language='en-US', format='wav'):
        """
        Complete voice chat with integrated audio deepfake detection
        
        Args:
            audio_blob: Audio data as bytes
            language: Language code
            format: Audio format
        
        Returns:
            dict: Chat response with audio analysis
        """
        # Analyze audio for deepfakes
        audio_analysis = self.analyze_voice_input(audio_blob, language)
        
        # If deepfake detected, flag in response
        if audio_analysis.get('deepfake_detected'):
            logger.warning(f"⚠️  Deepfake audio detected! Confidence: {audio_analysis['confidence']}")
        
        # Perform normal voice chat
        # ... (normal voice chat processing)
        
        # Return results combined
        response = {
            'audio_analysis': audio_analysis,
            # ... (normal voice chat response)
        }
        
        return response


# Flask routes integration
def setup_voice_audio_routes(app):
    """
    Setup Flask routes for voice chat with audio analysis
    
    Args:
        app: Flask application instance
    """
    
    # Initialize voice assistant with detection
    voice_assistant = VoiceAssistantWithAudioAnalysis()
    
    @app.route('/api/voice/analyze-audio', methods=['POST'])
    def analyze_audio():
        """Analyze audio for deepfake detection"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            language = request.form.get('language', 'en-US')
            
            # Analyze audio
            with tempfile.NamedTemporaryFile(suffix='.wav') as f:
                audio_file.save(f.name)
                analysis = voice_assistant.analyze_voice_input(f.name, language)
            
            return jsonify(analysis)
        
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voice/chat-with-analysis', methods=['POST'])
    def voice_chat_with_analysis():
        """Voice chat with integrated audio analysis"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            language = request.form.get('language', 'en-US')
            format_type = request.form.get('format', 'wav')
            
            # Analyze audio
            audio_data = audio_file.read()
            result = voice_assistant.voice_chat_with_detection(
                audio_data,
                language=language,
                format=format_type
            )
            
            return jsonify(result)
        
        except Exception as e:
            logger.error(f"Voice chat error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voice/detector-status', methods=['GET'])
    def detector_status():
        """Get audio detector status"""
        try:
            status = check_model_availability()
            
            return jsonify({
                'detector_available': voice_assistant.detector_available,
                'ensemble_available': status['ensemble_available'],
                'bigruattention_available': status['bigruattention']['available'],
                'pretrained_available': status['pretrained']['available'],
                'models': {
                    'bigruattention': status['bigruattention']['path'],
                    'pretrained': status['pretrained']['path']
                }
            })
        
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    """Example usage"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize voice assistant
    va = VoiceAssistantWithAudioAnalysis()
    
    if va.detector_available:
        print("✅ Voice Assistant with Audio Detection initialized")
        print(f"   Audio Detector: Available")
        
        # Example: analyze a test audio file
        # result = va.analyze_voice_input("test_audio.wav", language='en-US')
        # print(f"Analysis result: {result}")
    else:
        print("⚠️  Voice Assistant initialized (audio detection unavailable)")
