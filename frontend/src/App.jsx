import { useEffect, useState, useCallback } from 'react';
import Header from './components/Header';
import InventoryTable from './components/InventoryTable';
import AddItemForm from './components/AddItemForm';
import LookupPanel from './components/LookupPanel';
import { listItems, addItem, updateItem, deleteItem } from './api';
import './App.css';

export default function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listItems();
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleItemAdded(item) {
    setItems((prev) => [...prev, item]);
  }

  async function handleAdd(newItem) {
    const created = await addItem(newItem);
    handleItemAdded(created);
  }

  async function handleUpdate(id, updates) {
    const updated = await updateItem(id, updates);
    setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
  }

  async function handleDelete(id) {
    await deleteItem(id);
    setItems((prev) => prev.filter((it) => it.id !== id));
  }

  return (
    <div className="app-shell">
      <Header itemCount={items.length} />

      <main className="app-main">
        {error && (
          <div className="banner banner--error">
            Could not reach the API: {error}. Is the Flask server running on port 5000?
          </div>
        )}

        <section className="app-main__list">
          <InventoryTable
            items={items}
            loading={loading}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />
        </section>

        <aside className="app-main__sidebar">
          <LookupPanel onItemAdded={handleItemAdded} />
          <AddItemForm onAdd={handleAdd} />
        </aside>
      </main>
    </div>
  );
}
