// Thin wrapper around the Flask inventory API.
// In dev, Vite proxies /inventory/* straight through to
// http://127.0.0.1:5000 (see vite.config.js), so these calls
// can just use relative paths.

async function handle(response) {
  let body = null;
  try {
    body = await response.json();
  } catch {
    // no JSON body (e.g. network failure before a response existed)
  }
  if (!response.ok) {
    const message = body?.error || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body;
}

export async function listItems() {
  const res = await fetch('/inventory');
  return handle(res);
}

export async function getItem(id) {
  const res = await fetch(`/inventory/${id}`);
  return handle(res);
}

export async function addItem(item) {
  const res = await fetch('/inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item),
  });
  return handle(res);
}

export async function updateItem(id, updates) {
  const res = await fetch(`/inventory/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  return handle(res);
}

export async function deleteItem(id) {
  const res = await fetch(`/inventory/${id}`, { method: 'DELETE' });
  return handle(res);
}

export async function fetchByBarcode(barcode) {
  const res = await fetch(`/inventory/fetch/barcode/${encodeURIComponent(barcode)}`, {
    method: 'POST',
  });
  return handle(res);
}

export async function searchByName(name) {
  const res = await fetch(`/inventory/fetch/search?name=${encodeURIComponent(name)}`);
  return handle(res);
}
