import React from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import './MainLayout.css';
import logo from '/images/logo.png';

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation(); // Get current location

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  // Function to check if a path is active
  const isActive = (path) => location.pathname === path;

  return (
    <div className="main-layout">
      <div className="sidebar">
        <div>
          <div className="sidebar-header">
            <img src={logo} alt="SKKUed-IN Logo" className="sidebar-logo" />
            <span className="sidebar-title">SKKUed-IN</span>
          </div>
          <nav className="sidebar-nav">
            <Link 
              to="/find-project" 
              className={`nav-button ${isActive('/find-project') ? 'active' : ''}`}
            >
              <i className="fas fa-search"></i> Find Project
            </Link>
            <Link 
              to="/my-teams" 
              className={`nav-button ${isActive('/my-teams') ? 'active' : ''}`}
            >
              <i className="fas fa-users"></i> My Teams
            </Link>
            <Link 
              to="/messenger" 
              className={`nav-button ${isActive('/messenger') ? 'active' : ''}`}
            >
              <i className="fas fa-comments"></i> Messenger
            </Link>
            <Link 
              to="/my-page" 
              className={`nav-button ${isActive('/my-page') ? 'active' : ''}`}
            >
              <i className="fas fa-user"></i> My Page
            </Link>
          </nav>
        </div>
        <button onClick={handleLogout} className="logout-button">
          <i className="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
      <div className="content">
        <Outlet />
      </div>
    </div>
  );
}

export default MainLayout;
