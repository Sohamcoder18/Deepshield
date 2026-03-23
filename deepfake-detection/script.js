// ============================================
// GLOBAL STATE MANAGEMENT
// ============================================

let currentFile = null;
let analysisInProgress = false;
const detectionType = detectPageType();

function detectPageType() {
    const path = window.location.pathname;
    if (path.includes('image')) return 'image';
    if (path.includes('video')) return 'video';
    if (path.includes('audio')) return 'audio';
    return 'home';
}

// ============================================
// NOTIFICATION FUNCTIONS
// ============================================

function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    if (errorSection && errorMessage) {
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
    }
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #00D084 0%, #00A86B 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

function clearError() {
    const errorSection = document.getElementById('errorSection');
    if (errorSection) {
        errorSection.style.display = 'none';
    }
}

// ============================================
// UPLOAD FUNCTIONALITY
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initializeNavbar();
    setupNavigation();
    setupUploadArea();
    initializeExpandableCards();
});

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    window.location.href = 'login.html';
}

function setupUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!uploadArea) return;

    // Click to browse
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--secondary-color)';
        uploadArea.style.background = 'linear-gradient(135deg, rgba(0, 102, 255, 0.15) 0%, rgba(0, 212, 255, 0.15) 100%)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%)';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    currentFile = file;
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadArea = document.getElementById('uploadArea');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewSection = document.getElementById('previewSection');

    // Show file info
    fileName.textContent = `✓ ${file.name} (${formatFileSize(file.size)})`;
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';

    // Show preview
    if (detectionType === 'image') {
        previewImage(file);
    } else if (detectionType === 'video') {
        previewVideo(file);
    } else if (detectionType === 'audio') {
        previewAudio(file);
    }

    // Show analyze button
    if (analyzeBtn) analyzeBtn.style.display = 'block';
}

function clearFile() {
    currentFile = null;
    
    // Clear file input
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Reset UI elements
    const fileInfo = document.getElementById('fileInfo');
    const uploadArea = document.getElementById('uploadArea');
    const previewSection = document.getElementById('previewSection');
    const frameSelection = document.getElementById('frameSelection');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (fileInfo) fileInfo.style.display = 'none';
    if (uploadArea) uploadArea.style.display = 'block';
    if (previewSection) previewSection.style.display = 'none';
    if (frameSelection) frameSelection.style.display = 'none';
    if (analyzeBtn) analyzeBtn.style.display = 'none';
    
    clearResults();
}

function previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('previewSection').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function previewVideo(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const videoSource = document.getElementById('videoSource');
        videoSource.src = e.target.result;
        const video = document.getElementById('previewVideo');
        video.load();
        document.getElementById('previewSection').style.display = 'block';
        document.getElementById('frameSelection').style.display = 'block';

        // Get video metadata
        video.addEventListener('loadedmetadata', function() {
            const minutes = Math.floor(video.duration / 60);
            const seconds = Math.floor(video.duration % 60);
            document.getElementById('videoDuration').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
            document.getElementById('videoResolution').textContent = 
                `${video.videoWidth}x${video.videoHeight}`;
        });
    };
    reader.readAsDataURL(file);
}

function previewAudio(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const audioSource = document.getElementById('audioSource');
        audioSource.src = e.target.result;
        const audio = document.getElementById('previewAudio');
        audio.load();
        document.getElementById('previewSection').style.display = 'block';
        document.getElementById('waveformContainer').style.display = 'block';

        // Get audio metadata
        audio.addEventListener('loadedmetadata', function() {
            const minutes = Math.floor(audio.duration / 60);
            const seconds = Math.floor(audio.duration % 60);
            document.getElementById('audioDuration').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
        });

        // Draw waveform
        drawWaveform(e.target.result);
    };
    reader.readAsDataURL(file);
}

function drawWaveform(audioData) {
    const canvas = document.getElementById('waveformCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    
    canvas.width = width;
    canvas.height = height;

    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Draw waveform (simple visualization)
    ctx.strokeStyle = 'var(--secondary-color)';
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < width; i++) {
        const value = Math.sin((i / width) * Math.PI * 4) * (height / 4);
        const y = height / 2 + value;
        
        if (i === 0) {
            ctx.moveTo(i, y);
        } else {
            ctx.lineTo(i, y);
        }
    }
    ctx.stroke();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================
// ANALYSIS FUNCTIONS
// ============================================

function analyzeImage() {
    if (!currentFile || analysisInProgress) return;
    
    analysisInProgress = true;
    showLoading('Analyzing image with XceptionNet CNN...');
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    // Add user email if logged in
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
        formData.append('userEmail', userEmail);
    }
    
    fetch(getApiUrl('/api/analyze/image'), {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Analysis failed');
        return response.json();
    })
    .then(data => {
        if (data.error) throw new Error(data.error);
        displayImageResults(data);
        if (userEmail) {
            showSuccess('Analysis complete! Check your email for results.');
        }
    })
    .catch(error => {
        showError(error.message || 'Analysis failed. Please try again.');
        console.error('Error:', error);
    })
    .finally(() => {
        analysisInProgress = false;
        hideLoading();
    });
}

function analyzeVideo() {
    if (!currentFile || analysisInProgress) return;
    
    const frameCount = document.querySelector('input[name="frameSample"]:checked').value;
    analysisInProgress = true;
    showLoading(`Analyzing ${frameCount} frames from video...`);
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('frame_count', frameCount);
    
    // Add user email if logged in
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
        formData.append('userEmail', userEmail);
    }
    
    fetch(getApiUrl('/api/analyze/video'), {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Analysis failed');
        return response.json();
    })
    .then(data => {
        if (data.error) throw new Error(data.error);
        displayVideoResults(data);
        if (userEmail) {
            showSuccess('Analysis complete! Check your email for results.');
        }
    })
    .catch(error => {
        showError(error.message || 'Analysis failed. Please try again.');
        console.error('Error:', error);
    })
    .finally(() => {
        analysisInProgress = false;
        hideLoading();
    });
}

function analyzeAudio() {
    if (!currentFile || analysisInProgress) return;
    
    analysisInProgress = true;
    showLoading('Extracting MFCC features and analyzing speech...');
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    // Add user email if logged in
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
        formData.append('userEmail', userEmail);
    }
    
    fetch(getApiUrl('/api/analyze/audio'), {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Analysis failed');
        return response.json();
    })
    .then(data => {
        if (data.error) throw new Error(data.error);
        displayAudioResults(data);
        if (userEmail) {
            showSuccess('Analysis complete! Check your email for results.');
        }
    })
    .catch(error => {
        showError(error.message || 'Analysis failed. Please try again.');
        console.error('Error:', error);
    })
    .finally(() => {
        analysisInProgress = false;
        hideLoading();
    });
}

// ============================================
// RESULT GENERATION (Simulated)
// ============================================

function generateImageResults() {
    const isFake = Math.random() > 0.6;
    const confidence = 0.5 + Math.random() * 0.5;
    
    return {
        trustScore: isFake ? (1 - confidence) * 100 : confidence * 100,
        xceptionConfidence: isFake ? (1 - confidence) * 100 : confidence * 100,
        artifactConfidence: isFake ? (1 - confidence) * 80 : confidence * 90,
        isFake: isFake,
        fakeConfidence: isFake ? confidence : (1 - confidence),
        analysisTime: (2 + Math.random() * 2).toFixed(2)
    };
}

function generateVideoResults(frameCount) {
    const isFake = Math.random() > 0.55;
    const avgConfidence = 0.4 + Math.random() * 0.6;
    const consistencyScore = 0.7 + Math.random() * 0.3;
    
    return {
        trustScore: isFake ? (1 - avgConfidence) * 100 : avgConfidence * 100,
        framesAnalyzed: frameCount,
        avgConfidence: isFake ? (1 - avgConfidence) * 100 : avgConfidence * 100,
        suspiciousFrames: Math.floor(frameCount * (isFake ? 0.3 : 0.1)),
        consistencyScore: consistencyScore * 100,
        isFake: isFake,
        fakeConfidence: isFake ? avgConfidence : (1 - avgConfidence),
        analysisTime: (3 + Math.random() * 2).toFixed(2)
    };
}

function generateAudioResults() {
    const isFake = Math.random() > 0.65;
    const synthesisProb = 0.3 + Math.random() * 0.7;
    
    return {
        trustScore: isFake ? synthesisProb * 100 : (1 - synthesisProb) * 100,
        synthesisConfidence: isFake ? synthesisProb * 100 : (1 - synthesisProb) * 100,
        authenticityConfidence: isFake ? (1 - synthesisProb) * 100 : synthesisProb * 100,
        spectralConfidence: (0.6 + Math.random() * 0.4) * 100,
        frequencyConfidence: (0.65 + Math.random() * 0.35) * 100,
        isFake: isFake,
        fakeConfidence: isFake ? synthesisProb : (1 - synthesisProb),
        analysisTime: (2.5 + Math.random() * 1.5).toFixed(2)
    };
}

// ============================================
// DISPLAY RESULTS
// ============================================

function displayImageResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';

    // Debug: Log the entire response
    console.log('=== IMAGE ANALYSIS RESPONSE ===');
    console.log('Full Results:', results);
    console.log('AI Analysis:', results.ai_analysis);
    console.log('================================');

    // Ensure values are valid numbers
    const trustScore = parseFloat(results.trust_score) || 0;
    const xceptionConfidence = parseFloat(results.xception_score) || 0;
    const artifactScore = parseFloat(results.artifact_detection) || 0;
    const analysisTime = parseFloat(results.analysis_time) || 0;
    
    // Validate that values are not NaN
    if (isNaN(trustScore)) {
        console.error('Invalid trust_score:', results.trust_score);
    }

    // Update trust score
    updateTrustScore(trustScore);

    // Update confidence bars
    animateProgressBar('xceptionConfidence', xceptionConfidence);
    document.getElementById('xceptionScore').textContent = xceptionConfidence.toFixed(1) + '%';

    animateProgressBar('artifactConfidence', artifactScore);
    document.getElementById('artifactScore').textContent = artifactScore.toFixed(1) + '%';

    // Update verdict
    const isFake = results.is_fake || false;
    const fakeConfidence = parseFloat(results.confidence) || 0;
    updateVerdict({
        isFake: isFake,
        fakeConfidence: fakeConfidence
    });

    // Update report with AI analysis if available
    let recommendation = results.recommendation || (isFake 
        ? 'This image shows signs of manipulation. Exercise caution with this content.' 
        : 'This image appears to be authentic based on current analysis.');
    
    if (results.ai_analysis) {
        recommendation = results.ai_analysis.verdict || recommendation;
    }
    
    updateReport({
        fileName: currentFile.name,
        fileSize: formatFileSize(currentFile.size),
        analysisTime: analysisTime,
        recommendation: recommendation
    });

    // Display AI-based reasoning if available
    if (results.ai_analysis && results.ai_analysis.reasons) {
        console.log('✓ AI Analysis data found, displaying reasons');
        displayAIReasons(results.ai_analysis, isFake);
    } else {
        console.warn('⚠ No AI analysis data available');
        console.log('ai_analysis object:', results.ai_analysis);
        if (results.ai_analysis) {
            console.log('reasons array:', results.ai_analysis.reasons);
        }
    }

    // Generate Grad-CAM visualization
    generateGradCAM(results);

    // Hide loading
    hideLoading();
    
    // Initialize expandable cards
    initializeExpandableCards();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayVideoResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';

    // Ensure values are valid numbers
    const trustScore = parseFloat(results.trust_score) || 0;
    const confidence = parseFloat(results.confidence) || 0;
    const analysisTime = parseFloat(results.analysis_time) || 0;
    const isFake = results.is_fake || false;

    // Update trust score
    updateTrustScore(trustScore);

    // Update frame analysis (placeholder values if not provided)
    const framesAnalyzed = results.frames_analyzed || 0;
    const suspiciousFrames = results.suspicious_frames || 0;
    const avgConfidence = parseFloat(results.confidence) || 0;
    
    document.getElementById('framesAnalyzed').textContent = framesAnalyzed;
    animateProgressBar('avgConfidence', avgConfidence);
    document.getElementById('avgScore').textContent = avgConfidence.toFixed(1) + '%';
    document.getElementById('suspiciousFrames').textContent = suspiciousFrames;

    // Update temporal consistency
    const consistencyScore = parseFloat(results.consistency_score) || 50;
    animateProgressBar('consistencyScore', consistencyScore);
    document.getElementById('consistencyValue').textContent = consistencyScore.toFixed(1) + '%';
    
    const consistencyInfo = consistencyScore > 80 
        ? 'Good temporal consistency detected - likely authentic content'
        : 'Some temporal inconsistencies detected - may indicate manipulation';
    document.getElementById('consistencyInfo').textContent = consistencyInfo;

    // Update verdict
    updateVerdict({
        isFake: isFake,
        fakeConfidence: confidence
    });

    // Update report
    const video = document.getElementById('previewVideo');
    const duration = video ? `${Math.floor(video.duration / 60)}:${Math.floor(video.duration % 60).toString().padStart(2, '0')}` : 'N/A';
    
    let recommendation = results.recommendation || (isFake 
        ? 'This video shows signs of deepfake manipulation. Review suspicious frames carefully.' 
        : 'This video appears authentic based on frame-by-frame analysis.');
    
    if (results.ai_analysis) {
        recommendation = results.ai_analysis.verdict || recommendation;
    }
    
    updateReport({
        fileName: currentFile.name,
        fileSize: formatFileSize(currentFile.size),
        duration: duration,
        analysisTime: analysisTime,
        recommendation: recommendation
    });

    // Display AI-based reasoning if available
    if (results.ai_analysis && results.ai_analysis.reasons) {
        displayAIReasons(results.ai_analysis, isFake);
    }

    // Generate timeline chart
    generateTimelineChart(framesAnalyzed, suspiciousFrames);

    // Generate suspicious frames gallery
    generateFramesGallery(suspiciousFrames);

    // Hide loading
    hideLoading();
    
    // Initialize expandable cards
    initializeExpandableCards();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayAudioResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';

    // Ensure values are valid numbers
    const trustScore = parseFloat(results.trust_score) || 0;
    const confidence = parseFloat(results.confidence) || 0;
    const analysisTime = parseFloat(results.analysis_time) || 0;
    const isFake = results.is_fake || false;
    
    // Update trust score
    updateTrustScore(trustScore);

    // Update speech analysis
    const synthesisConfidence = parseFloat(results.synthesis_confidence) || parseFloat(results.confidence) || 0;
    animateProgressBar('synthesisConfidence', synthesisConfidence);
    document.getElementById('synthesisScore').textContent = synthesisConfidence.toFixed(1) + '%';

    const authenticityConfidence = parseFloat(results.authenticity_confidence) || parseFloat(results.confidence) || 0;
    animateProgressBar('authenticityConfidence', authenticityConfidence);
    document.getElementById('authenticityScore').textContent = authenticityConfidence.toFixed(1) + '%';

    // Update MFCC features
    const spectralConfidence = parseFloat(results.spectral_confidence) || parseFloat(results.confidence) || 0;
    animateProgressBar('spectralConfidence', spectralConfidence);
    document.getElementById('spectralScore').textContent = spectralConfidence.toFixed(1) + '%';

    const frequencyConfidence = parseFloat(results.frequency_confidence) || parseFloat(results.confidence) || 0;
    animateProgressBar('frequencyConfidence', frequencyConfidence);
    document.getElementById('frequencyScore').textContent = frequencyConfidence.toFixed(1) + '%';

    // Update verdict
    updateVerdict({
        isFake: isFake,
        fakeConfidence: confidence
    });

    // Update report
    const audio = document.getElementById('previewAudio');
    const duration = audio ? `${Math.floor(audio.duration / 60)}:${Math.floor(audio.duration % 60).toString().padStart(2, '0')}` : 'N/A';
    
    let recommendation = results.recommendation || (isFake 
        ? 'This audio shows characteristics of speech synthesis. Verify speaker identity separately.' 
        : 'This audio appears to be authentic human speech based on acoustic analysis.');
    
    if (results.ai_analysis) {
        recommendation = results.ai_analysis.verdict || recommendation;
    }
    
    updateReport({
        fileName: currentFile.name,
        fileSize: formatFileSize(currentFile.size),
        duration: duration,
        sampleRate: '44.1 kHz',
        analysisTime: analysisTime,
        recommendation: recommendation
    });

    // Display AI-based reasoning if available
    if (results.ai_analysis && results.ai_analysis.reasons) {
        displayAIReasons(results.ai_analysis, isFake);
    }

    // Generate spectrogram
    generateSpectrogram();

    // Generate frequency chart
    generateFrequencyChart();

    // Hide loading
    hideLoading();
    
    // Initialize expandable cards
    initializeExpandableCards();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

function updateTrustScore(score) {
    const trustBar = document.getElementById('trustBar');
    const trustPercentage = document.getElementById('trustPercentage');
    
    if (trustBar) {
        setTimeout(() => {
            trustBar.style.width = score + '%';
        }, 100);
    }
    
    if (trustPercentage) {
        animateCounter(trustPercentage, 0, score, 1000);
    }
}

function animateProgressBar(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    setTimeout(() => {
        element.style.width = targetValue + '%';
    }, 100);
}

function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = current.toFixed(1) + '%';
    }, 16);
}

function updateVerdict(results) {
    const verdictBox = document.getElementById('verdictBox');
    const verdictText = document.getElementById('verdictText');
    const verdictConfidence = document.getElementById('verdictConfidence');

    if (results.isFake) {
        verdictBox.classList.add('danger');
        verdictText.textContent = '⚠️ LIKELY DEEPFAKE';
        verdictConfidence.textContent = `Confidence: ${(results.fakeConfidence * 100).toFixed(1)}%`;
    } else {
        verdictBox.classList.remove('danger');
        verdictText.textContent = '✓ AUTHENTIC';
        verdictConfidence.textContent = `Confidence: ${(results.fakeConfidence * 100).toFixed(1)}%`;
    }
}

function updateReport(data) {
    if (data.fileName) document.getElementById('reportFileName').textContent = data.fileName;
    if (data.fileSize) document.getElementById('reportFileSize').textContent = data.fileSize;
    if (data.duration) document.getElementById('reportDuration').textContent = data.duration;
    if (data.sampleRate) document.getElementById('reportSampleRate').textContent = data.sampleRate;
    if (data.analysisTime) document.getElementById('reportTime').textContent = data.analysisTime + 's';
    if (data.recommendation) document.getElementById('reportRecommendation').textContent = data.recommendation;
}

function showLoading(text) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
        if (loadingText) loadingText.textContent = text;
    }
    
    hideResults();
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) loadingSpinner.style.display = 'none';
}

function hideResults() {
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) resultsSection.style.display = 'none';
}

function clearResults() {
    hideLoading();
    hideResults();
    document.getElementById('errorSection').style.display = 'none';
}

function clearError() {
    document.getElementById('errorSection').style.display = 'none';
}

// ============================================
// VISUALIZATION FUNCTIONS
// ============================================

function generateGradCAM(results) {
    console.log('=== GRADCAM GENERATION START ===');
    console.log('Results received:', results);
    console.log('gradcam_heatmap:', results.gradcam_heatmap);
    console.log('gradcam_heatmap is array:', Array.isArray(results.gradcam_heatmap));
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Check if we have actual Grad-CAM data from backend
    if (results.gradcam_heatmap && Array.isArray(results.gradcam_heatmap) && results.gradcam_heatmap.length > 0) {
        console.log('Using ACTUAL Grad-CAM heatmap data from backend');
        
        // Use actual backend Grad-CAM heatmap data
        const heatmapData = results.gradcam_heatmap;
        const height = heatmapData.length;
        const width = heatmapData[0] ? heatmapData[0].length : 0;

        console.log('Heatmap dimensions:', height, 'x', width);

        if (height > 0 && width > 0) {
            canvas.width = width;
            canvas.height = height;
            const imageData = ctx.createImageData(width, height);
            const data = imageData.data;

            // Find min and max values for normalization
            let min = Infinity, max = -Infinity;
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const value = heatmapData[y][x];
                    if (value < min) min = value;
                    if (value > max) max = value;
                }
            }

            console.log('Heatmap value range:', min, 'to', max);

            // Render heatmap with proper color mapping
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const pixelIndex = (y * width + x) * 4;
                    const value = heatmapData[y][x];
                    
                    // Normalize to 0-1 range
                    const normalized = (value - min) / (max - min + 1e-8);
                    
                    // Color mapping: blue (low) -> cyan -> green -> yellow -> red (high)
                    let red, green, blue;
                    
                    if (normalized < 0.25) {
                        // Blue to Cyan
                        red = 0;
                        green = Math.floor(normalized * 4 * 255);
                        blue = 255;
                    } else if (normalized < 0.5) {
                        // Cyan to Green
                        red = 0;
                        green = 255;
                        blue = Math.floor((1 - (normalized - 0.25) * 4) * 255);
                    } else if (normalized < 0.75) {
                        // Green to Yellow
                        red = Math.floor((normalized - 0.5) * 4 * 255);
                        green = 255;
                        blue = 0;
                    } else {
                        // Yellow to Red
                        red = 255;
                        green = Math.floor((1 - (normalized - 0.75) * 4) * 255);
                        blue = 0;
                    }
                    
                    data[pixelIndex] = Math.floor(red);
                    data[pixelIndex + 1] = Math.floor(green);
                    data[pixelIndex + 2] = Math.floor(blue);
                    data[pixelIndex + 3] = 255; // Full opacity
                }
            }

            ctx.putImageData(imageData, 0, 0);
            document.getElementById('gradcamImage').src = canvas.toDataURL();
            console.log('=== GRADCAM RENDERED FROM REAL DATA ===');
            return;
        }
    }

    // Fallback: Generate placeholder visualization if no backend data
    console.log('NO REAL DATA - Using FALLBACK placeholder visualization');
    console.log('This means gradcam_heatmap is:', results.gradcam_heatmap);
    
    canvas.width = 224;
    canvas.height = 224;
    const imageData = ctx.createImageData(224, 224);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
        const pixelIndex = i / 4;
        const x = pixelIndex % 224;
        const y = Math.floor(pixelIndex / 224);

        // Create a gradient based on position (placeholder)
        const importance = Math.sin((x / 224) * Math.PI) * Math.sin((y / 224) * Math.PI);
        const red = Math.min(255, Math.floor(importance * 255));
        const green = Math.min(255, Math.floor((1 - importance) * 100));
        const blue = 100;

        data[i] = red;
        data[i + 1] = green;
        data[i + 2] = blue;
        data[i + 3] = 128;
    }

    ctx.putImageData(imageData, 0, 0);
    document.getElementById('gradcamImage').src = canvas.toDataURL();
    console.log('=== GRADCAM USING FALLBACK ===');
}

// ============================================
// AI-BASED REASONING DISPLAY
// ============================================

function displayAIReasons(aiAnalysis, isFake) {
    console.log('=== DISPLAYING AI REASONS ===');
    console.log('AI Analysis:', aiAnalysis);
    console.log('Is Fake:', isFake);
    
    // Find the dedicated reasons container
    const reasonsContainer = document.getElementById('aiReasonsContainer');
    
    if (!reasonsContainer) {
        console.warn('⚠ AI Reasons container not found in DOM');
        return;
    }
    
    // Build HTML content with proper structure
    let html = `
        <h3 class="ai-section-title">AI-Powered Analysis</h3>
        
        <div class="ai-verdict-banner ${isFake ? 'deepfake' : ''}">
            <p class="ai-verdict-text">${escapeHtml(aiAnalysis.verdict || 'Analysis Complete')}</p>
            ${aiAnalysis.risk_assessment ? `
                <p class="ai-risk-assessment">${escapeHtml(aiAnalysis.risk_assessment)}</p>
            ` : ''}
        </div>
        
        <div>
            <h4 style="color: #00D4FF; margin-bottom: 20px; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                <span>📊</span> Key Technical Findings
            </h4>
            <div class="ai-findings-list">`;
    
    // Add each reason as a styled item
    if (aiAnalysis.reasons && Array.isArray(aiAnalysis.reasons) && aiAnalysis.reasons.length > 0) {
        aiAnalysis.reasons.forEach((reason, index) => {
            html += `
                <div class="ai-finding-item ${isFake ? 'deepfake' : ''}">
                    <div class="ai-finding-number">${index + 1}</div>
                    <p class="ai-finding-text">${escapeHtml(reason)}</p>
                </div>`;
        });
    } else {
        html += `<p style="color: #999; font-style: italic; text-align: center; padding: 20px;">Analysis in progress...</p>`;
    }
    
    html += `</div></div>`;
    
    // Add confidence and risk assessment info in a grid
    if (aiAnalysis.confidence_level || aiAnalysis.risk_assessment) {
        html += `
            <div class="ai-insights-grid">
                ${aiAnalysis.confidence_level ? `
                    <div class="ai-insight-card">
                        <span class="ai-insight-label">🎯 Confidence Level</span>
                        <span class="ai-insight-value">${escapeHtml(aiAnalysis.confidence_level)}</span>
                    </div>
                ` : ''}
                ${aiAnalysis.risk_assessment ? `
                    <div class="ai-insight-card">
                        <span class="ai-insight-label">⚠ Risk Assessment</span>
                        <span class="ai-insight-value">${escapeHtml(aiAnalysis.risk_assessment)}</span>
                    </div>
                ` : ''}
                ${aiAnalysis.detailed_analysis ? `
                    <div class="ai-insight-card">
                        <span class="ai-insight-label">📋 Analysis Method</span>
                        <span class="ai-insight-value">Multi-Model Ensemble + AI Reasoning</span>
                    </div>
                ` : ''}
            </div>`;
    }
    
    // Insert HTML and show
    reasonsContainer.innerHTML = html;
    reasonsContainer.classList.add('ai-analysis-section');
    reasonsContainer.style.display = 'block';
    
    // Make AI analysis section expandable like result cards
    makeElementExpandable(reasonsContainer);
    
    console.log('✓ AI Reasons displayed successfully');
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================
// EXPANDABLE CARDS FUNCTIONALITY
// ============================================

function initializeExpandableCards() {
    // Make result cards expandable with click handlers
    const resultCards = document.querySelectorAll('.result-card');
    
    resultCards.forEach(card => {
        makeElementExpandable(card);
    });
    
    console.log('✓ Expandable cards initialized');
}

function makeElementExpandable(element) {
    if (!element) return;
    
    const h3 = element.querySelector('h3');
    if (!h3) return;
    
    // Mark element as expandable if not already
    if (element.classList.contains('expandable')) {
        return; // Already expandable
    }
    
    element.classList.add('expandable');
    
    // Check if content wrapper already exists
    let content = element.querySelector('.card-content');
    
    if (!content) {
        // Wrap element content in a div for smooth collapsing
        content = document.createElement('div');
        content.className = 'card-content';
        
        // Move all children after h3 into the content div
        while (element.children.length > 1) {
            content.appendChild(element.children[1]);
        }
        
        element.appendChild(content);
    }
    
    // Add click handler to toggle expand/collapse
    h3.style.cursor = 'pointer';
    
    h3.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Toggle collapsed state
        const isCollapsed = element.classList.contains('collapsed');
        element.classList.toggle('collapsed', !isCollapsed);
    });
}

function generateTimelineChart(totalFrames, suspiciousFrames) {
    const canvas = document.getElementById('timelineChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 200;

    const width = canvas.width;
    const height = canvas.height;
    const barWidth = width / totalFrames;

    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Draw frame bars
    for (let i = 0; i < totalFrames; i++) {
        const isSuspicious = Math.random() < (suspiciousFrames / totalFrames);
        const x = i * barWidth;
        
        ctx.fillStyle = isSuspicious ? 'rgba(255, 51, 51, 0.7)' : 'rgba(0, 212, 255, 0.5)';
        ctx.fillRect(x, 50, barWidth - 2, height - 100);
    }

    // Draw labels
    ctx.fillStyle = 'var(--light-text-secondary)';
    ctx.font = '12px sans-serif';
    ctx.fillText('Suspicious', 10, 30);
    ctx.fillText('Normal', width - 50, 30);
}

function generateFramesGallery(suspiciousCount) {
    const gallery = document.getElementById('framesGallery');
    if (!gallery) return;

    gallery.innerHTML = '';

    // Generate frame thumbnails
    for (let i = 0; i < 6; i++) {
        const frameDiv = document.createElement('div');
        frameDiv.className = 'gallery-frame';
        
        const canvas = document.createElement('canvas');
        canvas.width = 120;
        canvas.height = 100;
        const ctx = canvas.getContext('2d');

        // Create random frame visualization
        ctx.fillStyle = `hsl(${Math.random() * 360}, 70%, 50%)`;
        ctx.fillRect(0, 0, 120, 100);

        const isSuspicious = Math.random() < 0.3;
        if (isSuspicious) {
            ctx.fillStyle = 'rgba(255, 51, 51, 0.3)';
            ctx.fillRect(0, 0, 120, 100);
        }

        frameDiv.innerHTML = canvas.toDataURL() 
            ? `<img src="${canvas.toDataURL()}" alt="Frame ${i + 1}">`
            : '<div style="width:120px;height:100px;background:#333"></div>';
        
        const info = document.createElement('div');
        info.className = 'gallery-frame-info';
        if (isSuspicious) {
            info.innerHTML = '<span>SUSPICIOUS</span>';
        } else {
            info.innerHTML = '<span>NORMAL</span>';
        }
        frameDiv.appendChild(info);
        gallery.appendChild(frameDiv);
    }
}

function generateSpectrogram() {
    const canvas = document.getElementById('spectrogramCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 200;

    const width = canvas.width;
    const height = canvas.height;

    // Draw spectrogram visualization
    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;

    for (let i = 0; i < width * height; i++) {
        const x = i % width;
        const y = Math.floor(i / width);
        
        const freq = Math.sin((x / width) * Math.PI * 8) * Math.sin((y / height) * Math.PI);
        const intensity = Math.abs(freq) * 255;

        data[i * 4] = intensity;
        data[i * 4 + 1] = intensity * 0.5;
        data[i * 4 + 2] = intensity * 0.2;
        data[i * 4 + 3] = 255;
    }

    ctx.putImageData(imageData, 0, 0);
}

function generateFrequencyChart() {
    const canvas = document.getElementById('frequencyChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 200;

    const width = canvas.width;
    const height = canvas.height;

    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Draw frequency bars
    const barCount = 20;
    const barWidth = width / barCount;

    ctx.fillStyle = 'var(--gradient-primary)';
    for (let i = 0; i < barCount; i++) {
        const barHeight = Math.sin((i / barCount) * Math.PI) * (height - 40) + 20;
        const x = i * barWidth;
        
        ctx.fillStyle = `hsl(${200 + i * 10}, 100%, 50%)`;
        ctx.fillRect(x, height - barHeight, barWidth - 2, barHeight);
    }

    // Draw axes
    ctx.strokeStyle = 'var(--border-color)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height);
    ctx.lineTo(width, height);
    ctx.stroke();
}

// ============================================
// DOWNLOAD REPORT
// ============================================

function downloadReport() {
    const fileName = document.getElementById('reportFileName').textContent;
    const fileSize = document.getElementById('reportFileSize').textContent;
    const analysisTime = document.getElementById('reportTime').textContent;
    const recommendation = document.getElementById('reportRecommendation').textContent;
    const trustScore = document.getElementById('trustPercentage').textContent;

    const report = `
DeepShield - Analysis Report
============================

File: ${fileName}
File Size: ${fileSize}
Analysis Time: ${analysisTime}

RESULTS
-------
Trust Score: ${trustScore}
Recommendation: ${recommendation}

Models Used:
- MTCNN (Face Detection)
- XceptionNet (Deepfake Detection)
${detectionType === 'audio' ? '- MFCC Feature Extraction' : ''}
${detectionType === 'audio' ? '- Audio CNN' : ''}

Generated by DeepShield - Advanced Deepfake Detection System
    `;

    const blob = new Blob([report], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deepshield-report-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ============================================
// ANALYZE ANOTHER
// ============================================

function analyzeAnother() {
    clearFile();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// NAVIGATION & NAVBAR SETUP
// ============================================

function initializeNavbar() {
    const navbar = document.querySelector('.navbar');
    const token = localStorage.getItem('authToken');
    const userEmail = localStorage.getItem('userEmail');
    const profileLink = document.getElementById('profileLink');
    const navLinks = document.querySelector('.nav-links');
    
    if (!navbar) return;

    // Handle scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    if (!profileLink || !navLinks) return;
    
    // Remove existing logout button if any
    const existingLogout = document.getElementById('logoutBtn');
    if (existingLogout) existingLogout.remove();
    
    if (token && userEmail) {
        // Show profile link with user email
        profileLink.style.display = 'block';
        profileLink.innerHTML = `<span class="nav-icon">👤</span> Profile`;
        
        // Create logout button
        const logoutLi = document.createElement('li');
        logoutLi.innerHTML = `<a href="#" id="logoutBtn" class="logout-link">🚪 Logout</a>`;
        navLinks.appendChild(logoutLi);
        
        // Logout functionality
        document.getElementById('logoutBtn').addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            window.location.href = 'login.html';
        });
    } else {
        // Hide profile link if not logged in
        profileLink.style.display = 'none';
    }
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const currentPath = window.location.pathname;
        
        // Check if this link matches the current page
        if (href && (
            currentPath.endsWith(href) || 
            currentPath.endsWith(href.split('#')[0])
        )) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ============================================
// SMOOTH SCROLL
// ============================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// ENHANCED ANIMATIONS & EFFECTS
// ============================================

// Scroll animation observer for elements
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all feature cards, model cards, etc.
document.querySelectorAll('.feature-card, .model-card, .workflow-step, .info-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// Enhanced drag and drop with visual feedback
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('dragenter', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
            this.style.borderWidth = '3px';
            createParticleEffect(e.clientX, e.clientY);
        });

        uploadArea.addEventListener('dragleave', function(e) {
            if (e.target === this) {
                this.classList.remove('drag-over');
                this.style.borderWidth = '2px';
            }
        });
    }
});

// Particle effect for drag and drop
function createParticleEffect(x, y) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: fixed;
        left: ${x}px;
        top: ${y}px;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        animation: particle-float 0.8s ease-out forwards;
    `;
    document.body.appendChild(particle);
    setTimeout(() => particle.remove(), 800);
}

// Animated counter for statistics
function countUpTo(element, target, duration = 1000) {
    if (!element || isNaN(target)) return;
    
    const start = 0;
    const range = target - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const counter = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = Math.floor(target);
            clearInterval(counter);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Floating animation for upload icon
const uploadIcon = document.querySelector('.upload-icon');
if (uploadIcon) {
    uploadIcon.style.animation = 'pulse 2s ease-in-out infinite';
}

// Button ripple effect
function addRippleEffect(button) {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
            animation: ripple 0.6s ease-out;
        `;

        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
}

// Apply ripple effect to all buttons
document.querySelectorAll('.btn').forEach(btn => {
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    addRippleEffect(btn);
});

// Enhanced success notification with animation
function showSuccessWithAnimation(message) {
    const alert = document.createElement('div');
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #00D084 0%, #00A86B 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 10px 30px rgba(0, 208, 132, 0.3);
        font-weight: 500;
    `;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.4s ease-in';
        setTimeout(() => alert.remove(), 400);
    }, 3000);
}

// Tab switching animations
function switchTab(tabName, event) {
    if (event) event.preventDefault();
    
    const tabs = document.querySelectorAll('.tab-pane');
    const buttons = document.querySelectorAll('[data-tab]');
    
    tabs.forEach(tab => {
        if (tab.id === tabName) {
            tab.style.display = 'block';
            tab.style.animation = 'fadeInUp 0.4s ease-out';
        } else {
            tab.style.display = 'none';
        }
    });
    
    buttons.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Smooth page transition
function transitionToPage(url) {
    document.body.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

// Loading bar effect
function showLoadingBar() {
    let bar = document.getElementById('loadingBar');
    if (!bar) {
        bar = document.createElement('div');
        bar.id = 'loadingBar';
        bar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #0066ff 0%, #00d4ff 100%);
            z-index: 9999;
            animation: expandWidth 0.8s ease-out forwards;
        `;
        document.body.appendChild(bar);
    }
    
    setTimeout(() => {
        bar.style.opacity = '0';
        bar.style.transition = 'opacity 0.3s ease-in';
        setTimeout(() => bar?.remove(), 300);
    }, 800);
}

// Typewriter effect for headings
function typewriterEffect(element, text, speed = 50) {
    if (!element) return;
    element.textContent = '';
    let index = 0;
    
    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Add glitch effect on hover for titles
document.querySelectorAll('h1, h2, h3').forEach(heading => {
    heading.addEventListener('mouseenter', function() {
        this.style.animation = 'glitch 0.3s ease-out';
    });
});

// Parallax scroll effect
document.addEventListener('scroll', function() {
    const shapes = document.querySelectorAll('.shape');
    const scrollY = window.pageYOffset;
    
    shapes.forEach((shape, index) => {
        const speed = 0.5 + (index * 0.1);
        shape.style.transform = `translateY(${scrollY * speed}px)`;
    });
});

// Animated progress indicator
function updateProgressIndicator(current, total) {
    let indicator = document.getElementById('progressIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'progressIndicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 102, 255, 0.4);
        `;
        document.body.appendChild(indicator);
    }
    
    const percentage = Math.round((current / total) * 100);
    indicator.textContent = percentage + '%';
}

// Confetti effect for success
function celebrationConfetti() {
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        const size = Math.random() * 10 + 5;
        const duration = Math.random() * 3 + 2;
        
        confetti.style.cssText = `
            position: fixed;
            width: ${size}px;
            height: ${size}px;
            background: hsl(${Math.random() * 360}, 100%, 50%);
            left: ${Math.random() * 100}%;
            top: -10px;
            z-index: 9999;
            border-radius: ${Math.random() > 0.5 ? '50%' : '0%'};
            animation: fall ${duration}s linear forwards;
        `;
        
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), duration * 1000);
    }
}

// Scroll to top button with animation
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '↑';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        font-size: 24px;
        opacity: 0;
        transition: all 0.3s ease-out;
        z-index: 999;
        box-shadow: 0 4px 15px rgba(0, 102, 255, 0.4);
    `;
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.style.opacity = '1';
            button.style.visibility = 'visible';
        } else {
            button.style.opacity = '0';
            button.style.visibility = 'hidden';
        }
    });
    
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    button.addEventListener('mouseenter', function() {
        this.style.animation = 'bounce 0.6s ease-in-out';
    });
    
    document.body.appendChild(button);
}

// Initialize scroll to top button
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createScrollToTopButton);
} else {
    createScrollToTopButton();
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        clearError();
    }
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        downloadReport();
    }
});

// Loading state feedback
let isLoading = false;

function setLoadingState(loading) {
    isLoading = loading;
    const buttons = document.querySelectorAll('.btn:not(.btn-secondary)');
    buttons.forEach(btn => {
        if (loading) {
            btn.disabled = true;
            btn.style.opacity = '0.6';
        } else {
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    });
}

// Add visual feedback on file selection
document.addEventListener('change', function(e) {
    if (e.target.type === 'file' && e.target.files.length > 0) {
        showSuccessWithAnimation(`📁 ${e.target.files[0].name} selected!`);
    }
});

// Animated tooltip
function addTooltip(element, text) {
    element.addEventListener('mouseenter', function() {
        const tooltip = document.createElement('div');
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            pointer-events: none;
            animation: fadeInUp 0.3s ease-out;
            z-index: 1000;
        `;
        
        const rect = this.getBoundingClientRect();
        tooltip.style.left = (rect.left + rect.width / 2 - 50) + 'px';
        tooltip.style.top = (rect.top - 40) + 'px';
        
        document.body.appendChild(tooltip);
        
        this.addEventListener('mouseleave', () => tooltip.remove(), { once: true });
    });
}

// Apply tooltips to important elements
document.querySelectorAll('[title]').forEach(el => {
    addTooltip(el, el.getAttribute('title'));
});

// Number counter animation for statistics
function animateNumbers() {
    const numbers = document.querySelectorAll('[data-count]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                const target = parseInt(entry.target.dataset.count);
                countUpTo(entry.target, target, 1000);
                entry.target.dataset.counted = 'true';
            }
        });
    });
    
    numbers.forEach(num => observer.observe(num));
}

// Initialize number animations
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateNumbers);
} else {
    animateNumbers();
}

// ============================================
// FEEDBACK FORM FUNCTIONALITY
// ============================================

let feedbackAttachment = null;
let authenticatedUserEmail = null;

// Initialize feedback form
function initializeFeedbackForm() {
    console.log('=== INITIALIZING FEEDBACK FORM ===');
    
    // Check if user is authenticated
    const token = localStorage.getItem('authToken') || localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    
    console.log('Token exists:', !!token);
    console.log('User email in localStorage:', userEmail);
    
    // If not logged in, show message and redirect
    if (!token || !userEmail) {
        console.warn('⚠️  User not authenticated');
        const feedbackForm = document.getElementById('feedbackForm');
        if (feedbackForm) {
            feedbackForm.style.display = 'none';
        }
        
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.style.display = 'block';
            document.getElementById('errorText').textContent = 'You must be logged in to submit feedback. Redirecting to login...';
        }
        
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }
    
    // Set authenticated user email
    authenticatedUserEmail = userEmail;
    console.log('✓ User authenticated:', authenticatedUserEmail);
    
    // Display user email
    document.getElementById('userEmail').value = authenticatedUserEmail;
    document.getElementById('userEmailText').textContent = authenticatedUserEmail;
    
    const uploadArea = document.querySelector('.feedback-upload-area');
    const messageTextarea = document.getElementById('message');
    
    if (!uploadArea || !messageTextarea) {
        console.error('❌ Required DOM elements not found');
        return;
    }
    
    // File upload handler
    uploadArea.addEventListener('click', () => {
        document.getElementById('attachment').click();
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#00d4ff';
        uploadArea.style.background = 'rgba(0, 212, 255, 0.1)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'rgba(0, 212, 255, 0.3)';
        uploadArea.style.background = 'rgba(0, 0, 0, 0.2)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'rgba(0, 212, 255, 0.3)';
        uploadArea.style.background = 'rgba(0, 0, 0, 0.2)';
        
        if (e.dataTransfer.files.length > 0) {
            handleFeedbackFileSelection(e.dataTransfer.files[0]);
        }
    });
    
    // File input change
    document.getElementById('attachment').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFeedbackFileSelection(e.target.files[0]);
        }
    });
    
    // Character counter
    messageTextarea.addEventListener('input', (e) => {
        const count = e.target.value.length;
        document.getElementById('charCount').textContent = `${count} / 2000 characters`;
    });
    
    console.log('✓ Feedback form initialized');
}

function handleFeedbackFileSelection(file) {
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    console.log('File selected:', file.name, 'Size:', file.size);
    
    if (file.size > maxSize) {
        showErrorAlert(`File is too large. Maximum size is 5MB.`);
        return;
    }
    
    feedbackAttachment = file;
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    
    fileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    fileInfo.style.display = 'block';
    document.querySelector('.feedback-upload-area').style.display = 'none';
    
    console.log('✓ File selected:', file.name);
}

function clearFeedbackFile() {
    feedbackAttachment = null;
    document.getElementById('attachment').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.querySelector('.feedback-upload-area').style.display = 'block';
    console.log('✓ File cleared');
}

async function submitFeedback(event) {
    event.preventDefault();
    console.log('=== SUBMITTING FEEDBACK ===');
    
    const feedbackType = document.getElementById('feedbackType').value;
    const subject = document.getElementById('subject').value.trim();
    const userEmail = document.getElementById('userEmail').value.trim();
    const message = document.getElementById('message').value.trim();
    const sendCopy = document.getElementById('sendCopy').checked;
    
    console.log('Form data:', {
        feedbackType,
        subject,
        userEmail,
        messageLength: message.length,
        sendCopy,
        hasAttachment: !!feedbackAttachment
    });
    
    // Validation
    if (!feedbackType || !subject || !userEmail || !message) {
        console.warn('⚠️  Missing required fields');
        showErrorAlert('Please fill in all required fields.');
        return;
    }
    
    // Email validation - simple check
    console.log('📧 Validating email:', userEmail, 'Length:', userEmail.length);
    const hasAtSign = userEmail.includes('@');
    const hasDot = userEmail.includes('.');
    const atIndex = userEmail.indexOf('@');
    const dotIndex = userEmail.lastIndexOf('.');
    const isValidEmail = hasAtSign && hasDot && atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < userEmail.length - 1;
    
    console.log('Email validation:', {hasAtSign, hasDot, atIndex, dotIndex, isValidEmail});
    
    if (!isValidEmail) {
        console.warn('⚠️  Invalid email format');
        showErrorAlert('Please enter a valid email address.');
        return;
    }
    
    // Show loading spinner
    const feedbackForm = document.getElementById('feedbackForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    
    feedbackForm.style.display = 'none';
    loadingSpinner.style.display = 'flex';
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('feedbackType', feedbackType);
        formData.append('subject', subject);
        formData.append('email', userEmail);
        formData.append('message', message);
        formData.append('sendCopy', sendCopy);
        
        if (feedbackAttachment) {
            formData.append('attachment', feedbackAttachment);
            console.log('📎 Attaching file:', feedbackAttachment.name);
        }
        
        console.log('📤 Sending feedback to backend...');
        
        // Submit to backend
        const response = await fetch(getApiUrl('/api/feedback/submit'), {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': localStorage.getItem('authToken') || localStorage.getItem('token') || ''
            }
        });
        
        console.log('📥 Response status:', response.status);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to submit feedback');
        }
        
        // Success
        loadingSpinner.style.display = 'none';
        successMessage.style.display = 'block';
        console.log('✅ Feedback submitted successfully');
        console.log('Feedback ID:', data.feedback_id);
        
    } catch (error) {
        console.error('❌ Feedback submission error:', error);
        loadingSpinner.style.display = 'none';
        errorMessage.style.display = 'block';
        document.getElementById('errorText').textContent = error.message || 'An error occurred while submitting your feedback. Please try again.';
        feedbackForm.style.display = 'block';
    }
}

function showErrorAlert(message) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        document.getElementById('errorText').textContent = message;
        errorMessage.style.display = 'block';
    }
    window.scrollTo(0, 0);
}

function hideErrorMessage() {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
}

function resetForm() {
    document.getElementById('feedbackForm').reset();
    feedbackAttachment = null;
    clearFeedbackFile();
    document.getElementById('feedbackForm').style.display = 'block';
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('charCount').textContent = '0 / 2000 characters';
    window.scrollTo(0, 0);
    console.log('✓ Form reset');
}

// Initialize feedback form when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.location.pathname.includes('feedback')) {
            console.log('📝 Feedback page detected, initializing...');
            initializeFeedbackForm();
        }
    });
} else {
    if (window.location.pathname.includes('feedback')) {
        console.log('📝 Feedback page detected, initializing...');
        initializeFeedbackForm();
    }
}


