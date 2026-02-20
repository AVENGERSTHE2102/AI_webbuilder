import React, { useState } from 'react';
import './CodeViewer.css';

function CodeViewer({ files }) {
  const [selectedFile, setSelectedFile] = useState(Object.keys(files)[0] || '');

  const fileCategories = {
    'Backend': Object.keys(files).filter(f => f.startsWith('backend/')),
    'Frontend': Object.keys(files).filter(f => f.startsWith('frontend/')),
    'Documentation': Object.keys(files).filter(f => f.endsWith('.md')),
  };

  const getLanguage = (filename) => {
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.jsx') || filename.endsWith('.js')) return 'javascript';
    if (filename.endsWith('.json')) return 'json';
    if (filename.endsWith('.css')) return 'css';
    if (filename.endsWith('.md')) return 'markdown';
    if (filename.endsWith('.html')) return 'html';
    return 'text';
  };

  const getFileName = (path) => {
    const parts = path.split('/');
    return parts[parts.length - 1];
  };

  return (
    <div className="code-viewer">
      {/* File Tree Sidebar */}
      <div className="file-tree">
        <h4>Files</h4>
        {Object.entries(fileCategories).map(([category, filePaths]) => (
          filePaths.length > 0 && (
            <div key={category} className="file-category">
              <div className="category-label">{category}</div>
              <div className="file-list">
                {filePaths.map((filePath) => (
                  <button
                    key={filePath}
                    className={`file-item ${selectedFile === filePath ? 'active' : ''}`}
                    onClick={() => setSelectedFile(filePath)}
                  >
                    <span className="file-icon">📄</span>
                    <span className="file-name">{getFileName(filePath)}</span>
                  </button>
                ))}
              </div>
            </div>
          )
        ))}
      </div>

      {/* Code Display */}
      <div className="code-display">
        <div className="code-header">
          <span className="file-path">{selectedFile}</span>
          <button
            className="copy-btn"
            onClick={() => {
              navigator.clipboard.writeText(files[selectedFile]);
              alert('Copied to clipboard!');
            }}
          >
            📋 Copy
          </button>
        </div>
        <pre className="code-content">
          <code className={`language-${getLanguage(selectedFile)}`}>
            {files[selectedFile]}
          </code>
        </pre>
      </div>
    </div>
  );
}

export default CodeViewer;
