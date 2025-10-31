import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css'; // Reuse the login CSS
import logo from '/images/logo.png'; // Import the logo

function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    setError('');

    try {
      await axios.post('http://127.0.0.1:8000/api/v1/auth/register', {
        email: email,
        password: password,
        full_name: fullName
      });
      alert('Registration successful! Please log in.');
      navigate('/login');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-container">
        <form onSubmit={handleSubmit} className="login-form">
          <h2>Register</h2>
          {error && <p className="error-message">{error}</p>}
          <div className="input-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="input-group">
            <label htmlFor="email">SKKU Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="input-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
          <p className="switch-form">
            <Link to="/login">Login</Link>
          </p>
        </form>
      </div>
      <div className="login-info-section">
        <div className="tagline-logo-wrapper">
          <p className="tagline">Your trusted campus connection for team building,<br/><span className="skku-name">SKKUed-IN</span></p>
          <img src={logo} alt="SKKUed-IN Logo" className="login-logo" />
        </div>
      </div>
    </div>
  );
}

export default Register;