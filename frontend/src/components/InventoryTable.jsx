import { useState } from 'react';
import BarcodeTag from './BarcodeTag';

function EditRow({ item, onSave, onCancel }) {
  const [price, setPrice] = useState(item.price);
  const [stock, setStock] = useState(item.stock);

  return (
    <tr className="inv-row inv-row--editing">
      <td><BarcodeTag value={item.id} /></td>
      <td className="inv-row__name">{item.name}</td>
      <td className="inv-row__muted">{item.brand || '—'}</td>
      <td>
        <input
          className="inv-input"
          type="number"
          step="0.01"
          min="0"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          aria-label={`Price for ${item.name}`}
        />
      </td>
      <td>
        <input
          className="inv-input"
          type="number"
          min="0"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          aria-label={`Stock for ${item.name}`}
        />
      </td>
      <td className="inv-row__actions">
        <button
          className="btn btn--accent btn--small"
          onClick={() => onSave({ price: parseFloat(price) || 0, stock: parseInt(stock, 10) || 0 })}
        >
          Save
        </button>
        <button className="btn btn--ghost btn--small" onClick={onCancel}>
          Cancel
        </button>
      </td>
    </tr>
  );
}

export default function InventoryTable({ items, onUpdate, onDelete, loading }) {
  const [editingId, setEditingId] = useState(null);

  if (loading) {
    return <p className="inv-empty">Loading inventory…</p>;
  }

  if (items.length === 0) {
    return (
      <div className="inv-empty">
        <p>No items in inventory yet.</p>
        <p className="inv-empty__hint">
          Add one manually, or look a product up by barcode or name on the right.
        </p>
      </div>
    );
  }

  return (
    <table className="inv-table">
      <colgroup>
        <col style={{ width: '70px' }} />
        <col style={{ width: '32%' }} />
        <col style={{ width: '22%' }} />
        <col style={{ width: '90px' }} />
        <col style={{ width: '80px' }} />
        <col style={{ width: '170px' }} />
      </colgroup>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Brand</th>
          <th>Price</th>
          <th>Stock</th>
          <th aria-label="Actions" />
        </tr>
      </thead>
      <tbody>
        {items.map((item) =>
          editingId === item.id ? (
            <EditRow
              key={item.id}
              item={item}
              onCancel={() => setEditingId(null)}
              onSave={async (updates) => {
                await onUpdate(item.id, updates);
                setEditingId(null);
              }}
            />
          ) : (
            <tr key={item.id} className="inv-row">
              <td><BarcodeTag value={item.id} /></td>
              <td className="inv-row__name">{item.name}</td>
              <td className="inv-row__muted">{item.brand || '—'}</td>
              <td className="inv-row__mono">${Number(item.price).toFixed(2)}</td>
              <td className="inv-row__mono">{item.stock}</td>
              <td className="inv-row__actions">
                <button className="btn btn--ghost btn--small" onClick={() => setEditingId(item.id)}>
                  Edit
                </button>
                <button className="btn btn--danger btn--small" onClick={() => onDelete(item.id)}>
                  Delete
                </button>
              </td>
            </tr>
          )
        )}
      </tbody>
    </table>
  );
}