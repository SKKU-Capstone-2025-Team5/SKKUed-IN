import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './components/Login';
import Register from './components/Register';
import Main from './components/Main';
import Profile from './components/Profile';
import PrivateRoute from './components/PrivateRoute';

import ContestDetail from './components/ContestDetail.jsx'; 

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          
          {/* --- 누구나 접근 가능한 Public Routes --- */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/main" element={<Main />} />

          {/*중복된 라우트를 모두 지우고, ContestDetail 컴포넌트를 연결.
          */}
          <Route path="/contests/:id" element={<ContestDetail />} />


          {/* --- 로그인이 필요한 Private Routes --- */}
          <Route 
            path="/profile" 
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            } 
          />
          
          {/* --- 기본 경로 --- */}
          <Route path="/" element={<Navigate to="/main" />} />

        </Routes>
      </div>
    </Router>
  );
}

export default App;