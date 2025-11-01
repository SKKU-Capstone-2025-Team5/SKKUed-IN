import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function MyTeams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.');
        }

        // For simplicity, fetching public teams for now.
        // A more robust solution would involve a dedicated endpoint for user's teams.
        const response = await axios.get('http://127.0.0.1:8000/api/v1/teams/public', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setTeams(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  if (loading) {
    return <div>팀 목록을 불러오는 중입니다...</div>;
  }

  if (error) {
    return <div>에러: {error}</div>;
  }

  return (
    <div>
      <h1>My Teams</h1>
      <button onClick={() => navigate('/teams/create')}>새 팀 만들기</button> {/* Placeholder for create team */}
      
      {teams.length === 0 ? (
        <p>아직 참여 중인 팀이 없습니다.</p>
      ) : (
        <ul>
          {teams.map(team => (
            <li key={team.id}>
              <Link to={`/teams/${team.id}`}>{team.name}</Link> ({team.is_public ? 'Public' : 'Private'})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyTeams;
