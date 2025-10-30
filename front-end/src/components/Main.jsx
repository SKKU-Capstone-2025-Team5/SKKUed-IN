import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Main() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  return (
    <div>
      <div style={{ position: 'absolute', top: '1rem', right: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Link to="/profile" style={{ textDecoration: 'none', color: '#388E3C', whiteSpace: 'nowrap' }}>Profile Settings</Link>
        <button onClick={handleLogout} style={{ background: 'none', border: 'none', color: '#388E3C', cursor: 'pointer', whiteSpace: 'nowrap', padding: 0, margin: 0 }}>Logout</button>
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <h1>MAIN</h1>
      </div>
    </div>
  );
}

export default Main;