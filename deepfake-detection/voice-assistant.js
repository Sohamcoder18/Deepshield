/**
 * Voice Assistant Module
 * Handles speech-to-text and text-to-speech functionality
 * Integrates with the backend voice API endpoints
 */

class VoiceAssistant {
    constructor(apiBaseUrl = '') {
        this.apiBaseUrl = apiBaseUrl || getApiUrl('');
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.audioContext = null;
        this.recognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        this.speechSynthesisSupported = 'speechSynthesis' in window;
        this.conversationHistory = [];
        
        // Callbacks
        this.onRecordingStart = null;
        this.onRecordingStop = null;
        this.onTranscriptionComplete = null;
        this.onSpeechStart = null;
        this.onSpeechComplete = null;
        this.onError = null;
    }

    /**
     * Check if voice features are available
     */
    async checkVoiceAvailability() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/voice/status`);
            if (response.ok) {
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.error('Error checking voice availability:', error);
        }
        return { voice_available: false, groq_available: false, status: 'unavailable' };
    }

    /**
     * Request microphone access and start recording
     */
    async startRecording() {
        try {
            if (this.isRecording) {
                console.warn('Already recording');
                return;
            }

            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(this.stream);

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                // Audio recording complete
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            if (this.onRecordingStart) {
                this.onRecordingStart();
            }

            console.log('🎤 Recording started...');

        } catch (error) {
            console.error('Error starting recording:', error);
            if (this.onError) {
                this.onError(`Microphone access denied: ${error.message}`);
            }
        }
    }

    /**
     * Stop recording and return audio blob
     */
    stopRecording() {
        return new Promise((resolve) => {
            if (!this.isRecording || !this.mediaRecorder) {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = async () => {
                this.isRecording = false;

                // Stop all tracks
                if (this.stream) {
                    this.stream.getTracks().forEach(track => track.stop());
                    this.stream = null;
                }

                if (this.onRecordingStop) {
                    this.onRecordingStop();
                }

                console.log('🛑 Recording stopped');

                // Convert audio chunks to proper WAV format
                try {
                    const audioBlob = this.convertToWAV(this.audioChunks);
                    resolve(audioBlob);
                } catch (error) {
                    console.error('Error converting audio to WAV:', error);
                    // Fallback: return raw blob
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
                    resolve(audioBlob);
                }
            };

            this.mediaRecorder.stop();
        });
    }

    /**
     * Convert recorded chunks to WAV format
     */
    convertToWAV(chunks) {
        const blob = new Blob(chunks, { type: this.mediaRecorder.mimeType || 'audio/webm' });
        return blob;
    }

    /**
     * Transcribe audio file to text
     */
    async transcribeAudio(audioBlob, language = 'en-US') {
        try {
            if (!audioBlob) {
                throw new Error('No audio blob provided');
            }

            const formData = new FormData();
            
            // Normalize language code for backend (e.g., en-US -> en)
            const normalizedLanguage = language.split('-')[0].toLowerCase() || 'en';
            
            // Send with proper filename and type
            const filename = `audio_${Date.now()}.webm`;
            formData.append('audio', audioBlob, filename);
            formData.append('language', normalizedLanguage);
            formData.append('mime_type', audioBlob.type || 'audio/webm');

            console.log(`📤 Uploading audio (${(audioBlob.size / 1024).toFixed(2)}KB, ${audioBlob.type})`);

            const response = await fetch(`${this.apiBaseUrl}/api/voice/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.error || `Transcription failed: ${response.status}`);
                } catch (e) {
                    throw new Error(`Transcription failed: ${errorText || response.statusText}`);
                }
            }

            const data = await response.json();
            console.log('✓ Transcription:', data.text);

            if (this.onTranscriptionComplete) {
                this.onTranscriptionComplete(data.text);
            }

            return data.text;

        } catch (error) {
            console.error('Transcription error:', error);
            if (this.onError) {
                this.onError(`Transcription error: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Convert text to speech
     */
    async textToSpeech(text, format = 'wav') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/voice/speak`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    format: format
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Text-to-speech failed');
            }

            const audioBlob = await response.blob();
            return audioBlob;

        } catch (error) {
            console.error('Text-to-speech error:', error);
            if (this.onError) {
                this.onError(`Text-to-speech error: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Play audio blob
     */
    async playAudio(audioBlob) {
        try {
            const url = URL.createObjectURL(audioBlob);
            const audio = new Audio(url);

            if (this.onSpeechStart) {
                this.onSpeechStart();
            }

            audio.onended = () => {
                URL.revokeObjectURL(url);
                if (this.onSpeechComplete) {
                    this.onSpeechComplete();
                }
            };

            audio.onerror = (error) => {
                console.error('Audio playback error:', error);
                URL.revokeObjectURL(url);
                if (this.onError) {
                    this.onError(`Audio playback error: ${error}`);
                }
            };

            const playPromise = audio.play();
            if (playPromise !== undefined) {
                await playPromise.catch(error => {
                    console.error('Audio play error:', error);
                    if (this.onError) {
                        this.onError(`Audio play error: ${error.message}`);
                    }
                });
            }
            console.log('🔊 Playing audio response...');

        } catch (error) {
            console.error('Error playing audio:', error);
            if (this.onError) {
                this.onError(`Error playing audio: ${error.message}`);
            }
        }
    }

    /**
     * Full voice chat interaction
     */
    async voiceChat(audioBlob, language = 'en-US', format = 'wav', analysisId = null) {
        try {
            if (!audioBlob) {
                throw new Error('No audio blob provided');
            }

            const formData = new FormData();
            
            // Normalize language code for backend (e.g., en-US -> en)
            const normalizedLanguage = language.split('-')[0].toLowerCase() || 'en';
            
            const filename = `audio_${Date.now()}.webm`;
            formData.append('audio', audioBlob, filename);
            formData.append('language', normalizedLanguage);
            formData.append('format', format);
            formData.append('mime_type', audioBlob.type || 'audio/webm');
            
            if (this.conversationHistory.length > 0) {
                formData.append('history', JSON.stringify(this.conversationHistory));
            }
            
            if (analysisId) {
                formData.append('analysis_id', analysisId);
            }

            console.log(`📤 Starting voice chat (${(audioBlob.size / 1024).toFixed(2)}KB, language: ${normalizedLanguage})`);

            const response = await fetch(`${this.apiBaseUrl}/api/voice/chat`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Voice chat HTTP error:', response.status, errorText);
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.error || `Voice chat failed: ${response.status}`);
                } catch (e) {
                    throw new Error(`Voice chat failed: ${errorText || response.statusText}`);
                }
            }

            console.log('📨 Response received, parsing JSON...');
            const data = await response.json();
            console.log('📨 JSON parsed successfully');
            console.log('📨 Received response from voice chat endpoint:', data);
            console.log('📨 Response includes:', {
                hasStatus: !!data.status,
                hasUserText: !!data.user_text,
                hasAssistantText: !!data.assistant_text,
                hasAudioBase64: !!data.audio_base64
            });

            // Validate response
            if (!data.user_text || !data.assistant_text) {
                console.warn('❌ Response missing required fields:', data);
                throw new Error('Invalid response format from voice chat endpoint');
            }

            // Add to conversation history
            this.conversationHistory.push({
                role: 'user',
                content: data.user_text
            });
            this.conversationHistory.push({
                role: 'assistant',
                content: data.assistant_text
            });

            console.log('✓ Voice Chat Response:');
            console.log('  User:', data.user_text);
            console.log('  Assistant:', data.assistant_text);
            console.log('  Audio included:', !!data.audio_base64);

            // Decode and play audio response
            if (data.audio_base64) {
                try {
                    console.log('🔄 Converting audio from base64...');
                    const audioBlob = this.base64ToBlob(data.audio_base64, `audio/${format}`);
                    console.log('✓ Audio blob created, size:', audioBlob.size, 'bytes');
                    await this.playAudio(audioBlob);
                } catch (audioError) {
                    console.error('❌ Error processing audio:', audioError);
                    if (this.onError) {
                        this.onError(`Error processing audio: ${audioError.message}`);
                    }
                    // Don't throw - continue even if audio playback fails
                }
            }

            console.log('✓ Voice chat completed successfully');
            return data;

        } catch (error) {
            console.error('Voice chat error:', error);
            if (this.onError) {
                this.onError(`Voice chat error: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Convert base64 to blob
     */
    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimeType });
    }

    /**
     * Use Web Speech API for recognition (alternative to server-side)
     */
    async startWebRecognition(language = 'en-US') {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            if (this.onError) {
                this.onError('Speech Recognition API not supported in this browser');
            }
            return null;
        }

        return new Promise((resolve, reject) => {
            const recognition = new SpeechRecognition();
            recognition.language = language;
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                console.log('🎤 Web Speech Recognition started');
                if (this.onRecordingStart) {
                    this.onRecordingStart();
                }
            };

            recognition.onend = () => {
                console.log('🛑 Web Speech Recognition ended');
                if (this.onRecordingStop) {
                    this.onRecordingStop();
                }
            };

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                console.log('✓ Recognized:', transcript);
                resolve(transcript);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                if (this.onError) {
                    this.onError(`Speech recognition error: ${event.error}`);
                }
                reject(new Error(event.error));
            };

            recognition.start();
        });
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
        console.log('Conversation history cleared');
    }

    /**
     * Get conversation history
     */
    getHistory() {
        return this.conversationHistory;
    }
}

// Export for use in HTML
if (typeof window !== 'undefined') {
    window.VoiceAssistant = VoiceAssistant;
}
