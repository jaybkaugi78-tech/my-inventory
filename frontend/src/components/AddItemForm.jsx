import { useState } from 'react';

const EMPTY = { name: '', brand: '', barcode: '', price: '', stock: '' };

export default function AddItemForm({ onAdd }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await onAdd({
        name: form.name.trim(),
        brand: form.brand.trim(),
        barcode: form.barcode.trim(),
        price: form.price ? parseFloat(form.price) : 0,
        stock: form.stock ? parseInt(form.stock, 10) : 0,
      });
      setForm(EMPTY);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h2 className="panel__title">Add item manually</h2>
      <label className="field">
        <span>Name</span>
        <input value={form.name} onChange={(e) => update('name', e.target.value)} />
      </label>
      <label className="field">
        <span>Brand</span>
        <input value={form.brand} onChange={(e) => update('brand', e.target.value)} />
      </label>
      <label className="field">
        <span>Barcode</span>
        <input value={form.barcode} onChange={(e) => update('barcode', e.target.value)} />
      </label>
      <div className="field-row">
        <label className="field">
          <span>Price</span>
          <input
            type="number"
            step="0.01"
            min="0"
            value={form.price}
            onChange={(e) => update('price', e.target.value)}
          />
        </label>
        <label className="field">
          <span>Stock</span>
          <input
            type="number"
            min="0"
            value={form.stock}
            onChange={(e) => update('stock', e.target.value)}
          />
        </label>
      </div>
      {error && <p className="panel__error">{error}</p>}
      <button className="btn btn--accent" type="submit" disabled={submitting}>
        {submitting ? 'Adding…' : 'Add to inventory'}
      </button>
    </form>
  );
}
