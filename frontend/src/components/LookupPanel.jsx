import { useState } from 'react';
import { fetchByBarcode, searchByName } from '../api';

export default function LookupPanel({ onItemAdded }) {
  const [barcode, setBarcode] = useState('');
  const [name, setName] = useState('');
  const [barcodeStatus, setBarcodeStatus] = useState(null); // { type: 'success'|'error', message }
  const [searchResults, setSearchResults] = useState(null);
  const [searchError, setSearchError] = useState(null);
  const [barcodeLoading, setBarcodeLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);

  async function handleBarcodeSubmit(e) {
    e.preventDefault();
    if (!barcode.trim()) return;
    setBarcodeStatus(null);
    setBarcodeLoading(true);
    try {
      const item = await fetchByBarcode(barcode.trim());
      onItemAdded(item);
      setBarcodeStatus({ type: 'success', message: `Added "${item.name}" to inventory.` });
      setBarcode('');
    } catch (err) {
      setBarcodeStatus({ type: 'error', message: err.message });
    } finally {
      setBarcodeLoading(false);
    }
  }

  async function handleSearchSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setSearchError(null);
    setSearchResults(null);
    setSearchLoading(true);
    try {
      const results = await searchByName(name.trim());
      setSearchResults(results);
    } catch (err) {
      setSearchError(err.message);
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <div className="panel">
      <h2 className="panel__title">Look up on OpenFoodFacts</h2>

      <form onSubmit={handleBarcodeSubmit} className="lookup-form">
        <label className="field">
          <span>Barcode</span>
          <input
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            placeholder="e.g. 3017620422003"
          />
        </label>
        <button className="btn btn--accent btn--small" type="submit" disabled={barcodeLoading}>
          {barcodeLoading ? 'Fetching…' : 'Fetch & add'}
        </button>
      </form>
      {barcodeStatus && (
        <p className={`panel__status panel__status--${barcodeStatus.type}`}>
          {barcodeStatus.message}
        </p>
      )}

      <hr className="panel__divider" />

      <form onSubmit={handleSearchSubmit} className="lookup-form">
        <label className="field">
          <span>Product name</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. almond milk"
          />
        </label>
        <button className="btn btn--ghost btn--small" type="submit" disabled={searchLoading}>
          {searchLoading ? 'Searching…' : 'Search'}
        </button>
      </form>
      {searchError && <p className="panel__status panel__status--error">{searchError}</p>}

      {searchResults && (
        <ul className="lookup-results">
          {searchResults.length === 0 && <li className="lookup-results__empty">No products found.</li>}
          {searchResults.map((product, i) => (
            <li key={i} className="lookup-results__item">
              <div>
                <strong>{product.product_name}</strong>
                {product.brands && <span className="inv-row__muted"> — {product.brands}</span>}
              </div>
              {product.barcode && (
                <button
                  className="btn btn--ghost btn--small"
                  onClick={async () => {
                    try {
                      const item = await fetchByBarcode(product.barcode);
                      onItemAdded(item);
                      setSearchResults((rs) => rs.filter((p) => p !== product));
                    } catch (err) {
                      setSearchError(err.message);
                    }
                  }}
                >
                  Add
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
