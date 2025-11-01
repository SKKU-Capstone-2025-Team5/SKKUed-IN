import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './components/Login';
import Register from './components/Register';
import Main from './components/Main';
import Profile from './components/Profile';
import PrivateRoute from './components/PrivateRoute';
import MainLayout from './components/MainLayout';
import MyTeams from './components/MyTeams';
import Messenger from './components/Messenger';
import CreateTeam from './components/CreateTeam';
import ContestDetail from './components/ContestDetail.jsx'; 

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Navigate to="/login" />} />

          <Route element={<PrivateRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/find-project" element={<Main />} />
              <Route path="/my-teams" element={<MyTeams />} />
              <Route path="/messenger" element={<Messenger />} />
              <Route path="/my-page" element={<Profile />} />
              <Route path="/contests/:id" element={<ContestDetail />} />
              <Route path="/teams/create" element={<CreateTeam />} />
            </Route>
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;