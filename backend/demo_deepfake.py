#!/usr/bin/env python
"""
Deepfake Detection Demo and Testing Script
Demonstrates how to use the deepfake detection service and database utilities
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_service_usage():
    """
    Demo 1: Direct service usage without database
    """
    logger.info("=" * 80)
    logger.info("DEMO 1: Direct Service Usage")
    logger.info("=" * 80)
    
    try:
        from models.deepfake_service import DeepfakeDetectionService
        
        service = DeepfakeDetectionService()
        logger.info("✅ Service initialized")
        
        # Test with a sample image from dataset
        test_videos = [
            "../dataset/Face2Face/001_870.mp4",
            "../dataset/FaceSwap/001_870.mp4",
            "../dataset/original/001.mp4"
        ]
        
        for video_path in test_videos:
            if os.path.exists(video_path):
                logger.info(f"\nProcessing: {video_path}")
                
                start = time.time()
                result = service.classify_video(video_path, num_frames=3)
                elapsed = time.time() - start
                
                logger.info(f"  Fake: {result['fake']:.3f}")
                logger.info(f"  Real: {result['real']:.3f}")
                logger.info(f"  Time: {elapsed:.2f}s")
                logger.info(f"  Verdict: {'FAKE' if result['fake'] > result['real'] else 'REAL'}")
                
                time.sleep(1)
            else:
                logger.warning(f"File not found: {video_path}")
    
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")

def demo_database_integration():
    """
    Demo 2: Database integration (requires Flask app context)
    """
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Database Integration")
    logger.info("=" * 80)
    
    try:
        from app import app, db
        from models.deepfake_result import DeepfakeDetectionResult
        from models.deepfake_service import get_deepfake_service
        from utils.deepfake_db_utils import save_detection_result, get_user_stats
        
        with app.app_context():
            logger.info("✅ Flask app context created")
            
            # Initialize service
            service = get_deepfake_service()
            
            # Test file
            test_file = "../dataset/Face2Face/000_003.mp4"
            user_email = "demo@deepshield.com"
            
            if os.path.exists(test_file):
                logger.info(f"\nProcessing: {test_file}")
                logger.info(f"User: {user_email}")
                
                # Process file
                file_size = os.path.getsize(test_file)
                result = service.process_file(test_file, 'video')
                
                # Save to database
                db_result = save_detection_result(
                    db=db,
                    user_email=user_email,
                    file_name=os.path.basename(test_file),
                    file_path=test_file,
                    file_type='video',
                    file_size=file_size,
                    is_fake=result['is_fake'],
                    fake_confidence=result['fake_confidence'],
                    real_confidence=result['real_confidence'],
                    prediction_result=result['prediction'],
                    processing_time=result['processing_time'],
                    model_version=result['model_version'],
                    notes="Demo test"
                )
                
                if db_result:
                    logger.info(f"✅ Saved to database with ID: {db_result.id}")
                
                # Get user stats
                stats = get_user_stats(db, user_email)
                logger.info("\nUser Statistics:")
                logger.info(f"  Total Analyses: {stats['total_analyses']}")
                logger.info(f"  Fake Detected: {stats['fake_detected']}")
                logger.info(f"  Authentic: {stats['authentic_detected']}")
                logger.info(f"  Avg Processing Time: {stats['avg_processing_time']}s")
            else:
                logger.warning(f"Test file not found: {test_file}")
    
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_bulk_processing():
    """
    Demo 3: Bulk processing multiple files
    """
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Bulk Processing")
    logger.info("=" * 80)
    
    try:
        from app import app, db
        from models.deepfake_service import get_deepfake_service
        from utils.deepfake_db_utils import bulk_process_and_save
        
        with app.app_context():
            service = get_deepfake_service()
            user_email = "bulk-demo@deepshield.com"
            
            # Find test files
            dataset_dir = "../dataset"
            test_files = []
            
            for category in ['Face2Face', 'FaceSwap', 'original']:
                category_path = os.path.join(dataset_dir, category)
                if os.path.exists(category_path):
                    videos = [f for f in os.listdir(category_path)[:2] if f.endswith('.mp4')]
                    for video in videos:
                        test_files.append((os.path.join(category_path, video), 'video'))
            
            if test_files:
                logger.info(f"\nBulk processing {len(test_files)} files...")
                results = bulk_process_and_save(db, service, test_files, user_email)
                logger.info(f"✅ Successfully processed {len(results)} files")
            else:
                logger.warning("No test files found")
    
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        import traceback
        traceback.print_exc()

def show_api_endpoints():
    """
    Show available API endpoints
    """
    logger.info("\n" + "=" * 80)
    logger.info("AVAILABLE API ENDPOINTS")
    logger.info("=" * 80)
    
    endpoints = {
        "Service Health": "/api/deepfake/health",
        "Analyze Image": "POST /api/deepfake/analyze/image",
        "Analyze Video": "POST /api/deepfake/analyze/video",
        "Detection History": "GET /api/deepfake/history",
        "Detection Statistics": "GET /api/deepfake/stats"
    }
    
    for name, endpoint in endpoints.items():
        logger.info(f"  ✓ {name}: {endpoint}")
    
    logger.info("\nExample Usage:")
    logger.info("  # Analyze an image")
    logger.info("  curl -X POST http://localhost:5000/api/deepfake/analyze/image \\")
    logger.info("    -F 'file=@image.jpg' \\")
    logger.info("    -H 'Authorization: Bearer YOUR_TOKEN'")
    logger.info("")
    logger.info("  # Analyze a video")
    logger.info("  curl -X POST http://localhost:5000/api/deepfake/analyze/video \\")
    logger.info("    -F 'file=@video.mp4' \\")
    logger.info("    -F 'num_frames=5' \\")
    logger.info("    -H 'Authorization: Bearer YOUR_TOKEN'")
    logger.info("")
    logger.info("  # Get detection history")
    logger.info("  curl http://localhost:5000/api/deepfake/history \\")
    logger.info("    -H 'Authorization: Bearer YOUR_TOKEN'")

if __name__ == "__main__":
    logger.info("\n🎬 DEEPFAKE DETECTION DEMO\n")
    
    # Run demos
    demo_service_usage()
    demo_database_integration()
    demo_bulk_processing()
    
    # Show API endpoints
    show_api_endpoints()
    
    logger.info("\n✅ Demo completed!\n")
