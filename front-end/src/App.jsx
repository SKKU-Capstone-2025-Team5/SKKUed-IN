// import React from 'react';
// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import Login from './components/Login';
// import Register from './components/Register';
// import Main from './components/Main';
// import Profile from './components/Profile';
// import './App.css';

// function App() {
//   return (
//     <Router>
//       <div className="App">
//         <Routes>
//           <Route path="/login" element={<Login />} />
//           <Route path="/register" element={<Register />} />
//           <Route path="/main" element={<Main />} />
//           <Route path="/profile" element={<Profile />} />
//           <Route path="/" element={<Navigate to="/login" />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// }

// export default App;

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// 컴포넌트 import
import Login from './components/Login';
import Register from './components/Register';
import Main from './components/Main';
import Profile from './components/Profile';

// 1. PrivateRoute 컴포넌트를 import 합니다.
import PrivateRoute from './components/PrivateRoute';

// 2. (TODO) 나중에 만들 공모전 상세 페이지 import (지금은 주석 처리)
// import ContestDetail from './components/ContestDetail'; 

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

          {/* 3. Main.jsx의 Link가 연결될 상세 페이지 라우트입니다. 
             :id 부분에는 contest_id가 동적으로 들어갑니다.
             나중에 ContestDetail.jsx 파일을 만들어서 아래 element에 연결하세요.
          */}
          <Route path="/contests/:id" element={<div>공모전 상세 페이지 (TODO)</div>} />
          {/* <Route path="/contests/:id" element={<ContestDetail />} /> */}


          {/* --- 로그인이 필요한 Private Routes --- */}
          <Route 
            path="/profile" 
            element={
              // 4. /profile 경로를 PrivateRoute로 감싸서 보호합니다.
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            } 
          />
          
          {/* 5. 기본 접속(/) 경로를 /login 대신 /main으로 변경합니다. */}
          <Route path="/" element={<Navigate to="/main" />} />

        </Routes>
      </div>
    </Router>
  );
}

export default App;