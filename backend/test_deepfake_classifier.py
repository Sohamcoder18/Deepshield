import os
import cv2
from PIL import Image
import numpy as np
from deepfake_classifier import classify_image

def extract_frame_from_video(video_path, frame_num=10):
    """Extract a specific frame from a video file"""
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        return None
    except Exception as e:
        print(f"Error extracting frame: {e}")
        return None

def test_classifier():
    """Test the deepfake classifier on dataset videos"""
    
    # Define test directories
    test_dirs = {
        "Deepfakes": "../dataset/Deepfakes",
        "Face2Face": "../dataset/Face2Face",
        "FaceShifter": "../dataset/FaceShifter",
        "FaceSwap": "../dataset/FaceSwap",
        "NeuralTextures": "../dataset/NeuralTextures",
        "Original": "../dataset/original"
    }
    
    results = {}
    correct_predictions = 0
    total_predictions = 0
    
    print("=" * 80)
    print("DEEPFAKE DETECTION TEST RESULTS")
    print("=" * 80)
    
    for category, test_dir in test_dirs.items():
        if not os.path.exists(test_dir):
            print(f"\n⚠️  {category} directory not found: {test_dir}")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"Testing {category.upper()}")
        print(f"{'=' * 80}")
        
        results[category] = []
        video_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        
        if not video_files:
            print(f"No videos found in {test_dir}")
            continue
        
        # Test first 5 videos from each category
        for video_file in video_files[:5]:
            try:
                video_path = os.path.join(test_dir, video_file)
                
                # Extract frame from video
                img = extract_frame_from_video(video_path, frame_num=10)
                
                if img is None:
                    print(f"\n⚠️  Could not extract frame from {video_file}")
                    continue
                
                img_array = np.array(img)
                result = classify_image(img_array)
                results[category].append({
                    "file": video_file,
                    "prediction": result
                })
                
                print(f"\n📹 {video_file}")
                print(f"   Fake:  {result['fake']:.3f}")
                print(f"   Real:  {result['real']:.3f}")
                
                # Determine if prediction is correct
                is_fake = category != "Original"
                predicted_fake = result['fake'] > result['real']
                
                if is_fake == predicted_fake:
                    print(f"   ✅ Correct prediction")
                    correct_predictions += 1
                else:
                    print(f"   ❌ Incorrect prediction")
                
                total_predictions += 1
                
            except Exception as e:
                print(f"\n❌ Error processing {video_file}: {str(e)}")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    
    total_tests = sum(len(v) for v in results.values())
    print(f"Total videos tested: {total_tests}")
    
    if total_predictions > 0:
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"Correct predictions: {correct_predictions}/{total_predictions}")
        print(f"Accuracy: {accuracy:.2f}%")
    
    for category, predictions in results.items():
        if predictions:
            print(f"\n{category}: {len(predictions)} videos tested")

if __name__ == "__main__":
    test_classifier()
