"""
Video Deepfake Detection Model Training Script
Trains XceptionNet model on video frame data for deepfake detection
"""

import os
import numpy as np
import cv2
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
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
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoDataProcessor:
    def __init__(self, dataset_root, frames_per_video=15, face_size=224):
        """
        Initialize video data processor
        
        Args:
            dataset_root: Root directory of dataset
            frames_per_video: Number of frames to extract from each video
            face_size: Size to resize detected faces
        """
        # Convert to absolute path - handle relative paths correctly
        dataset_path = Path(dataset_root)
        if not dataset_path.is_absolute():
            # Resolve relative paths from current working directory
            dataset_path = (Path.cwd() / dataset_path).resolve()
        self.dataset_root = dataset_path
        self.frames_per_video = frames_per_video
        self.face_size = face_size
        
        # Initialize face detectors
        logger.info("Initializing face detectors...")
        self.mtcnn_detector = None
        self.use_mtcnn = True
        
        try:
            self.mtcnn_detector = MTCNN()
            logger.info("MTCNN initialized successfully")
        except Exception as e:
            logger.warning(f"MTCNN initialization failed: {e}")
            logger.warning("Will use Haar Cascade fallback only")
            self.use_mtcnn = False
        
        # Load Haar Cascade as primary fallback
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if self.haar_cascade.empty():
            logger.error("Haar Cascade failed to load!")
        
        self.data = []
        self.labels = []
        
    def extract_faces_from_frame(self, frame):
        """Extract face regions from a frame using MTCNN with Haar Cascade fallback"""
        try:
            # Convert BGR to RGB for MTCNN
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            faces = []
            
            # Try MTCNN first if available
            if self.use_mtcnn and self.mtcnn_detector is not None:
                try:
                    detections = self.mtcnn_detector.detect_faces(frame_rgb)
                    
                    for detection in detections:
                        x, y, w, h = detection['box']
                        # Ensure coordinates are within image bounds
                        x = max(0, x)
                        y = max(0, y)
                        w = min(w, frame_rgb.shape[1] - x)
                        h = min(h, frame_rgb.shape[0] - y)
                        
                        if w > 0 and h > 0:
                            face = frame_rgb[y:y+h, x:x+w]
                            if face.size > 0:
                                # Resize to standard size
                                face = cv2.resize(face, (self.face_size, self.face_size))
                                faces.append(face)
                    
                    # If MTCNN found faces, return them
                    if faces:
                        return faces
                except Exception as e:
                    logger.debug(f"MTCNN detection failed: {e}, using Haar Cascade")
            
            # Use Haar Cascade (more reliable) - with multiple scale factors for better coverage
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Try with different parameters to catch more faces
            for scale in [1.05, 1.1, 1.15]:
                haar_faces = self.haar_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=scale,
                    minNeighbors=4, 
                    minSize=(40, 40)
                )
                
                if len(haar_faces) > 0:
                    # Use first detection strategy found
                    for (x, y, w, h) in haar_faces:
                        face = frame_rgb[y:y+h, x:x+w]
                        if face.size > 0:
                            face = cv2.resize(face, (self.face_size, self.face_size))
                            faces.append(face)
                    break  # Exit loop once we find faces
            
            return faces if faces else None
            
        except Exception as e:
            logger.debug(f"Face extraction error: {str(e)}")
            return None
    
    def extract_frames(self, video_path, num_frames=None):
        """Extract evenly spaced frames from video"""
        if num_frames is None:
            num_frames = self.frames_per_video
            
        frames = []
        try:
            # Try with different backends to handle codec issues
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                # Try with FFMPEG backend
                cap = cv2.VideoCapture(str(video_path), cv2.CAP_FFMPEG)
            
            if not cap.isOpened():
                logger.debug(f"Could not open video: {video_path}")
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.debug(f"Video {video_path}: {total_frames} total frames")
            
            if total_frames < num_frames:
                logger.debug(f"Video has fewer frames than requested: {total_frames} < {num_frames}, using all frames")
                num_frames = total_frames
            
            # Calculate frame indices to extract
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    frames.append(frame)
            
            cap.release()
            
            return frames if len(frames) > 0 else None
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {str(e)}")
            return None
    
    def process_video(self, video_path, label):
        """Process single video: extract frames and faces"""
        frames = self.extract_frames(video_path)
        
        if frames is None:
            logger.debug(f"No frames extracted from {video_path}")
            return False
        
        faces_found = 0
        for frame_idx, frame in enumerate(frames):
            faces = self.extract_faces_from_frame(frame)
            
            if faces:
                faces_found += len(faces)
                for face in faces:
                    # Normalize pixel values
                    face_normalized = face.astype(np.float32) / 255.0
                    self.data.append(face_normalized)
                    self.labels.append(label)
        
        if faces_found == 0:
            logger.debug(f"No faces detected in {video_path}")
            return False
            
        logger.debug(f"Extracted {faces_found} faces from {video_path}")
        return True
    
    def load_dataset(self, real_dir, fake_dirs):
        """Load entire dataset from directory structure"""
        logger.info("Loading dataset...")
        logger.info(f"Using face detector: {'MTCNN + Haar Cascade' if self.use_mtcnn else 'Haar Cascade only'}")
        
        # Process real videos (label: 1)
        logger.info(f"Processing real videos from: {real_dir}")
        real_path = self.dataset_root / real_dir
        real_videos_processed = 0
        real_videos_failed = 0
        real_faces_total = 0
        
        if real_path.exists():
            video_files = sorted(real_path.glob("*.mp4"))[:100]  # Limit to 100 for faster processing
            logger.info(f"Found {len(video_files)} real videos to process")
            
            initial_size = len(self.data)
            for video_file in tqdm(video_files, desc="Real videos"):
                if self.process_video(str(video_file), label=1):
                    real_videos_processed += 1
                else:
                    real_videos_failed += 1
            
            real_faces_total = len(self.data) - initial_size
            logger.info(f"Real videos: {real_videos_processed} processed, {real_videos_failed} failed")
            logger.info(f"Real faces extracted: {real_faces_total}")
        
        # Process fake videos (label: 0)
        for fake_dir in fake_dirs:
            logger.info(f"Processing fake videos from: {fake_dir}")
            fake_path = self.dataset_root / fake_dir
            fake_videos_processed = 0
            fake_videos_failed = 0
            
            if fake_path.exists():
                video_files = sorted(fake_path.glob("*.mp4"))[:50]  # Limit to 50 per category
                logger.info(f"Found {len(video_files)} fake videos to process from {fake_dir}")
                
                initial_size = len(self.data)
                for video_file in tqdm(video_files, desc=f"{fake_dir}"):
                    if self.process_video(str(video_file), label=0):
                        fake_videos_processed += 1
                    else:
                        fake_videos_failed += 1
                
                fake_faces_extracted = len(self.data) - initial_size
                logger.info(f"{fake_dir}: {fake_videos_processed} processed, {fake_videos_failed} failed")
                logger.info(f"{fake_dir} faces extracted: {fake_faces_extracted}")
        
        logger.info(f"Total face samples collected: {len(self.data)}")
        logger.info(f"Total labels: {len(self.labels)}")
        
        if len(self.data) == 0:
            logger.error("No data loaded! This usually means:")
            logger.error("  1. Videos cannot be read (codec issue)")
            logger.error("  2. Face detector not finding any faces")
            logger.error("  3. Videos are too low quality or contain no clear faces")
            logger.error("  4. Haar Cascade detector parameters need adjustment")
            return None, None
        
        return np.array(self.data), np.array(self.labels)


class VideoDetectionModelTrainer:
    def __init__(self, input_shape=(224, 224, 3)):
        """Initialize model trainer"""
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_xception_model(self):
        """Build XceptionNet-based model for deepfake detection"""
        logger.info("Building XceptionNet model...")
        
        # Load pretrained XceptionNet
        base_model = keras.applications.Xception(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        inputs = keras.Input(shape=self.input_shape)
        
        # Preprocess input for Xception
        x = keras.applications.xception.preprocess_input(inputs)
        
        # Base model
        x = base_model(x)
        
        # Global average pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer
        outputs = layers.Dense(1, activation='sigmoid')(x)
        
        self.model = Model(inputs=inputs, outputs=outputs)
        
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
                filepath='models/xceptionnet_model_checkpoint.h5',
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
    logger.info("VIDEO MODEL TRAINING PIPELINE")
    logger.info("=" * 50)
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Dataset root (absolute): {dataset_root}")
    
    processor = VideoDataProcessor(dataset_root, frames_per_video=10, face_size=224)
    
    # Load dataset
    logger.info("Loading dataset...")
    
    # Note: The Deepfakes folder has codec issues. We'll use Face2Face, FaceShifter, FaceSwap instead
    X, y = processor.load_dataset(
        real_dir="DeepFakeDetection",
        fake_dirs=["Face2Face", "FaceShifter", "FaceSwap", "NeuralTextures"]  # Skip Deepfakes due to codec issues
    )
    
    if X is None or len(X) == 0:
        logger.error("Failed to load dataset - No face samples extracted")
        logger.error("Possible causes:")
        logger.error("  1. Videos cannot be read (codec issue)")
        logger.error("  2. Face detector not finding any faces")
        logger.error("  3. Videos are too low quality or contain no clear faces")
        logger.error("\nAttempting alternative approach: Using reduced frame requirements...")
        
        # Try again with lower frame requirements
        processor2 = VideoDataProcessor(dataset_root, frames_per_video=3, face_size=224)
        X, y = processor2.load_dataset(
            real_dir="DeepFakeDetection",
            fake_dirs=["Face2Face", "FaceShifter", "FaceSwap", "NeuralTextures"]  # Skip Deepfakes
        )
        
        if X is None or len(X) == 0:
            logger.error("Still no data after retry. Training cannot proceed.")
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
    trainer = VideoDetectionModelTrainer(input_shape=(224, 224, 3))
    trainer.build_xception_model()
    
    trainer.train(
        X_train, y_train,
        X_val, y_val,
        epochs=30,
        batch_size=32
    )
    
    # Evaluate model
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model(str(models_dir / "xceptionnet_model.h5"))
    trainer.plot_training_history(str(models_dir / "video_training_history.png"))
    
    # Save metrics
    import json
    with open(str(models_dir / "video_metrics.json"), 'w') as f:
        metrics_to_save = metrics.copy()
        metrics_to_save['confusion_matrix'] = metrics_to_save['confusion_matrix'].tolist()
        json.dump(metrics_to_save, f, indent=2)
    
    logger.info("Video model training completed!")


if __name__ == "__main__":
    main()
