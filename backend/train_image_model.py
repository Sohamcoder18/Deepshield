"""
Image Deepfake Detection Model Training Script
Trains XceptionNet model on image frame data for deepfake detection
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageDataProcessor:
    def __init__(self, dataset_root, face_size=224):
        """
        Initialize image data processor
        
        Args:
            dataset_root: Root directory of dataset
            face_size: Size to resize detected faces
        """
        # Convert to absolute path - handle relative paths correctly
        dataset_path = Path(dataset_root)
        if not dataset_path.is_absolute():
            # Resolve relative paths from current working directory
            dataset_path = (Path.cwd() / dataset_path).resolve()
        self.dataset_root = dataset_path
        self.face_size = face_size
        
        # Initialize face detectors
        logger.info("Initializing face detectors...")
        self.mtcnn_detector = MTCNN()
        # Load Haar Cascade as fallback
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.data = []
        self.labels = []
        
    def extract_faces_from_frame(self, frame):
        """Extract face regions from a frame using MTCNN with Haar Cascade fallback"""
        try:
            # Convert BGR to RGB for MTCNN
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Try MTCNN first
            detections = self.mtcnn_detector.detect_faces(frame_rgb)
            
            faces = []
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
            
            # Fallback to Haar Cascade if MTCNN found nothing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            haar_faces = self.haar_cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
            
            for (x, y, w, h) in haar_faces:
                face = frame_rgb[y:y+h, x:x+w]
                if face.size > 0:
                    face = cv2.resize(face, (self.face_size, self.face_size))
                    faces.append(face)
            
            return faces if faces else None
            
        except Exception as e:
            logger.debug(f"Face extraction error: {str(e)}")
            return None
    
    def extract_first_frame(self, video_path):
        """Extract first frame from video"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                logger.warning(f"Could not open video: {video_path}")
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
        except Exception as e:
            logger.error(f"Error extracting frame from {video_path}: {str(e)}")
            return None
    
    def process_video(self, video_path, label):
        """Process video: extract first frame and faces"""
        frame = self.extract_first_frame(video_path)
        
        if frame is None:
            logger.debug(f"Could not extract frame from {video_path}")
            return False
        
        faces = self.extract_faces_from_frame(frame)
        
        if faces:
            for face in faces:
                # Normalize pixel values
                face_normalized = face.astype(np.float32) / 255.0
                self.data.append(face_normalized)
                self.labels.append(label)
            logger.debug(f"Extracted {len(faces)} faces from {video_path}")
            return True
        
        logger.debug(f"No faces detected in {video_path}")
        return False
    
    def load_dataset(self, real_dir, fake_dirs):
        """Load entire dataset from directory structure"""
        logger.info("Loading image dataset...")
        
        # Process real videos (label: 1)
        logger.info(f"Processing real videos from: {real_dir}")
        real_path = self.dataset_root / real_dir
        real_videos_processed = 0
        real_videos_failed = 0
        
        if real_path.exists():
            video_files = sorted(real_path.glob("*.mp4"))[:200]  # Limit to 200 for faster processing
            logger.info(f"Found {len(video_files)} real videos to process")
            for video_file in tqdm(video_files):
                if self.process_video(str(video_file), label=1):
                    real_videos_processed += 1
                else:
                    real_videos_failed += 1
            logger.info(f"Real videos: {real_videos_processed} processed, {real_videos_failed} failed")
        
        # Process fake videos (label: 0)
        for fake_dir in fake_dirs:
            logger.info(f"Processing fake videos from: {fake_dir}")
            fake_path = self.dataset_root / fake_dir
            fake_videos_processed = 0
            fake_videos_failed = 0
            
            if fake_path.exists():
                video_files = sorted(fake_path.glob("*.mp4"))[:100]  # Limit to 100 per category
                logger.info(f"Found {len(video_files)} fake videos from {fake_dir}")
                for video_file in tqdm(video_files):
                    if self.process_video(str(video_file), label=0):
                        fake_videos_processed += 1
                    else:
                        fake_videos_failed += 1
                logger.info(f"{fake_dir}: {fake_videos_processed} processed, {fake_videos_failed} failed")
        
        logger.info(f"Total face samples collected: {len(self.data)}")
        
        if len(self.data) == 0:
            logger.error("No data loaded! This usually means:")
            logger.error("  1. Videos cannot be read (codec issue)")
            logger.error("  2. Face detectors are not finding any faces")
            logger.error("  3. Videos are too low quality or contain no clear faces")
            return None, None
            return None, None
        
        return np.array(self.data), np.array(self.labels)


class ImageDetectionModelTrainer:
    def __init__(self, input_shape=(224, 224, 3)):
        """Initialize model trainer"""
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_efficientnet_model(self):
        """Build EfficientNetB3 model for image deepfake detection"""
        logger.info("Building EfficientNetB3 model...")
        
        # Load pretrained EfficientNetB3
        base_model = keras.applications.EfficientNetB3(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        inputs = keras.Input(shape=self.input_shape)
        
        # Preprocess input for EfficientNet
        x = keras.applications.efficientnet.preprocess_input(inputs)
        
        # Base model
        x = base_model(x)
        
        # Global average pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers
        x = layers.Dense(512, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(128, activation='relu')(x)
        x = layers.BatchNormalization()(x)
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
                filepath='models/efficientnet_model_checkpoint.h5',
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
    logger.info("IMAGE MODEL TRAINING PIPELINE")
    logger.info("=" * 50)
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Dataset root (absolute): {dataset_root}")
    
    processor = ImageDataProcessor(dataset_root, face_size=224)
    
    # Load dataset
    X, y = processor.load_dataset(
        real_dir="DeepFakeDetection",
        fake_dirs=["Deepfakes", "Face2Face", "FaceShifter", "FaceSwap"]
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
    trainer = ImageDetectionModelTrainer(input_shape=(224, 224, 3))
    trainer.build_efficientnet_model()
    
    trainer.train(
        X_train, y_train,
        X_val, y_val,
        epochs=30,
        batch_size=32
    )
    
    # Evaluate model
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model(str(models_dir / "efficientnet_model.h5"))
    trainer.plot_training_history(str(models_dir / "image_training_history.png"))
    
    # Save metrics
    import json
    with open(str(models_dir / "image_metrics.json"), 'w') as f:
        metrics_to_save = metrics.copy()
        metrics_to_save['confusion_matrix'] = metrics_to_save['confusion_matrix'].tolist()
        json.dump(metrics_to_save, f, indent=2)
    
    logger.info("Image model training completed!")


if __name__ == "__main__":
    main()
