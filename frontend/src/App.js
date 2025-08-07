import React, { useState } from 'react';
import './App.css';
import { FiCopy } from 'react-icons/fi';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [status, setStatus] = useState('');
  const [transcript, setTranscript] = useState('');

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files).slice(0, 50); // Limit to 50
    setSelectedFiles(files);
    setStatus(`Selected ${files.length} file(s)`);
  };

  const handleUploadClick = () => {
    document.getElementById('fileInput').click();
  };

  const handleTranscribe = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select at least one file.');
      return;
    }

    setStatus('Processing...');
    const formData = new FormData();
    selectedFiles.forEach(file => formData.append('files', file));

    try {
      const response = await fetch('http://localhost:8000/transcribe/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transcription failed');

      const data = await response.json();
      setTranscript(data.transcript);
      setStatus('Done!');
    } catch (error) {
      setStatus('Error: ' + error.message);
    }
  };

  const handleDownload = () => {
    if (!transcript) return;
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcriptions.txt';
    a.click();
  };

  const handleCopy = () => {
    if (transcript) {
      navigator.clipboard.writeText(transcript);
      setStatus('Copied to clipboard!');
      setTimeout(() => setStatus('Done!'), 1500);
    }
  };

  return (
    <div className="App">
      <header>
        <img src="/eoxs-erp.webp" alt="Eoxs Logo" className="logo-header" />
      </header>

      <div className="container">
        <h1>Transcribe Audio to Text</h1>
        <p>Upload up to 50 audio files and get the combined transcription.</p>

        <div className="upload-card">
          <h2>Upload your files</h2>
          <p>Select multiple audio files from your system.</p>
          <input
            type="file"
            id="fileInput"
            accept="audio/*"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <button onClick={handleUploadClick}>Choose Files</button>

          {selectedFiles.length > 0 && (
            <div className="file-selected-msg">
              Selected: {selectedFiles.map(f => f.name).join(', ')}
            </div>
          )}
        </div>

        <button onClick={handleTranscribe}>Transcribe</button>
        <button onClick={handleDownload} disabled={!transcript}>
          Download Output
        </button>

        {status && !status.startsWith('Selected:') && (
          <div id="status">{status}</div>
        )}

        {transcript && (
          <div className="transcript-box">
            <div className="transcript-header">
              <h2>Transcript</h2>
              <button className="copy-btn" onClick={handleCopy} title="Copy to clipboard">
                <FiCopy size={18} />
              </button>
            </div>
            <pre>{transcript}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
