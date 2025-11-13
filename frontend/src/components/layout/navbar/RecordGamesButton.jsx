import VolleyballIcon from './VolleyballIcon';

export default function RecordGamesButton({ onClick }) {
  return (
    <button
      className="navbar-menu-button"
      onClick={onClick}
      aria-label="Record Games"
    >
      <VolleyballIcon className="navbar-volleyball-icon" />
      <span className="navbar-menu-label">Record Games</span>
    </button>
  );
}

