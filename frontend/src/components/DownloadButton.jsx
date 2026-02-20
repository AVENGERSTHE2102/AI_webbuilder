import React, { useState } from 'react';
import './DownloadButton.css';

function DownloadButton({ appId }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);

    try {
      const downloadUrl = `http://localhost:8000/api/download/${appId}`;

      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${appId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log('Download initiated for:', appId);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      // Reset after a short delay
      setTimeout(() => setDownloading(false), 1000);
    }
  };

  return (
    <button
      className="download-btn"
      onClick={handleDownload}
      disabled={downloading}
    >
      {downloading ? (
        <>
          <span className="download-spinner"></span>
          Downloading...
        </>
      ) : (
        <>
          📥 Download ZIP
        </>
      )}
    </button>
  );
}

export default DownloadButton;
