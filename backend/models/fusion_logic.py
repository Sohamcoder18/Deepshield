import numpy as np
import logging

logger = logging.getLogger(__name__)

class FusionLogic:
    def __init__(self, image_weight=0.35, video_weight=0.35, audio_weight=0.30):
        """
        Initialize Fusion Logic with weighted combination
        
        Args:
            image_weight: Weight for image analysis (0-1)
            video_weight: Weight for video analysis (0-1)
            audio_weight: Weight for audio analysis (0-1)
        """
        # Normalize weights
        total = image_weight + video_weight + audio_weight
        self.weights = {
            'image': image_weight / total,
            'video': video_weight / total,
            'audio': audio_weight / total
        }
        
        logger.info(f"Fusion weights initialized: {self.weights}")
    
    def fuse_results(self, image_score=None, video_score=None, audio_score=None):
        """
        Combine detection results using weighted fusion
        
        Args:
            image_score: Trust score from image analysis (0-100)
            video_score: Trust score from video analysis (0-100)
            audio_score: Trust score from audio analysis (0-100)
            
        Returns:
            Dictionary with fused results
        """
        try:
            scores = {}
            weights_applied = {}
            weighted_sum = 0
            weight_sum = 0
            
            # Image score
            if image_score is not None and 0 <= image_score <= 100:
                scores['image'] = image_score / 100.0  # Normalize to 0-1
                weights_applied['image'] = self.weights['image']
                weighted_sum += (image_score / 100.0) * self.weights['image']
                weight_sum += self.weights['image']
            
            # Video score
            if video_score is not None and 0 <= video_score <= 100:
                scores['video'] = video_score / 100.0
                weights_applied['video'] = self.weights['video']
                weighted_sum += (video_score / 100.0) * self.weights['video']
                weight_sum += self.weights['video']
            
            # Audio score
            if audio_score is not None and 0 <= audio_score <= 100:
                scores['audio'] = audio_score / 100.0
                weights_applied['audio'] = self.weights['audio']
                weighted_sum += (audio_score / 100.0) * self.weights['audio']
                weight_sum += self.weights['audio']
            
            # Normalize by applied weights
            if weight_sum > 0:
                fused_score_normalized = weighted_sum / weight_sum
            else:
                fused_score_normalized = 0.5  # Default if no scores provided
            
            # Convert back to 0-100 scale
            fused_trust_score = fused_score_normalized * 100
            
            # Determine verdict
            is_fake = fused_score_normalized < 0.5
            confidence = max(fused_score_normalized, 1 - fused_score_normalized)
            
            # Generate recommendation
            if is_fake:
                verdict = 'LIKELY DEEPFAKE'
                recommendation = f"Combined analysis indicates potential deepfake content. Review all detection modules carefully."
            else:
                verdict = 'AUTHENTIC'
                recommendation = f"Multi-modal analysis indicates authentic content."
            
            result = {
                'trust_score': float(fused_trust_score),
                'verdict': verdict,
                'confidence': float(confidence),
                'is_fake': bool(is_fake),
                'individual_scores': {
                    'image': float(image_score) if image_score is not None else None,
                    'video': float(video_score) if video_score is not None else None,
                    'audio': float(audio_score) if audio_score is not None else None
                },
                'weights': {
                    'image': float(weights_applied.get('image', self.weights['image'])),
                    'video': float(weights_applied.get('video', self.weights['video'])),
                    'audio': float(weights_applied.get('audio', self.weights['audio']))
                },
                'recommendation': recommendation
            }
            
            logger.info(f"Fusion result: {verdict} (confidence: {confidence*100:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Fusion error: {str(e)}")
            return {
                'trust_score': 50.0,
                'verdict': 'INCONCLUSIVE',
                'confidence': 0.5,
                'is_fake': False,
                'individual_scores': {
                    'image': image_score,
                    'video': video_score,
                    'audio': audio_score
                },
                'weights': self.weights,
                'recommendation': f'Error during fusion: {str(e)}'
            }
    
    def adjust_weights(self, image_weight=None, video_weight=None, audio_weight=None):
        """
        Adjust fusion weights dynamically
        
        Args:
            image_weight: New weight for image analysis
            video_weight: New weight for video analysis
            audio_weight: New weight for audio analysis
        """
        try:
            if image_weight is not None:
                self.weights['image'] = image_weight
            if video_weight is not None:
                self.weights['video'] = video_weight
            if audio_weight is not None:
                self.weights['audio'] = audio_weight
            
            # Normalize weights
            total = sum(self.weights.values())
            for key in self.weights:
                self.weights[key] /= total
            
            logger.info(f"Weights adjusted: {self.weights}")
            
        except Exception as e:
            logger.error(f"Weight adjustment error: {str(e)}")
