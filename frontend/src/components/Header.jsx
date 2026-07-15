export default function Header({ itemCount }) {
  return (
    <header className="app-header">
      <h1 className="app-header__title">Inventory</h1>
      <p className="app-header__subtitle">
        {itemCount} {itemCount === 1 ? 'item' : 'items'}
      </p>
    </header>
  );
}
