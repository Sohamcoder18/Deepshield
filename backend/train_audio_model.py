"""
Audio Deepfake Detection Model Training Script
Trains audio deepfake detection model using MFCC features
"""

import os
import numpy as np
import librosa
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
from tqdm import tqdm
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import soundfile as sf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioDataProcessor:
    def __init__(self, dataset_root, n_mfcc=40, sr=22050):
        """
        Initialize audio data processor
        
        Args:
            dataset_root: Root directory of dataset
            n_mfcc: Number of MFCC coefficients
            sr: Sample rate
        """
        # Convert to absolute path - handle relative paths correctly
        dataset_path = Path(dataset_root)
        if not dataset_path.is_absolute():
            # Resolve relative paths from current working directory
            dataset_path = (Path.cwd() / dataset_path).resolve()
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
            
            # Calculate statistics over time
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
        """Extract audio from video file"""
        try:
            import subprocess
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
    
    def load_dataset(self, real_dir, fake_dirs):
        """Load entire dataset from directory structure"""
        logger.info("Loading audio dataset...")
        
        # Process real videos (label: 1)
        logger.info(f"Processing real videos from: {real_dir}")
        real_path = self.dataset_root / real_dir
        video_count = 0
        
        if real_path.exists():
            video_files = sorted(real_path.glob("*.mp4"))[:100]
            for video_file in tqdm(video_files):
                if self.process_video(str(video_file), label=1):
                    video_count += 1
            logger.info(f"Processed {video_count} real videos")
        
        # Process fake videos (label: 0)
        for fake_dir in fake_dirs:
            logger.info(f"Processing fake videos from: {fake_dir}")
            fake_path = self.dataset_root / fake_dir
            video_count = 0
            
            if fake_path.exists():
                video_files = sorted(fake_path.glob("*.mp4"))[:50]
                for video_file in tqdm(video_files):
                    if self.process_video(str(video_file), label=0):
                        video_count += 1
                logger.info(f"Processed {video_count} fake videos from {fake_dir}")
        
        logger.info(f"Total audio samples collected: {len(self.data)}")
        
        if len(self.data) == 0:
            logger.error("No data loaded!")
            return None, None
        
        return np.array(self.data), np.array(self.labels)


class AudioDetectionModelTrainer:
    def __init__(self, input_shape=(120,)):
        """Initialize model trainer"""
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build neural network for audio deepfake detection"""
        logger.info("Building audio detection model...")
        
        self.model = Sequential([
            layers.Input(shape=self.input_shape),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        logger.info("Model built successfully")
        self.model.summary()
        
        return self.model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train the model"""
        logger.info("Starting model training...")
        
        # Calculate class weights to handle imbalance
        from sklearn.utils.class_weight import compute_class_weight
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
        
        # Train model with class weights
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
        
        # Get predictions
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        y_test_flat = y_test.flatten()
        
        # Calculate metrics
        accuracy = accuracy_score(y_test_flat, y_pred)
        precision = precision_score(y_test_flat, y_pred)
        recall = recall_score(y_test_flat, y_pred)
        f1 = f1_score(y_test_flat, y_pred)
        auc = roc_auc_score(y_test_flat, y_pred_proba)
        cm = confusion_matrix(y_test_flat, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc,
            'confusion_matrix': cm
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
    
    def plot_training_history(self, save_path='training_history.png'):
        """Plot training history"""
        if self.history is None:
            logger.warning("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
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
    """Main training pipeline"""
    
    # Use absolute path from script location
    script_dir = Path(__file__).parent  # D:\hackethon\backend
    dataset_root = (script_dir.parent / "dataset").resolve()  # D:\hackethon\dataset
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Initialize data processor
    logger.info("=" * 50)
    logger.info("AUDIO MODEL TRAINING PIPELINE")
    logger.info("=" * 50)
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Dataset root (absolute): {dataset_root}")
    
    processor = AudioDataProcessor(dataset_root, n_mfcc=40)
    
    # Load dataset
    X, y = processor.load_dataset(
        real_dir="DeepFakeDetection",
        fake_dirs=["Deepfakes", "Face2Face", "FaceShifter"]
    )
    
    if X is None or len(X) == 0:
        logger.error("Failed to load dataset")
        return
    
    logger.info(f"Dataset shape: {X.shape}")
    logger.info(f"Labels distribution - Real: {np.sum(y)}, Fake: {len(y) - np.sum(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    logger.info(f"Train set: {X_train.shape}")
    logger.info(f"Val set: {X_val.shape}")
    logger.info(f"Test set: {X_test.shape}")
    
    # Build and train model
    trainer = AudioDetectionModelTrainer(input_shape=(X_train.shape[1],))
    trainer.build_model()
    
    trainer.train(
        X_train, y_train,
        X_val, y_val,
        epochs=30,
        batch_size=32
    )
    
    # Evaluate model
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model(str(models_dir / "audio_model.h5"))
    trainer.plot_training_history(str(models_dir / "audio_training_history.png"))
    
    # Save metrics
    import json
    with open(str(models_dir / "audio_metrics.json"), 'w') as f:
        metrics_to_save = metrics.copy()
        metrics_to_save['confusion_matrix'] = metrics_to_save['confusion_matrix'].tolist()
        json.dump(metrics_to_save, f, indent=2)
    
    logger.info("Audio model training completed!")


if __name__ == "__main__":
    main()
