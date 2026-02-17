"""
Master Training Pipeline - Trains all deepfake detection models
Orchestrates training of video, image, and audio models
"""

import os
import sys
import logging
from pathlib import Path
import json
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrainingOrchestrator:
    def __init__(self, backend_dir="."):
        """Initialize training orchestrator"""
        self.backend_dir = Path(backend_dir)
        self.models_dir = self.backend_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        self.training_report = {
            'start_time': datetime.now().isoformat(),
            'models': {}
        }
        
    def train_video_model(self):
        """Train video detection model"""
        logger.info("=" * 70)
        logger.info("STARTING VIDEO MODEL TRAINING")
        logger.info("=" * 70)
        
        try:
            script_path = self.backend_dir / "train_video_model.py"
            
            if not script_path.exists():
                logger.error(f"Training script not found: {script_path}")
                return False
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.backend_dir),
                capture_output=True,
                text=True,
                timeout=21600  # 6 hour timeout for video model
            )
            
            logger.info("STDOUT:\n" + result.stdout)
            if result.stderr:
                logger.warning("STDERR:\n" + result.stderr)
            
            if result.returncode == 0:
                logger.info("Video model training completed successfully!")
                self.training_report['models']['video'] = {
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat()
                }
                return True
            else:
                logger.error("Video model training failed!")
                self.training_report['models']['video'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Video model training timed out!")
            self.training_report['models']['video'] = {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            logger.error(f"Video model training error: {str(e)}")
            self.training_report['models']['video'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def train_image_model(self):
        """Train image detection model"""
        logger.info("=" * 70)
        logger.info("STARTING IMAGE MODEL TRAINING")
        logger.info("=" * 70)
        
        try:
            script_path = self.backend_dir / "train_image_model.py"
            
            if not script_path.exists():
                logger.error(f"Training script not found: {script_path}")
                return False
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.backend_dir),
                capture_output=True,
                text=True,
                timeout=21600  # 6 hour timeout for image model
            )
            
            logger.info("STDOUT:\n" + result.stdout)
            if result.stderr:
                logger.warning("STDERR:\n" + result.stderr)
            
            if result.returncode == 0:
                logger.info("Image model training completed successfully!")
                self.training_report['models']['image'] = {
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat()
                }
                return True
            else:
                logger.error("Image model training failed!")
                self.training_report['models']['image'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Image model training timed out!")
            self.training_report['models']['image'] = {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            logger.error(f"Image model training error: {str(e)}")
            self.training_report['models']['image'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def train_audio_model(self):
        """Train audio detection model"""
        logger.info("=" * 70)
        logger.info("STARTING AUDIO MODEL TRAINING")
        logger.info("=" * 70)
        
        try:
            script_path = self.backend_dir / "train_audio_model.py"
            
            if not script_path.exists():
                logger.error(f"Training script not found: {script_path}")
                return False
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.backend_dir),
                capture_output=True,
                text=True,
                timeout=21600  # 6 hour timeout for audio model
            )
            
            logger.info("STDOUT:\n" + result.stdout)
            if result.stderr:
                logger.warning("STDERR:\n" + result.stderr)
            
            if result.returncode == 0:
                logger.info("Audio model training completed successfully!")
                self.training_report['models']['audio'] = {
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat()
                }
                return True
            else:
                logger.error("Audio model training failed!")
                self.training_report['models']['audio'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Audio model training timed out!")
            self.training_report['models']['audio'] = {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            logger.error(f"Audio model training error: {str(e)}")
            self.training_report['models']['audio'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def verify_trained_models(self):
        """Verify that all models were trained successfully"""
        logger.info("=" * 70)
        logger.info("VERIFYING TRAINED MODELS")
        logger.info("=" * 70)
        
        required_files = [
            'xceptionnet_model.h5',
            'efficientnet_model.h5',
            'audio_model.h5'
        ]
        
        results = {}
        for filename in required_files:
            filepath = self.models_dir / filename
            exists = filepath.exists()
            results[filename] = exists
            
            status = "[FOUND]" if exists else "[MISSING]"
            logger.info(f"{status}: {filename}")
        
        return all(results.values())
    
    def load_training_metrics(self):
        """Load and display training metrics from all models"""
        logger.info("=" * 70)
        logger.info("TRAINING METRICS SUMMARY")
        logger.info("=" * 70)
        
        metric_files = [
            ('video_metrics.json', 'Video Model'),
            ('image_metrics.json', 'Image Model'),
            ('audio_metrics.json', 'Audio Model')
        ]
        
        for filename, model_name in metric_files:
            filepath = self.models_dir / filename
            
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        metrics = json.load(f)
                    
                    logger.info(f"\n{model_name} Metrics:")
                    logger.info(f"  Accuracy: {metrics.get('accuracy', 'N/A'):.4f}")
                    logger.info(f"  Precision: {metrics.get('precision', 'N/A'):.4f}")
                    logger.info(f"  Recall: {metrics.get('recall', 'N/A'):.4f}")
                    logger.info(f"  F1-Score: {metrics.get('f1', 'N/A'):.4f}")
                    logger.info(f"  AUC-ROC: {metrics.get('auc', 'N/A'):.4f}")
                except Exception as e:
                    logger.warning(f"Could not load metrics from {filename}: {str(e)}")
            else:
                logger.warning(f"Metrics file not found: {filename}")
    
    def save_training_report(self):
        """Save training report"""
        self.training_report['end_time'] = datetime.now().isoformat()
        self.training_report['models_verified'] = self.verify_trained_models()
        
        report_path = self.backend_dir / "training_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.training_report, f, indent=2)
        
        logger.info(f"\nTraining report saved to: {report_path}")
    
    def run_complete_pipeline(self, skip_video=False, skip_image=False, skip_audio=False):
        """Run complete training pipeline"""
        logger.info("\n" + "=" * 70)
        logger.info("DEEPFAKE DETECTION MODEL TRAINING PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Start Time: {datetime.now()}\n")
        
        results = {
            'video': True,
            'image': True,
            'audio': True
        }
        
        # Train models
        if not skip_video:
            results['video'] = self.train_video_model()
        
        if not skip_image:
            results['image'] = self.train_image_model()
        
        if not skip_audio:
            results['audio'] = self.train_audio_model()
        
        # Verify and report
        logger.info("\n" + "=" * 70)
        logger.info("TRAINING PIPELINE SUMMARY")
        logger.info("=" * 70)
        
        for model_type, success in results.items():
            status = "[OK]" if success else "[FAILED]"
            logger.info(f"{status}: {model_type.upper()} model")
        
        # Verify models
        self.verify_trained_models()
        
        # Load and display metrics
        self.load_training_metrics()
        
        # Save report
        self.save_training_report()
        
        logger.info("\n" + "=" * 70)
        logger.info("TRAINING PIPELINE COMPLETED")
        logger.info("=" * 70 + "\n")
        
        return all(results.values())


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Train deepfake detection models'
    )
    parser.add_argument('--skip-video', action='store_true', help='Skip video model training')
    parser.add_argument('--skip-image', action='store_true', help='Skip image model training')
    parser.add_argument('--skip-audio', action='store_true', help='Skip audio model training')
    parser.add_argument('--backend-dir', default='.', help='Backend directory path')
    
    args = parser.parse_args()
    
    orchestrator = TrainingOrchestrator(backend_dir=args.backend_dir)
    success = orchestrator.run_complete_pipeline(
        skip_video=args.skip_video,
        skip_image=args.skip_image,
        skip_audio=args.skip_audio
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
