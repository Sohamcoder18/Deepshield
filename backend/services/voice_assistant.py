"""
Voice Assistant Service
Handles speech-to-text and text-to-speech conversion for the AI assistant.
"""

import logging
import os
import io
from typing import Optional, Tuple
from datetime import datetime
import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Handles voice input and output for AI assistant"""
    
    def __init__(self):
        """Initialize voice assistant with speech recognition and TTS engines"""
        self.recognizer = sr.Recognizer()
        # Adjust recognizer sensitivity
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Configure voice (prefer female voice if available)
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    
    def speech_to_text(self, audio_data: bytes, language: str = 'en-US') -> Tuple[bool, str]:
        """
        Convert audio bytes to text using Google Speech Recognition
        
        Args:
            audio_data: Audio file bytes (WAV, MP3, WebM, etc.)
            language: Language code (default: 'en-US')
        
        Returns:
            Tuple of (success: bool, text: str)
        """
        try:
            audio_stream = io.BytesIO(audio_data)
            
            # Try to detect and convert audio format to WAV
            clean_audio_data = self._ensure_wav_format(audio_data)
            
            # Load audio file
            audio_stream = io.BytesIO(clean_audio_data)
            
            try:
                with sr.AudioFile(audio_stream) as source:
                    audio = self.recognizer.record(source)
            except Exception as e:
                logger.warning(f"Could not use sr.AudioFile, trying alternative method: {e}")
                # Try direct audio data conversion
                return self._transcribe_with_groq(clean_audio_data, language)
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=language)
            logger.info(f"✓ Speech recognition successful: {text[:50]}...")
            return True, text
            
        except sr.UnknownValueError:
            error_msg = "Could not understand audio. Please try again with clearer speech."
            logger.warning(error_msg)
            return False, error_msg
        except sr.RequestError as e:
            error_msg = f"Speech recognition service error: {str(e)}"
            logger.error(error_msg)
            # Fallback to Groq if available
            try:
                return self._transcribe_with_groq(audio_data, language)
            except:
                return False, error_msg
        except Exception as e:
            error_msg = f"Error in speech-to-text: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _ensure_wav_format(self, audio_data: bytes) -> bytes:
        """
        Ensure audio data is in WAV format for compatibility
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Audio bytes in WAV format
        """
        try:
            # Check if it's already WAV by looking for RIFF header
            if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                logger.info(f"Audio is already in WAV format ({len(audio_data)} bytes)")
                return audio_data
            
            # Try to detect format using pydub (requires ffmpeg)
            try:
                audio_stream = io.BytesIO(audio_data)
                audio = AudioSegment.from_file(audio_stream)
                logger.info(f"Detected audio format, duration: {len(audio)/1000:.2f}s")
                
                # Convert to WAV
                wav_io = io.BytesIO()
                audio.export(wav_io, format='wav')
                wav_io.seek(0)
                wav_data = wav_io.read()
                
                logger.info(f"Converted audio to WAV: {len(wav_data)} bytes")
                return wav_data
                
            except Exception as e:
                logger.warning(f"Could not use pydub for conversion (ffmpeg may be missing): {e}")
                
                # Try explicit format detection without ffmpeg
                # Check for WebM Opus header
                if audio_data[:4] == b'\x1a\x45\xdf\xa3':  # EBML (WebM)
                    logger.info("Detected WebM format, but cannot convert without ffmpeg")
                    return audio_data
                
                # Check for Ogg Vorbis
                if audio_data[:4] == b'OggS':
                    logger.info("Detected Ogg Vorbis format, but cannot convert without ffmpeg")
                    return audio_data
                
                # Check for FLAC
                if audio_data[:4] == b'fLaC':
                    logger.info("Detected FLAC format, but cannot convert without ffmpeg")
                    return audio_data
                
                logger.warning(f"Could not detect audio format, returning original ({len(audio_data)} bytes)")
                return audio_data
                
        except Exception as e:
            logger.error(f"Error ensuring WAV format: {e}")
            return audio_data
    
    def _transcribe_with_groq(self, audio_data: bytes, language: str) -> Tuple[bool, str]:
        """
        Transcribe using Groq API as fallback
        
        Args:
            audio_data: Audio file bytes
            language: Language code
            
        Returns:
            Tuple of (success: bool, text: str)
        """
        try:
            import os
            groq_api_key = os.getenv('GROQ_API_KEY', '')
            
            if not groq_api_key or groq_api_key.startswith('<'):
                raise Exception("Groq API key not configured")
            
            from groq import Groq
            
            client = Groq(api_key=groq_api_key)
            
            # Normalize language code to Groq format
            # Groq supports 2-letter language codes only (en, es, fr, etc.)
            language_code = language.split('-')[0].lower() if language else 'en'
            
            # Ensure WAV format for Groq
            audio_stream = io.BytesIO(audio_data)
            
            transcript = client.audio.transcriptions.create(
                file=("audio.wav", audio_stream, "audio/wav"),
                model="whisper-large-v3-turbo",
                language=language_code
            )
            
            logger.info(f"✓ Groq transcription successful: {transcript.text[:50]}...")
            return True, transcript.text
            
        except Exception as e:
            error_msg = f"Groq transcription failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def text_to_speech(self, text: str, output_format: str = 'wav') -> Tuple[bool, bytes]:
        """
        Convert text to speech audio bytes
        
        Args:
            text: Text to convert to speech
            output_format: Output audio format ('wav' or 'mp3')
        
        Returns:
            Tuple of (success: bool, audio_bytes: bytes)
        """
        try:
            if not text or not text.strip():
                return False, b''
            
            # Limit text length for TTS (avoid very long speeches)
            max_length = 1000
            if len(text) > max_length:
                text = text[:max_length] + "..."
                logger.warning(f"Text truncated to {max_length} characters for TTS")
            
            # Save to temporary file
            temp_file = f"/tmp/tts_output_{datetime.now().timestamp()}.wav"
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()
            
            # Read audio file and convert to bytes
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    audio_bytes = f.read()
                
                # Convert to target format if needed
                if output_format.lower() == 'mp3':
                    audio = AudioSegment.from_wav(temp_file)
                    mp3_io = io.BytesIO()
                    audio.export(mp3_io, format='mp3', bitrate='192k')
                    audio_bytes = mp3_io.getvalue()
                
                # Cleanup
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                logger.info(f"✓ Text-to-speech successful: {len(audio_bytes)} bytes")
                return True, audio_bytes
            else:
                return False, b''
                
        except Exception as e:
            error_msg = f"Error in text-to-speech: {str(e)}"
            logger.error(error_msg)
            return False, b''
    
    def process_voice_input(self, audio_file_path: str, language: str = 'en-US') -> Tuple[bool, str]:
        """
        Process audio file from disk
        
        Args:
            audio_file_path: Path to audio file
            language: Language code
        
        Returns:
            Tuple of (success: bool, text: str)
        """
        try:
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            return self.speech_to_text(audio_bytes, language)
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return False, f"Error processing audio: {str(e)}"
    
    def generate_voice_output(self, text: str, output_path: Optional[str] = None, 
                            output_format: str = 'wav') -> Tuple[bool, Optional[str], bytes]:
        """
        Generate voice output from text
        
        Args:
            text: Text to convert
            output_path: Optional path to save audio file
            output_format: Output format ('wav' or 'mp3')
        
        Returns:
            Tuple of (success: bool, file_path: str or None, audio_bytes: bytes)
        """
        success, audio_bytes = self.text_to_speech(text, output_format)
        
        if success and output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"Voice output saved to {output_path}")
                return True, output_path, audio_bytes
            except Exception as e:
                logger.error(f"Failed to save audio file: {str(e)}")
                return True, None, audio_bytes
        
        return success, None, audio_bytes
    
    def get_audio_duration(self, audio_bytes: bytes) -> float:
        """
        Get duration of audio in seconds
        
        Args:
            audio_bytes: Audio file bytes
        
        Returns:
            Duration in seconds
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return len(audio) / 1000.0
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return 0.0


# Singleton instance
_voice_assistant_instance = None

def get_voice_assistant() -> VoiceAssistant:
    """Get or create voice assistant instance"""
    global _voice_assistant_instance
    if _voice_assistant_instance is None:
        _voice_assistant_instance = VoiceAssistant()
    return _voice_assistant_instance
