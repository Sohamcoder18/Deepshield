"""
Standalone Video Model Training Script
Trains XceptionNet model independently
"""

import os
import sys
import numpy as np
import cv2
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from mtcnn import MTCNN
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoDataProcessor:
    def __init__(self, dataset_root, frames_per_video=10, face_size=224):
        """Initialize video data processor"""
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
        self.frames_per_video = frames_per_video
        self.face_size = face_size
        self.mtcnn_detector = MTCNN()
        self.data = []
        self.labels = []
        
    def extract_faces_from_frame(self, frame):
        """Extract face regions from a frame using MTCNN"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = self.mtcnn_detector.detect_faces(frame_rgb)
            
            if detections:
                for detection in detections:
                    x, y, w, h = detection['box']
                    x, y = max(0, x), max(0, y)
                    face = frame[y:y+h, x:x+w]
                    
                    if face.size > 0:
                        face_resized = cv2.resize(face, (self.face_size, self.face_size))
                        return face_resized
            
            frame_resized = cv2.resize(frame, (self.face_size, self.face_size))
            return frame_resized
        except Exception as e:
            logger.warning(f"Error extracting face: {str(e)}")
            return None
    
    def process_video(self, video_path, label):
        """Process video: extract frames and faces"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            frame_count = 0
            extracted_frames = []
            
            while frame_count < self.frames_per_video:
                ret, frame = cap.read()
                if not ret:
                    break
                
                face = self.extract_faces_from_frame(frame)
                if face is not None:
                    face_normalized = face.astype('float32') / 255.0
                    extracted_frames.append(face_normalized)
                    frame_count += 1
            
            cap.release()
            
            if extracted_frames:
                stacked_frames = np.stack(extracted_frames, axis=0)
                self.data.append(stacked_frames)
                self.labels.append(label)
                return True
        except Exception as e:
            logger.warning(f"Error processing video {video_path}: {str(e)}")
        
        return False
    
    def load_dataset(self, real_dir, fake_dirs, max_samples=None):
        """Load entire dataset from directory structure"""
        logger.info("Loading video dataset...")
        
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
                video_files = sorted(fake_path.glob("*.mp4"))[:100]
                for video_file in tqdm(video_files, desc=f"Fake - {fake_dir}"):
                    if self.process_video(str(video_file), label=1):
                        fake_count += 1
                logger.info(f"Processed {fake_count} fake videos from {fake_dir}")
        
        X = np.array(self.data)
        y = np.array(self.labels)
        
        logger.info(f"Dataset shape: {X.shape}")
        logger.info(f"Labels distribution - Real: {np.sum(y == 0)}, Fake: {np.sum(y == 1)}")
        
        return X, y


class VideoDetectionModelTrainer:
    def __init__(self):
        """Initialize model trainer"""
        self.model = None
        self.history = None
    
    def build_xception_model(self):
        """Build 3D CNN model for video with transfer learning"""
        logger.info("Building XceptionNet model for video...")
        
        # Load pretrained Xception
        base_model = keras.applications.Xception(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        base_model.trainable = False
        
        # Build new model
        inputs = keras.Input(shape=(self.frames_per_video, 224, 224, 3))
        
        # Process each frame
        x = layers.TimeDistributed(keras.applications.xception.preprocess_input)(inputs)
        x = layers.TimeDistributed(base_model)(x)
        
        # Global average pooling
        x = layers.TimeDistributed(layers.GlobalAveragePooling2D())(x)
        
        # LSTM layers
        x = layers.LSTM(256, return_sequences=True)(x)
        x = layers.Dropout(0.5)(x)
        x = layers.LSTM(128)(x)
        x = layers.Dropout(0.3)(x)
        
        # Dense layers
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer
        outputs = layers.Dense(1, activation='sigmoid')(x)
        
        self.model = Model(inputs=inputs, outputs=outputs)
        self.frames_per_video = 10
        
        # Compile model
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
                filepath='models/xceptionnet_model_checkpoint.h5',
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
    
    def plot_training_history(self, save_path='models/video_training_history.png'):
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
    logger.info("VIDEO MODEL TRAINING - STANDALONE")
    logger.info("=" * 70)
    
    try:
        # Create models directory
        Path('models').mkdir(exist_ok=True)
        
        # Initialize processor
        dataset_root = '../dataset'
        processor = VideoDataProcessor(dataset_root, frames_per_video=10, face_size=224)
        
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
        trainer = VideoDetectionModelTrainer()
        trainer.build_xception_model()
        trainer.train(X_train, y_train, X_val, y_val, epochs=30, batch_size=32)
        
        # Evaluate model
        metrics = trainer.evaluate(X_test, y_test)
        
        # Save model and metrics
        trainer.save_model('models/xceptionnet_model.h5')
        trainer.plot_training_history()
        
        # Save metrics to JSON
        with open('models/video_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=4)
        
        logger.info("=" * 70)
        logger.info("VIDEO MODEL TRAINING COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        return True
    
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
