# Integration Examples - Database with Detection Endpoints

This file shows how to integrate database saving into your existing detection endpoints.

## Example 1: Image Detection with Database Saving

```python
@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    """
    Analyze image for deepfake detection with database saving
    """
    try:
        # ... existing validation code ...
        
        # Perform detection
        logger.info(f"Analyzing image: {filename}")
        results = image_detector.detect(filepath)
        
        # Get file info
        file_info = get_file_info(filepath)
        
        # Prepare response
        response = {
            'status': 'success',
            'analysis_type': 'image',
            'file_name': filename,
            'file_size': file_info['size'],
            'analysis_time': results['analysis_time'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'xception_score': results['xception_confidence'],
            'artifact_detection': results['artifact_score'],
            'gradcam_heatmap': results['gradcam'],
            'recommendation': results['recommendation'],
            'timestamp': datetime.now().isoformat()
        }
        
        # NEW: Save to databases
        db_result = db_manager.save_analysis_result({
            'analysis_type': 'image',
            'file_name': filename,
            'file_size': file_info['size'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'recommendation': results['recommendation'],
            'analysis_time': results['analysis_time']
        })
        
        # Add database IDs to response
        response['analysis_id'] = db_result['analysis_id']
        response['sqlite_id'] = db_result['sqlite_id']
        response['mongodb_id'] = db_result['mongodb_id']
        
        # Clean up
        os.remove(filepath)
        
        logger.info(f"Analysis saved with ID: {db_result['analysis_id']}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in image analysis: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
```

## Example 2: Video Detection with Database Saving

```python
@app.route('/api/analyze/video', methods=['POST'])
def analyze_video():
    """
    Analyze video for deepfake detection with database saving
    """
    try:
        # ... existing validation code ...
        
        # Perform detection
        logger.info(f"Analyzing video: {filename}")
        results = video_detector.detect(filepath, frame_count)
        
        # Get file info
        file_info = get_file_info(filepath)
        
        # Prepare response
        response = {
            'status': 'success',
            'analysis_type': 'video',
            'file_name': filename,
            'file_size': file_info['size'],
            'analysis_time': results['analysis_time'],
            'duration': results['duration'],
            'frames_analyzed': results['frames_analyzed'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'average_fake_probability': results['avg_fake_probability'],
            'suspicious_frames': results['suspicious_frames'],
            'suspicious_frame_indices': results['suspicious_frame_indices'],
            'temporal_consistency': results['temporal_consistency'],
            'consistency_score': results['consistency_score'],
            'frame_results': results['frame_results'],
            'recommendation': results['recommendation'],
            'timestamp': datetime.now().isoformat()
        }
        
        # NEW: Save to databases with detailed results
        db_result = db_manager.save_analysis_result({
            'analysis_type': 'video',
            'file_name': filename,
            'file_size': file_info['size'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'recommendation': results['recommendation'],
            'analysis_time': results['analysis_time'],
            # Additional video-specific data (stored in MongoDB only)
            'duration': results['duration'],
            'frames_analyzed': results['frames_analyzed'],
            'suspicious_frames': results['suspicious_frames'],
            'temporal_consistency': results['temporal_consistency']
        })
        
        # Add database IDs to response
        response['analysis_id'] = db_result['analysis_id']
        response['sqlite_id'] = db_result['sqlite_id']
        response['mongodb_id'] = db_result['mongodb_id']
        
        # Clean up
        os.remove(filepath)
        
        logger.info(f"Video analysis saved with ID: {db_result['analysis_id']}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in video analysis: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
```

## Example 3: Audio Detection with Database Saving

```python
@app.route('/api/analyze/audio', methods=['POST'])
def analyze_audio():
    """
    Analyze audio for deepfake detection with database saving
    """
    try:
        # ... existing validation code ...
        
        # Perform detection
        logger.info(f"Analyzing audio: {filename}")
        results = audio_detector.detect(filepath)
        
        # Get file info
        file_info = get_file_info(filepath)
        
        # Prepare response
        response = {
            'status': 'success',
            'analysis_type': 'audio',
            'file_name': filename,
            'file_size': file_info['size'],
            'analysis_time': results['analysis_time'],
            'duration': results['duration'],
            'sample_rate': results['sample_rate'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'synthesis_probability': results['synthesis_probability'],
            'authenticity_score': results['authenticity_score'],
            'spectral_consistency': results['spectral_consistency'],
            'frequency_stability': results['frequency_stability'],
            'mfcc_features': results['mfcc_features'],
            'spectrogram': results['spectrogram'],
            'recommendation': results['recommendation'],
            'timestamp': datetime.now().isoformat()
        }
        
        # NEW: Save to databases
        db_result = db_manager.save_analysis_result({
            'analysis_type': 'audio',
            'file_name': filename,
            'file_size': file_info['size'],
            'trust_score': results['trust_score'],
            'is_fake': results['is_fake'],
            'confidence': results['confidence'],
            'recommendation': results['recommendation'],
            'analysis_time': results['analysis_time'],
            # Additional audio-specific data
            'duration': results['duration'],
            'sample_rate': results['sample_rate'],
            'synthesis_probability': results['synthesis_probability']
        })
        
        # Add database IDs to response
        response['analysis_id'] = db_result['analysis_id']
        response['sqlite_id'] = db_result['sqlite_id']
        response['mongodb_id'] = db_result['mongodb_id']
        
        # Clean up
        os.remove(filepath)
        
        logger.info(f"Audio analysis saved with ID: {db_result['analysis_id']}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
```

## Example 4: Save Fusion Results

```python
@app.route('/api/fusion/combine', methods=['POST'])
def combine_results():
    """
    Combine results from image, video, and audio analysis with database saving
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract scores
        image_score = data.get('image_score')
        video_score = data.get('video_score')
        audio_score = data.get('audio_score')
        
        # Perform fusion
        logger.info("Performing weighted fusion on detection results")
        fused_result = fusion_logic.fuse_results(
            image_score=image_score,
            video_score=video_score,
            audio_score=audio_score
        )
        
        response = {
            'status': 'success',
            'fusion_type': 'weighted_average',
            'individual_scores': {
                'image': image_score,
                'video': video_score,
                'audio': audio_score
            },
            'fused_trust_score': fused_result['trust_score'],
            'final_verdict': fused_result['verdict'],
            'confidence': fused_result['confidence'],
            'weights': fused_result['weights'],
            'recommendation': fused_result['recommendation'],
            'timestamp': datetime.now().isoformat()
        }
        
        # NEW: Save fusion result to MongoDB
        if mongo_db:
            fusion_data = {
                'fusion_id': str(uuid.uuid4()),
                'individual_scores': {
                    'image': image_score,
                    'video': video_score,
                    'audio': audio_score
                },
                'fused_trust_score': fused_result['trust_score'],
                'final_verdict': fused_result['verdict'],
                'confidence': fused_result['confidence'],
                'weights': fused_result['weights'],
                'recommendation': fused_result['recommendation']
            }
            
            fusion_id = db_manager.save_fusion_result(fusion_data)
            response['fusion_id'] = fusion_id
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in fusion: {str(e)}")
        return jsonify({'error': f'Fusion failed: {str(e)}'}), 500
```

## Example 5: Create Analysis History Endpoint

```python
@app.route('/api/user/<user_id>/analyses', methods=['GET'])
def get_user_analyses(user_id):
    """Get all analyses performed by a specific user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        analysis_type = request.args.get('type', None)
        
        # Query from MongoDB for better flexibility
        if not mongo_db:
            return jsonify({'error': 'MongoDB not available'}), 503
        
        query = {'user_id': user_id}
        if analysis_type:
            query['analysis_type'] = analysis_type
        
        analyses = list(mongo_db.analysis_results.find(query).limit(limit).sort('timestamp', -1))
        
        for analysis in analyses:
            analysis['_id'] = str(analysis['_id'])
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'total': len(analyses),
            'analyses': analyses,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user analyses: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

## Usage Pattern

When integrating these examples into your detection endpoints:

1. **Keep existing detection logic** - Don't change how detection works
2. **Add database saving** - Right after generating results
3. **Include analysis_id in response** - So clients can retrieve results later
4. **Handle database errors gracefully** - Detection should work even if database is down
5. **Log database operations** - For debugging and auditing

## Best Practice Code Structure

```python
try:
    # Step 1: Validate input
    # Step 2: Save file temporarily
    # Step 3: Perform detection
    # Step 4: Prepare response
    # Step 5: SAVE TO DATABASE
    # Step 6: Clean up files
    # Step 7: Return response
except Exception as e:
    # Handle error
```
