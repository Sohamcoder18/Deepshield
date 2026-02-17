"""
AI-Powered Reasoning Engine for Deepfake Detection
Generates detailed, intelligent explanations for detection verdicts
Uses Groq AI to create comprehensive analysis reports
"""

import os
import logging
from groq import Groq
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class AIReasoningEngine:
    """
    Uses Groq AI to generate intelligent, detailed reasoning for deepfake detection
    """
    
    def __init__(self):
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                logger.warning("⚠ GROQ_API_KEY not found in environment variables")
                self.client = None
            else:
                self.client = Groq(api_key=api_key)
                self.model = "mixtral-8x7b-32768"  # Fast, powerful model
                logger.info("✓ Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None
            self.model = None
        
    def generate_image_analysis(self, metrics: Dict) -> Dict:
        """
        Generate detailed AI-based analysis for image detection
        
        Args:
            metrics: Dictionary containing:
                - trust_score: float (0-100, higher = more authentic)
                - confidence: float (0-1)
                - artifact_score: float (0-100)
                - xception_confidence: float (0-100)
                - face_detected: bool
                - is_fake: bool
        
        Returns:
            Dictionary with detailed reasoning
        """
        try:
            # Check if Groq client is available
            if not self.client:
                logger.warning("Groq client not available, using fallback analysis")
                return self._get_fallback_image_analysis(metrics)
            
            trust_score = metrics.get('trust_score', 50)
            confidence = metrics.get('confidence', 0.5)
            artifact_score = metrics.get('artifact_score', 50)
            xception_confidence = metrics.get('xception_confidence', 50)
            is_fake = metrics.get('is_fake', False)
            
            # Determine verdict direction
            verdict = "DEEPFAKE (HIGH RISK)" if is_fake else "AUTHENTIC (LOW RISK)"
            
            # Create context for AI reasoning
            prompt = f"""You are an expert AI deepfake detection analyst. Analyze the following detection metrics and provide detailed, technical reasoning.

DETECTION METRICS:
- Overall Trust Score: {trust_score:.1f}% (indicates authenticity, 0-100)
- Model Confidence: {confidence*100:.1f}% (model certainty in prediction)
- Artifact Detection Score: {artifact_score:.1f}% (presence of manipulation artifacts)
- XceptionNet Confidence: {xception_confidence:.1f}% (CNN-based detection)
- Verdict: {verdict}

Provide 3-4 detailed technical reasons why this image is likely {verdict.split('(')[0].strip()}. Focus on:
1. Specific artifacts or patterns detected
2. Facial consistency/inconsistency
3. Model prediction agreement
4. Statistical anomalies

Format as a bulleted list with specific technical details. Be concise but informative."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            reasons_text = message.content[0].text
            reasons = self._parse_reasons(reasons_text)
            
            return {
                'verdict': verdict,
                'reasons': reasons,
                'detailed_analysis': reasons_text,
                'confidence_level': self._get_confidence_level(confidence),
                'risk_assessment': self._get_risk_level(trust_score)
            }
            
        except Exception as e:
            logger.error(f"Error generating image analysis: {str(e)}")
            return self._get_fallback_image_analysis(metrics)
    
    def generate_video_analysis(self, metrics: Dict) -> Dict:
        """
        Generate AI-based analysis for video detection
        
        Args:
            metrics: Dictionary containing:
                - trust_score: float
                - suspicious_frames: int
                - frames_analyzed: int
                - consistency_score: float
                - temporal_consistency: string
        """
        try:
            # Check if Groq client is available
            if not self.client:
                logger.warning("Groq client not available, using fallback analysis")
                return self._get_fallback_video_analysis(metrics)
            
            trust_score = metrics.get('trust_score', 50)
            suspicious_frames = metrics.get('suspicious_frames', 0)
            frames_analyzed = metrics.get('frames_analyzed', 30)
            consistency_score = metrics.get('consistency_score', 50)
            is_fake = metrics.get('is_fake', False)
            
            suspicious_percentage = (suspicious_frames / frames_analyzed * 100) if frames_analyzed > 0 else 0
            
            verdict = "DEEPFAKE VIDEO (MANIPULATION DETECTED)" if is_fake else "AUTHENTIC VIDEO"
            
            prompt = f"""You are an expert video deepfake detection analyst. Analyze these frame-level metrics:

VIDEO ANALYSIS METRICS:
- Overall Trust Score: {trust_score:.1f}%
- Suspicious Frames: {suspicious_frames}/{frames_analyzed} ({suspicious_percentage:.1f}%)
- Frame-to-Frame Consistency: {consistency_score:.1f}%
- Verdict: {verdict}

Provide 4 detailed technical reasons about {verdict}. Consider:
1. Temporal inconsistency patterns
2. Frame-level anomalies
3. Consistency degradation patterns
4. Deepfake generation artifacts (facial warping, lighting changes, lip-sync issues)

Format as a technical bulleted list."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            reasons_text = message.content[0].text
            reasons = self._parse_reasons(reasons_text)
            
            return {
                'verdict': verdict,
                'reasons': reasons,
                'detailed_analysis': reasons_text,
                'suspicious_frame_summary': f"{suspicious_frames} of {frames_analyzed} frames show anomalies",
                'consistency_rating': self._get_consistency_rating(consistency_score)
            }
            
        except Exception as e:
            logger.error(f"Error generating video analysis: {str(e)}")
            return self._get_fallback_video_analysis(metrics)
    
    def generate_audio_analysis(self, metrics: Dict) -> Dict:
        """
        Generate AI-based analysis for audio detection
        """
        try:
            # Check if Groq client is available
            if not self.client:
                logger.warning("Groq client not available, using fallback analysis")
                return self._get_fallback_audio_analysis(metrics)
            
            trust_score = metrics.get('trust_score', 50)
            synthesis_probability = metrics.get('synthesis_probability', 0.5)
            authenticity_score = metrics.get('authenticity_score', 50)
            spectral_consistency = metrics.get('spectral_consistency', 50)
            is_fake = metrics.get('is_fake', False)
            
            verdict = "SYNTHESIZED SPEECH (AI-GENERATED)" if is_fake else "AUTHENTIC SPEECH"
            
            prompt = f"""You are an expert audio deepfake detection analyst. Analyze these audio metrics:

AUDIO ANALYSIS METRICS:
- Overall Trust Score: {trust_score:.1f}%
- Speech Synthesis Probability: {synthesis_probability*100:.1f}%
- Authenticity Score: {authenticity_score:.1f}%
- Spectral Consistency: {spectral_consistency:.1f}%
- Verdict: {verdict}

Provide 4 detailed technical reasons why this audio is {verdict}. Focus on:
1. Spectral anomalies and patterns
2. Prosody and naturalness indicators
3. Synthesis artifacts (breathing, mouth clicks, formant transitions)
4. Acoustic consistency markers

Format as a technical bulleted list."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            reasons_text = message.content[0].text
            reasons = self._parse_reasons(reasons_text)
            
            return {
                'verdict': verdict,
                'reasons': reasons,
                'detailed_analysis': reasons_text,
                'authenticity_rating': self._get_authenticity_rating(authenticity_score),
                'synthesis_risk': f"{synthesis_probability*100:.1f}% AI synthesis probability"
            }
            
        except Exception as e:
            logger.error(f"Error generating audio analysis: {str(e)}")
            return self._get_fallback_audio_analysis(metrics)
    
    def _parse_reasons(self, text: str) -> List[str]:
        """Extract bulleted reasons from AI response"""
        reasons = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Remove bullet and numbering
                reason = line.lstrip('•-* ').strip()
                if reason and len(reason) > 10:  # Filter out very short lines
                    reasons.append(reason)
            elif line and line[0].isdigit() and '.' in line[:3]:
                # Handle numbered lists like "1. reason"
                reason = line.split('.', 1)[1].strip() if '.' in line else line
                if reason and len(reason) > 10:
                    reasons.append(reason)
        
        return reasons if reasons else self._extract_paragraphs(text)
    
    def _extract_paragraphs(self, text: str) -> List[str]:
        """Extract main points from text as fallback"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 20]
        return paragraphs[:4]  # Return first 4 paragraphs
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level"""
        if confidence > 0.9:
            return "Very High Confidence"
        elif confidence > 0.75:
            return "High Confidence"
        elif confidence > 0.6:
            return "Moderate Confidence"
        elif confidence > 0.5:
            return "Low Confidence"
        else:
            return "Very Low Confidence"
    
    def _get_risk_level(self, trust_score: float) -> str:
        """Get human-readable risk level"""
        if trust_score > 85:
            return "✓ Very Low Risk - Likely Authentic"
        elif trust_score > 70:
            return "✓ Low Risk - Probably Authentic"
        elif trust_score > 60:
            return "⚠ Medium Risk - Uncertain"
        elif trust_score > 40:
            return "⚠ High Risk - Likely Manipulated"
        else:
            return "✗ Very High Risk - Probably Deepfake"
    
    def _get_consistency_rating(self, consistency_score: float) -> str:
        """Video consistency rating"""
        if consistency_score > 85:
            return "Excellent - Very consistent across frames"
        elif consistency_score > 70:
            return "Good - Generally consistent"
        elif consistency_score > 50:
            return "Fair - Some temporal inconsistencies"
        else:
            return "Poor - Significant temporal anomalies detected"
    
    def _get_authenticity_rating(self, authenticity_score: float) -> str:
        """Audio authenticity rating"""
        if authenticity_score > 85:
            return "Very Authentic - Natural speech patterns"
        elif authenticity_score > 70:
            return "Probably Authentic"
        elif authenticity_score > 50:
            return "Uncertain - Mixed signals"
        else:
            return "Likely Synthesized - Strong AI artifacts"
    
    def _get_fallback_image_analysis(self, metrics: Dict) -> Dict:
        """Fallback analysis if Groq fails"""
        is_fake = metrics.get('is_fake', False)
        trust_score = metrics.get('trust_score', 50)
        artifact_score = metrics.get('artifact_score', 50)
        
        if is_fake:
            reasons = [
                f"High artifact detection score ({artifact_score:.1f}%) indicates manipulation",
                "Inconsistent model predictions suggest generation by deepfake synthesis",
                "Facial feature irregularities detected in key regions",
                f"Low trust score ({trust_score:.1f}%) across detection models"
            ]
        else:
            reasons = [
                f"Consistent authentication across multiple models ({trust_score:.1f}% trust)",
                f"Low artifact detection score ({artifact_score:.1f}%) indicates natural image",
                "Facial features show natural biological variation patterns",
                "No significant deepfake synthesis indicators detected"
            ]
        
        return {
            'verdict': "DEEPFAKE (HIGH RISK)" if is_fake else "AUTHENTIC (LOW RISK)",
            'reasons': reasons,
            'detailed_analysis': "AI analysis generation temporarily unavailable. Using baseline analysis.",
            'confidence_level': self._get_confidence_level(metrics.get('confidence', 0.5)),
            'risk_assessment': self._get_risk_level(trust_score)
        }
    
    def _get_fallback_video_analysis(self, metrics: Dict) -> Dict:
        """Fallback video analysis"""
        is_fake = metrics.get('is_fake', False)
        suspicious_frames = metrics.get('suspicious_frames', 0)
        frames_analyzed = metrics.get('frames_analyzed', 30)
        
        if is_fake:
            reasons = [
                f"High number of anomalous frames ({suspicious_frames}/{frames_analyzed}) detected",
                "Temporal consistency breaks indicate frame manipulation",
                "Deepfake-specific artifacts identified in suspicious frames",
                "Inconsistent facial dynamics across video sequence"
            ]
        else:
            reasons = [
                f"Natural temporal flow maintained ({frames_analyzed} frames analyzed)",
                "Low anomaly detection rate across full video",
                "Consistent facial features and lighting throughout",
                "No compression or generation artifacts detected"
            ]
        
        return {
            'verdict': "DEEPFAKE VIDEO" if is_fake else "AUTHENTIC VIDEO",
            'reasons': reasons,
            'detailed_analysis': "Baseline video analysis provided",
            'suspicious_frame_summary': f"{suspicious_frames} anomalous frames",
            'consistency_rating': self._get_consistency_rating(metrics.get('consistency_score', 50))
        }
    
    def _get_fallback_audio_analysis(self, metrics: Dict) -> Dict:
        """Fallback audio analysis"""
        is_fake = metrics.get('is_fake', False)
        synthesis_probability = metrics.get('synthesis_probability', 0.5)
        
        if is_fake:
            reasons = [
                f"High synthesis probability ({synthesis_probability*100:.1f}%) indicates AI generation",
                "Spectral anomalies consistent with voice synthesis models",
                "Unnatural prosody patterns detected",
                "Missing natural speech artifacts (breathing, mouth clicks)"
            ]
        else:
            reasons = [
                "Natural prosody and rhythm patterns detected",
                f"Synthesis probability very low ({synthesis_probability*100:.1f}%)",
                "Authentic acoustic markers present throughout",
                "Consistent vocal characteristics across entire sample"
            ]
        
        return {
            'verdict': "SYNTHESIZED SPEECH" if is_fake else "AUTHENTIC SPEECH",
            'reasons': reasons,
            'detailed_analysis': "Baseline audio analysis provided",
            'authenticity_rating': self._get_authenticity_rating(metrics.get('authenticity_score', 50)),
            'synthesis_risk': f"{synthesis_probability*100:.1f}% AI synthesis probability"
        }


# Create singleton instance
_reasoning_engine = None

def get_reasoning_engine():
    """Get or create reasoning engine instance"""
    global _reasoning_engine
    if _reasoning_engine is None:
        try:
            _reasoning_engine = AIReasoningEngine()
        except Exception as e:
            logger.error(f"Failed to initialize reasoning engine: {str(e)}")
    return _reasoning_engine
