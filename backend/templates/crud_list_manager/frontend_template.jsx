import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({INITIAL_FORM_STATE});

  // Fetch all items on component mount
  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/{ENTITY_NAME_LOWER}`);
      setItems(response.data);
    } catch (err) {
      setError('Failed to fetch {ENTITY_NAME_LOWER}s. Make sure the backend is running.');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/{ENTITY_NAME_LOWER}`, formData);
      setItems([...items, response.data]);
      setFormData({INITIAL_FORM_STATE}); // Reset form
    } catch (err) {
      setError('Failed to add {ENTITY_NAME_LOWER}. Please try again.');
      console.error('Submit error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    setLoading(true);
    setError(null);

    try {
      await axios.delete(`${API_BASE_URL}/{ENTITY_NAME_LOWER}/${id}`);
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      setError('Failed to delete {ENTITY_NAME_LOWER}.');
      console.error('Delete error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>{ENTITY_NAME} Manager</h1>
        <p>{DESCRIPTION}</p>
      </header>

      <main className="App-main">
        {/* Error Display */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Add Form */}
        <section className="form-section">
          <h2>Add New {ENTITY_NAME}</h2>
          <form onSubmit={handleSubmit}>
            {FORM_FIELDS}

            <button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add {ENTITY_NAME}'}
            </button>
          </form>
        </section>

        {/* Items List */}
        <section className="list-section">
          <h2>All {ENTITY_NAME}s ({items.length})</h2>

          {loading && <div className="loading">Loading...</div>}

          {items.length === 0 && !loading && (
            <div className="empty-state">
              No {ENTITY_NAME_LOWER}s yet. Add one above!
            </div>
          )}

          <div className="items-grid">
            {items.map(item => (
              <div key={item.id} className="item-card">
                {LIST_ITEM_CONTENT}

                <button
                  className="delete-btn"
                  onClick={() => handleDelete(item.id)}
                  disabled={loading}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="App-footer">
        <p>Built with ❤️ by Zero-Code AI App Builder</p>
      </footer>
    </div>
  );
}

export default App;
