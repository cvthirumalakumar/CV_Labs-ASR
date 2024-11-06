// frontend/src/App.js

import React, { useState } from 'react';
import axios from 'axios';
import { AudioRecorder } from 'react-audio-voice-recorder';

function App() {
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [loading, setLoading] = useState(false);

  // Callback function to handle the completed recording
  const handleRecordingComplete = (recordedBlob) => {
    setAudioBlob(recordedBlob);
  };

  // Upload audio to the backend for transcription
  const uploadAudio = async () => {
    if (!audioBlob) {
      alert("Please record audio before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append('audio', audioBlob);

    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/upload-audio', formData);
      setTranscription(response.data.transcription);
      console.log(response.data.transcription)
    } catch (error) {
      setTranscription('Error transcribing audio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Record Audio for Transcription</h1>
      <AudioRecorder
        onRecordingComplete={handleRecordingComplete}
        mimeType="audio/wav"
        audioTrackConstraints={{
          noiseSuppression: true,
          echoCancellation: true,
        }}
      />
      
      {audioBlob && (
        <div>
          <audio controls src={URL.createObjectURL(audioBlob)}></audio>
          <button onClick={uploadAudio}>Upload & Transcribe</button>
        </div>
      )}

      {loading ? (
        <p>Transcribing...</p>
      ) : (
        transcription && <p><strong>Transcription:</strong> {transcription}</p>
      )}
    </div>
  );
}

export default App;
