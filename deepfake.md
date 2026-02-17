Deepfake Detection Project – Model Overview
This document explains the models used in the Deepfake Detection System, their purpose, how they are used, and where they are applied in the project.
1. XceptionNet
Type: Convolutional Neural Network (CNN)
Purpose: Image and video deepfake detection

Description:
XceptionNet is a deep learning CNN architecture based on depthwise separable convolutions. It is widely used for deepfake detection because it can capture subtle facial artifacts introduced during face manipulation.

How it is used:
- A pretrained XceptionNet model (trained on FaceForensics++ dataset) is loaded in Python.
- The model takes a cropped face image as input.
- It outputs a probability score indicating whether the image is real or fake.

Where it is used in the project:
- Image deepfake detection module
- Video deepfake detection (by applying the model on extracted frames)
2. MTCNN (Multi-task Cascaded Convolutional Neural Network)
Type: Face detection model
Purpose: Detect and crop face regions before deepfake analysis

Description:
MTCNN is a face detection model that detects human faces and facial landmarks in images and video frames. It improves deepfake detection accuracy by ensuring that only the face region is analyzed.

How it is used:
- Input image or video frame is passed to MTCNN.
- MTCNN detects the face and returns bounding box coordinates.
- The detected face region is cropped and resized.

Where it is used in the project:
- Preprocessing step before XceptionNet inference
- Image and video analysis pipeline
3. MFCC (Mel-Frequency Cepstral Coefficients)
Type: Audio feature extraction technique
Purpose: Extract meaningful features from audio for deepfake detection

Description:
MFCC is not a model but a signal processing technique used to represent audio signals in a form suitable for machine learning models. It captures characteristics of human speech.

How it is used:
- Audio file is loaded using Librosa.
- MFCC features are extracted from the audio signal.
- These features are fed into a CNN classifier.

Where it is used in the project:
- Audio deepfake detection module
4. CNN for Audio Deepfake Detection
Type: Convolutional Neural Network
Purpose: Classify audio as real or fake

Description:
A CNN model is used to classify audio based on MFCC features. It learns patterns that differentiate real human speech from AI-generated or manipulated audio.

How it is used:
- MFCC features are passed to the CNN.
- The model predicts whether the audio is real or fake.

Where it is used in the project:
- Audio deepfake detection pipeline
5. Weighted Fusion Logic
Type: Rule-based fusion logic
Purpose: Combine results from image, video, and audio models

Description:
Weighted fusion logic combines prediction scores from multiple models to generate a final trust score.

How it is used:
- Image, video, and audio fake probabilities are collected.
- A weighted average formula is applied.
- Final trust score is generated.

Where it is used in the project:
- Final decision-making module
- Trust score generation
6. Grad-CAM (Optional Explainability)
Type: Explainable AI technique
Purpose: Visual explanation of model decisions

Description:
Grad-CAM highlights regions of the image that influence the model's prediction, helping users understand why content was classified as fake.

Where it is used in the project:
- Image and video explanation module (optional)
Overall System Workflow and Processing Pipeline

Image / Video Processing Pipeline:
1. The input image or video is uploaded through the frontend.
2. For images and video frames, MTCNN is used to detect and crop the facial region.
3. The cropped face is passed to XceptionNet, which analyzes visual artifacts and produces a real/fake probability score.
4. In case of video input, the video is split into frames and each frame is processed individually. The final video score is obtained by averaging frame-level predictions.

Audio Processing Pipeline:
1. The uploaded audio file is first processed using MFCC (Mel-Frequency Cepstral Coefficients).
2. MFCC extracts spectral and frequency-based audio features.
3. These features are passed to a CNN model, which detects synthetic or manipulated speech and produces an audio authenticity score.

Final Decision and Explainability:
1. The outputs from image/video analysis and audio analysis are combined using weighted fusion logic.
2. This fusion generates a final trust score indicating whether the content is real or fake.
3. Grad-CAM is applied on XceptionNet to highlight suspicious facial regions and provide explainable AI insights.

