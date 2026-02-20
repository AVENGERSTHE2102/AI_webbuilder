import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CodeViewer from '../components/CodeViewer';
import DownloadButton from '../components/DownloadButton';
import LoadingSpinner from '../components/LoadingSpinner';
import LivePreview from '../components/LivePreview';
import './Builder.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function Builder() {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedApp, setGeneratedApp] = useState(null);
  const [error, setError] = useState(null);
  const [examples, setExamples] = useState([]);
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' or 'code'

  useEffect(() => {
    // Load example templates
    fetchExamples();
  }, []);

  const fetchExamples = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/templates`);
      if (response.data.templates && response.data.templates.length > 0) {
        setExamples(response.data.templates[0].examples || []);
      }
    } catch (err) {
      console.error('Failed to load examples:', err);
    }
  };

  const handleGenerate = async () => {
    if (!description.trim()) {
      setError('Please enter an app description');
      return;
    }

    if (description.length < 10) {
      setError('Description too short. Please be more specific.');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedApp(null);

    try {
      console.log('Generating app from description:', description);

      const response = await axios.post(`${API_BASE}/api/generate`, {
        description: description.trim()
      });

      console.log('App generated successfully:', response.data.app_id);

      setGeneratedApp(response.data);
    } catch (err) {
      console.error('Generation error:', err);

      if (err.response) {
        setError(err.response.data.detail || 'Generation failed. Please try again.');
      } else if (err.request) {
        setError('Cannot connect to server. Make sure the backend is running at http://localhost:8000');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example) => {
    setDescription(example);
    setError(null);
    setGeneratedApp(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleGenerate();
    }
  };

  return (
    <div className="builder-container">
      {/* Header */}
      <header className="builder-header">
        <div className="header-content">
          <h1 className="title">Zero-Code AI App Builder</h1>
          <p className="subtitle">
            Describe your app idea in plain text, get a complete working full-stack application instantly.
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="builder-main">
        {/* Input Section */}
        <section className="input-section">
          <div className="input-container">
            <label htmlFor="description" className="input-label">
              Describe Your App
            </label>
            <textarea
              id="description"
              className="description-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Example: A recipe manager with ingredients and cooking steps..."
              rows={6}
              disabled={loading}
            />
            <div className="input-footer">
              <span className="char-count">
                {description.length}/500 characters
              </span>
              <span className="hint">
                Press Ctrl+Enter to generate
              </span>
            </div>
          </div>

          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={loading || !description.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Generating Your App...
              </>
            ) : (
              <>
                ✨ Generate App
              </>
            )}
          </button>
        </section>

        {/* Examples Section */}
        {!generatedApp && !loading && examples.length > 0 && (
          <section className="examples-section">
            <h3>Try These Examples:</h3>
            <div className="examples-grid">
              {examples.slice(0, 5).map((example, index) => (
                <button
                  key={index}
                  className="example-btn"
                  onClick={() => handleExampleClick(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-section">
            <LoadingSpinner message="Building your app with AI..." />
            <p className="loading-details">
              This usually takes 10-30 seconds. We're:
            </p>
            <ul className="loading-steps">
              <li>Analyzing your description</li>
              <li>Generating backend API</li>
              <li>Creating React frontend</li>
              <li>Packaging everything together</li>
            </ul>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-section">
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <div>
                <strong>Error:</strong> {error}
              </div>
            </div>
            <button
              className="retry-btn"
              onClick={() => setError(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Success: Generated App */}
        {generatedApp && !loading && (
          <div className="success-section">
            <div className="success-header">
              <div className="success-icon">🎉</div>
              <div>
                <h2>Your App is Ready!</h2>
                <p className="success-subtitle">
                  Generated: <strong>{generatedApp.metadata.entity_name} Manager</strong>
                  {' '}with {generatedApp.metadata.field_count} fields
                </p>
              </div>
            </div>

            {/* Download Section */}
            <div className="download-section">
              <DownloadButton appId={generatedApp.app_id} />
              <p className="download-hint">
                Download includes complete frontend + backend code, ready to run locally.
              </p>
            </div>

            {/* Instructions */}
            <div className="instructions-section">
              <h3>Quick Start Guide</h3>
              <pre className="instructions-box">
                {generatedApp.instructions}
              </pre>
            </div>

            {/* Tab Navigation */}
            <div className="preview-tabs">
              <button
                className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
                onClick={() => setActiveTab('preview')}
              >
                🔴 Live Preview
              </button>
              <button
                className={`tab-btn ${activeTab === 'code' ? 'active' : ''}`}
                onClick={() => setActiveTab('code')}
              >
                📄 Code View
              </button>
            </div>

            {/* Live Preview Tab */}
            {activeTab === 'preview' && (
              <div className="preview-tab-content">
                <LivePreview files={generatedApp.files} appId={generatedApp.app_id} />
              </div>
            )}

            {/* Code Preview Tab */}
            {activeTab === 'code' && (
              <div className="code-preview-section">
                <CodeViewer files={generatedApp.files} />
              </div>
            )}

            {/* Generate Another */}
            <div className="actions-section">
              <button
                className="secondary-btn"
                onClick={() => {
                  setGeneratedApp(null);
                  setDescription('');
                }}
              >
                Generate Another App
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="builder-footer">
        <p>
          Built with ❤️ using Claude AI | Open Source
        </p>
        <p className="footer-note">
          All generated apps include: FastAPI backend, React frontend, complete documentation
        </p>
      </footer>
    </div>
  );
}

export default Builder;
