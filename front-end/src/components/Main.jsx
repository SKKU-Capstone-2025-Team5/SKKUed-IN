import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Main.css'; 

/**
 * D-Day 계산 함수
 * @param {string} endDateString - "YYYY-MM-DD" 형식의 마감 날짜
 * @returns {string} - "D-day", "D-10", "마감" 등의 문자열
 */
const calculateDday = (endDateString) => {
  if (!endDateString) {
    return ''; // 날짜가 없으면 빈 문자열 반환
  }

  const today = new Date();
  const endDate = new Date(endDateString);

  // 날짜 차이를 밀리초(ms)로 계산
  const diffTime = endDate.getTime() - today.getTime();
  
  // 밀리초를 일(day)로 변환 (소수점 올림)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return "마감"; // 마감일이 지남
  } else if (diffDays === 0) {
    return "D-Day"; // 오늘 마감
  } else {
    return `D-${diffDays}`; // D-day 남음
  }
};

function Main() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchContests = async () => {
      try {

        // 1. localStorage에서 토큰 가져오기
        const token = localStorage.getItem('accessToken');

        if (!token) {
          throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.');
        }

        // 2. fetch 요청에 'Authorization' 헤더 추가하기
        const response = await fetch('http://127.0.0.1:8000/api/v1/contests', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` 
          }
        });

        if (!response.ok) {
          throw new Error('서버에서 데이터를 가져오는 데 실패했습니다.');
        }

        const data = await response.json();
        setContests(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchContests();
  }, []); // 컴포넌트 마운트 시 한 번만 실행

  if (loading) {
    return <div>데이터를 불러오는 중입니다...</div>;
  }

  if (error) {
    return <div>에러: {error}</div>;
  }

  return (
    <div className="main-container">
      {/* ... (h1, contest-list, map 등 기존 코드) ... */}
      <h1 className="main-title">진행중인 공모전</h1>
      
      <div className="contest-list">
        {contests.map((contest) => (
          <div key={contest.id} className="contest-card">
            <Link to={`/contests/${contest.id}`} className="card-link">
              
              <div className="card-image-container">
                <img src={contest.ex_image} alt={contest.ex_name} className="card-image" />
                <span className="card-d-day">
                  {calculateDday(contest.ex_end)}
                </span>
              </div>

              <div className="card-content">
                <h3 className="card-title">{contest.ex_name}</h3>
                <p className="card-organization">{contest.ex_host}</p>
                <div className="card-footer">
                  <span>시작: {contest.ex_start}</span>
                  <span>마감: {contest.ex_end}</span>
                </div>
              </div>

            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Main;