import { Home, MessageCircle } from 'lucide-react';

function Navigation() {
  const currentPath = window.location.pathname;

  const navigate = (path) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <nav style={{
      backgroundColor: '#1a1a2e',
      padding: '12px 20px',
      display: 'flex',
      gap: '20px',
      alignItems: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <button
        onClick={() => navigate('/')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          backgroundColor: currentPath === '/' ? '#667eea' : 'transparent',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '1rem',
          fontWeight: '500',
          transition: 'background-color 0.2s'
        }}
        onMouseOver={(e) => {
          if (currentPath !== '/') {
            e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
          }
        }}
        onMouseOut={(e) => {
          if (currentPath !== '/') {
            e.target.style.backgroundColor = 'transparent';
          }
        }}
      >
        <Home size={18} />
        Home
      </button>
      
      <button
        onClick={() => navigate('/whatsapp')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          backgroundColor: currentPath === '/whatsapp' ? '#25D366' : 'transparent',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '1rem',
          fontWeight: '500',
          transition: 'background-color 0.2s'
        }}
        onMouseOver={(e) => {
          if (currentPath !== '/whatsapp') {
            e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
          }
        }}
        onMouseOut={(e) => {
          if (currentPath !== '/whatsapp') {
            e.target.style.backgroundColor = 'transparent';
          }
        }}
      >
        <MessageCircle size={18} />
        WhatsApp
      </button>
    </nav>
  );
}

export default Navigation;

