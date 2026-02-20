import React, { useState, useEffect, useRef } from 'react';
import './LivePreview.css';

/**
 * LivePreview - Renders generated apps in an iframe with auto-debugging
 *
 * Features:
 * - Live preview of generated React apps
 * - Automatic error detection and display
 * - Console log capture
 * - Hot reload support
 */
function LivePreview({ files, appId }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [logs, setLogs] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const iframeRef = useRef(null);

  useEffect(() => {
    if (files) {
      generatePreview();
    }
  }, [files]);

  const generatePreview = async () => {
    setLoading(true);
    setErrors([]);
    setLogs([]);

    try {
      // Create a self-contained HTML with the React app
      const previewHtml = createPreviewHTML(files);

      // Create blob URL for iframe
      const blob = new Blob([previewHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);

      setPreviewUrl(url);
      addLog('Preview generated successfully', 'success');

    } catch (error) {
      addError('Failed to generate preview: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const createPreviewHTML = (files) => {
    // Extract code from files
    const appJsx = files['frontend/src/App.jsx'] || '';
    const appCss = files['frontend/src/App.css'] || '';

    // Parse the JSX to extract component code
    const componentCode = extractComponentCode(appJsx);

    // Create self-contained HTML with inline React
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Live Preview</title>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.7/axios.min.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
    }
    ${appCss}
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect } = React;

    // Override console to send logs to parent
    const originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn
    };

    console.log = (...args) => {
      originalConsole.log(...args);
      window.parent.postMessage({ type: 'console', level: 'log', data: args }, '*');
    };

    console.error = (...args) => {
      originalConsole.error(...args);
      window.parent.postMessage({ type: 'console', level: 'error', data: args }, '*');
    };

    console.warn = (...args) => {
      originalConsole.warn(...args);
      window.parent.postMessage({ type: 'console', level: 'warn', data: args }, '*');
    };

    // Global error handler
    window.addEventListener('error', (event) => {
      window.parent.postMessage({
        type: 'error',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }, '*');
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      window.parent.postMessage({
        type: 'error',
        message: 'Unhandled Promise Rejection: ' + event.reason
      }, '*');
    });

    try {
      ${componentCode}

      // Render the app
      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<App />);

      window.parent.postMessage({ type: 'ready' }, '*');
      console.log('✅ App rendered successfully');

    } catch (error) {
      console.error('Failed to render app:', error);
      document.getElementById('root').innerHTML =
        '<div style="padding: 40px; background: white; margin: 20px; border-radius: 12px;">' +
        '<h2 style="color: #c33;">Preview Error</h2>' +
        '<p style="margin-top: 10px; color: #666;">' + error.message + '</p>' +
        '</div>';
    }
  </script>
</body>
</html>
    `;
  };

  const extractComponentCode = (appJsx) => {
    // Remove all import statements (including multi-line)
    let code = appJsx;

    // Remove single-line imports: import ... from '...'
    code = code.replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '');

    // Remove CSS imports: import './App.css'
    code = code.replace(/import\s+['"].*?\.css['"];?\s*/g, '');

    // Remove any remaining import statements
    code = code.replace(/import\s+.*?;?\s*/g, '');

    // Remove export default and export statements
    code = code.replace(/export\s+default\s+App;?/g, '');
    code = code.replace(/export\s+default\s+/g, '');
    code = code.replace(/export\s+\{.*?\};?/g, '');

    // Replace API_BASE_URL with localhost
    code = code.replace(/const API_BASE_URL\s*=\s*.*?;/,
      "const API_BASE_URL = 'http://localhost:8000';");

    // Clean up extra whitespace
    code = code.replace(/^\s*[\r\n]/gm, '');

    return code.trim();
  };

  const addLog = (message, level = 'info') => {
    setLogs(prev => [...prev, {
      message,
      level,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const addError = (message) => {
    setErrors(prev => [...prev, {
      message,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  // Listen for messages from iframe
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data.type === 'console') {
        const message = event.data.data.map(arg =>
          typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        addLog(message, event.data.level);
      } else if (event.data.type === 'error') {
        addError(event.data.message);
      } else if (event.data.type === 'ready') {
        addLog('Preview loaded successfully', 'success');
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleRefresh = () => {
    if (iframeRef.current) {
      iframeRef.current.src = previewUrl;
      setLogs([]);
      setErrors([]);
      addLog('Preview refreshed', 'info');
    }
  };

  const clearLogs = () => {
    setLogs([]);
    setErrors([]);
  };

  return (
    <div className="live-preview">
      {/* Preview Header */}
      <div className="preview-header">
        <div className="header-left">
          <span className="preview-title">🔴 Live Preview</span>
          {!loading && <span className="preview-status">Running</span>}
        </div>
        <div className="header-right">
          <button onClick={handleRefresh} className="refresh-btn" disabled={loading}>
            🔄 Refresh
          </button>
          <button onClick={clearLogs} className="clear-btn">
            🗑️ Clear Logs
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="preview-content">
        {/* App Preview */}
        <div className="preview-frame-container">
          {loading && (
            <div className="preview-loading">
              <div className="loading-spinner"></div>
              <p>Generating preview...</p>
            </div>
          )}

          {previewUrl && (
            <iframe
              ref={iframeRef}
              src={previewUrl}
              className="preview-frame"
              title="Live Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          )}
        </div>

        {/* Debug Console */}
        <div className="debug-console">
          <div className="console-header">
            <span className="console-title">🐛 Debug Console</span>
            <div className="console-stats">
              <span className="stat-badge error-badge">{errors.length} errors</span>
              <span className="stat-badge log-badge">{logs.length} logs</span>
            </div>
          </div>

          <div className="console-content">
            {/* Errors Section */}
            {errors.length > 0 && (
              <div className="console-section">
                <div className="section-header error-header">❌ Errors</div>
                {errors.map((error, index) => (
                  <div key={index} className="console-entry error-entry">
                    <span className="entry-time">{error.timestamp}</span>
                    <span className="entry-message">{error.message}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Logs Section */}
            {logs.length > 0 && (
              <div className="console-section">
                <div className="section-header">📋 Console Logs</div>
                {logs.map((log, index) => (
                  <div
                    key={index}
                    className={`console-entry ${log.level}-entry`}
                  >
                    <span className="entry-time">{log.timestamp}</span>
                    <span className="entry-message">{log.message}</span>
                  </div>
                ))}
              </div>
            )}

            {errors.length === 0 && logs.length === 0 && (
              <div className="console-empty">
                <p>No logs or errors yet. Try interacting with the preview above.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Auto-Debug Tips */}
      {errors.length > 0 && (
        <div className="debug-tips">
          <div className="tips-header">💡 Auto-Debug Suggestions</div>
          <ul className="tips-list">
            <li>Check if the backend is running at http://localhost:8000</li>
            <li>Verify CORS is enabled in the backend</li>
            <li>Look for JavaScript errors in the console above</li>
            <li>Try refreshing the preview</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default LivePreview;
