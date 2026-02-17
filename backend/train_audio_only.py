"""
Standalone Audio Model Training Script
Trains audio deepfake detection model independently
"""

import os
import sys
import numpy as np
import librosa
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
from tqdm import tqdm
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import subprocess
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioDataProcessor:
    def __init__(self, dataset_root, n_mfcc=40, sr=22050):
        """Initialize audio data processor"""
        # Convert to absolute path
        dataset_path = Path(dataset_root).resolve()
        if not dataset_path.exists():
            # Try from current directory
            alt_path = Path.cwd() / dataset_root
            if alt_path.exists():
                dataset_path = alt_path.resolve()
            else:
                # Try parent directory
                alt_path = Path.cwd().parent / dataset_root
                if alt_path.exists():
                    dataset_path = alt_path.resolve()
        logger.info(f"Dataset root: {dataset_path}")
        self.dataset_root = dataset_path
        self.n_mfcc = n_mfcc
        self.sr = sr
        self.data = []
        self.labels = []
        
    def extract_mfcc(self, audio_path):
        """Extract MFCC features from audio"""
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=self.sr)
            
            # Extract MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            
            # Calculate statistics
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            mfcc_delta = librosa.feature.delta(mfcc)
            mfcc_delta_mean = np.mean(mfcc_delta, axis=1)
            
            # Combine features
            features = np.concatenate([mfcc_mean, mfcc_std, mfcc_delta_mean])
            
            return features
        except Exception as e:
            logger.warning(f"Error extracting MFCC from {audio_path}: {str(e)}")
            return None
    
    def extract_audio_from_video(self, video_path):
        """Extract audio from video file using FFmpeg"""
        try:
            audio_path = str(video_path).replace('.mp4', '_audio.wav')
            
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-q:a', '9', '-n',
                audio_path
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=30)
            
            if os.path.exists(audio_path):
                return audio_path
            else:
                return None
        except Exception as e:
            logger.warning(f"Error extracting audio from {video_path}: {str(e)}")
            return None
    
    def process_video(self, video_path, label):
        """Process video: extract audio and MFCC features"""
        audio_path = self.extract_audio_from_video(video_path)
        
        if audio_path is None:
            return False
        
        try:
            features = self.extract_mfcc(audio_path)
            
            if features is not None:
                self.data.append(features)
                self.labels.append(label)
                
                # Clean up temp audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                return True
        except Exception as e:
            logger.warning(f"Error processing audio: {str(e)}")
        
        return False
    
    def load_dataset(self, real_dir, fake_dirs, max_samples=None):
        """Load entire dataset from directory structure"""
        logger.info("Loading audio dataset...")
        
        # Process real videos (label: 0)
        logger.info(f"Processing real videos from: {real_dir}")
        real_path = self.dataset_root / real_dir
        real_count = 0
        
        if real_path.exists():
            video_files = sorted(real_path.glob("*.mp4"))[:100]
            for video_file in tqdm(video_files, desc="Real videos"):
                if self.process_video(str(video_file), label=0):
                    real_count += 1
            logger.info(f"Processed {real_count} real videos")
        
        # Process fake videos (label: 1)
        for fake_dir in fake_dirs:
            logger.info(f"Processing fake videos from: {fake_dir}")
            fake_path = self.dataset_root / fake_dir
            fake_count = 0
            
            if fake_path.exists():
                video_files = sorted(fake_path.glob("*.mp4"))[:50]
                for video_file in tqdm(video_files, desc=f"Fake - {fake_dir}"):
                    if self.process_video(str(video_file), label=1):
                        fake_count += 1
                logger.info(f"Processed {fake_count} fake videos from {fake_dir}")
        
        X = np.array(self.data)
        y = np.array(self.labels)
        
        logger.info(f"Dataset shape: {X.shape}")
        logger.info(f"Labels distribution - Real: {np.sum(y == 0)}, Fake: {np.sum(y == 1)}")
        
        return X, y


class AudioDetectionModelTrainer:
    def __init__(self):
        """Initialize model trainer"""
        self.model = None
        self.history = None
    
    def build_model(self, input_dim=120):
        """Build MLP model for audio detection"""
        logger.info("Building audio detection model...")
        
        self.model = Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        logger.info("Model built successfully")
        return self.model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=30, batch_size=32):
        """Train the model with class weights"""
        logger.info("Starting model training...")
        
        # Calculate class weights
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weight_dict = dict(enumerate(class_weights))
        logger.info(f"Class weights: {class_weight_dict}")
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                filepath='models/audio_model_checkpoint.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            class_weight=class_weight_dict,
            verbose=1
        )
        
        logger.info("Training completed")
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        logger.info("Evaluating model...")
        
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        y_test_flat = y_test.flatten()
        
        accuracy = accuracy_score(y_test_flat, y_pred)
        precision = precision_score(y_test_flat, y_pred, zero_division=0)
        recall = recall_score(y_test_flat, y_pred, zero_division=0)
        f1 = f1_score(y_test_flat, y_pred, zero_division=0)
        auc = roc_auc_score(y_test_flat, y_pred_proba)
        cm = confusion_matrix(y_test_flat, y_pred)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'auc': float(auc),
            'confusion_matrix': cm.tolist()
        }
        
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1-Score: {f1:.4f}")
        logger.info(f"AUC-ROC: {auc:.4f}")
        
        return metrics
    
    def save_model(self, filepath):
        """Save trained model"""
        if self.model:
            self.model.save(filepath)
            logger.info(f"Model saved to {filepath}")
    
    def plot_training_history(self, save_path='models/audio_training_history.png'):
        """Plot training history"""
        if self.history is None:
            logger.warning("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        axes[0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        axes[1].plot(self.history.history['loss'], label='Train Loss')
        axes[1].plot(self.history.history['val_loss'], label='Val Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        logger.info(f"Training history saved to {save_path}")


def main():
    """Main training function"""
    logger.info("=" * 70)
    logger.info("AUDIO MODEL TRAINING - STANDALONE")
    logger.info("=" * 70)
    
    try:
        # Create models directory
        Path('models').mkdir(exist_ok=True)
        
        # Initialize processor
        dataset_root = '../dataset'
        processor = AudioDataProcessor(dataset_root, n_mfcc=40, sr=22050)
        
        # Load dataset
        fake_dirs = ['Deepfakes', 'Face2Face', 'FaceShifter', 'FaceSwap']
        X, y = processor.load_dataset('DeepFakeDetection', fake_dirs)
        
        if len(X) == 0:
            logger.error("No data loaded!")
            return False
        
        # Split dataset
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.4, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        logger.info(f"Train set: {X_train.shape}")
        logger.info(f"Val set: {X_val.shape}")
        logger.info(f"Test set: {X_test.shape}")
        
        # Build and train model
        trainer = AudioDetectionModelTrainer()
        trainer.build_model(input_dim=X_train.shape[1])
        trainer.train(X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
        
        # Evaluate model
        metrics = trainer.evaluate(X_test, y_test)
        
        # Save model and metrics
        trainer.save_model('models/audio_model.h5')
        trainer.plot_training_history()
        
        # Save metrics to JSON
        with open('models/audio_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=4)
        
        logger.info("=" * 70)
        logger.info("AUDIO MODEL TRAINING COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        return True
    
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
