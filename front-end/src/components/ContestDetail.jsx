import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './ContestDetail.css';

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Avatar from '@mui/material/Avatar';

// D-Day 계산 함수 
const calculateDday = (endDateString) => {
    if (!endDateString) return '';
    const today = new Date();
    const endDate = new Date(endDateString);
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays < 0) return "마감";
    if (diffDays === 0) return "D-Day";
    return `D-${diffDays}`;
};

function ContestDetail() {
  const { id } = useParams(); 
  const contestId = parseInt(id, 10);

  const [contest, setContest] = useState(null);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTeamDetailDialog, setShowTeamDetailDialog] = useState(false);
  const [selectedTeamForDialog, setSelectedTeamForDialog] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.');
        }

        // --- 데이터 요청 1: 공모전 상세 정보 ---
        const contestResponse = await fetch(`http://127.0.0.1:8000/api/v1/contests/${contestId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!contestResponse.ok) {
          throw new Error('공모전 정보를 불러오는 데 실패했습니다.');
        }
        const contestData = await contestResponse.json();
        setContest(contestData);

        // --- 데이터 요청 2: 공개 팀 목록 ---
        const teamsResponse = await fetch(`/api/v1/teams/by_contest/${contestId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!teamsResponse.ok) {
          throw new Error('팀 목록을 불러오는 데 실패했습니다.');
        }
        const filteredTeams = await teamsResponse.json();
        setTeams(filteredTeams);

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [contestId]);

  const handleOpenTeamDetailDialog = (team) => {
    setSelectedTeamForDialog(team);
    setShowTeamDetailDialog(true);
  };

  const handleCloseTeamDetailDialog = () => {
    setShowTeamDetailDialog(false);
    setSelectedTeamForDialog(null);
  };

  if (loading) {
    return <div>데이터를 불러오는 중입니다...</div>;
  }

  if (error) {
    return <div>에러: {error}</div>;
  }

  if (!contest) {
    return <div>공모전 정보를 찾을 수 없습니다.</div>;
  }


  return (
    <div className="detail-container">
      
      {/* --- 1. 공모전 상세 카드 (가로형) --- */}
      <div className="detail-card-horizontal">
        <img
          src={contest.ex_image || '/images/placeholder_contest.png'} // Use a placeholder if ex_image is empty
          alt={contest.ex_name}
          className="detail-card-image"
        />
        <div className="detail-card-content">
          <h1 className="detail-title">{contest.ex_name}</h1>
          <p className="detail-host">주최: {contest.ex_host}</p>
          <div className="detail-dates">
            <span>시작: {contest.ex_start}</span>
            <span>마감: {contest.ex_end}</span>
            <span className="detail-dday">{calculateDday(contest.ex_end)}</span>
          </div>
          <a href={contest.ex_link} target="_blank" rel="noopener noreferrer" className="detail-link-button">
            공모전 링크 바로가기
          </a>
        </div>
      </div>

      {/* --- 2. 참여중인 팀 목록 --- */}
      <div className="team-list-section">
        <div className="team-list-header">
          <h2>이 공모전에 참여중인 팀 ({teams.length}개)</h2>
          <Link to={`/teams/create?contestId=${contestId}`} className="create-team-button">
            + 새 팀 만들기
          </Link>
        </div>
        
        {teams.length > 0 ? (
          <div className="team-list">
            {teams.map(team => (
              // 🚨 가정: 팀 객체(team)에 'id'와 'name' 필드가 있다고 가정합니다.
              <div key={team.id} className="team-card">
                <h4 className="team-name">{team.name}</h4>
                <div className="team-leader-info">
                  <Avatar src={team.leader.profile_image_url ? `http://127.0.0.1:8000${team.leader.profile_image_url}` : '/images/basic_profile.png'} sx={{ width: 60, height: 60 }} />
                  <p style={{ fontWeight: 'bold', fontSize: '1.1rem', marginTop: 0 }}>{team.leader.full_name}</p>
                </div>
                <p className="team-members-status">{team.members.length} / {team.member_limit}</p>
                <button onClick={() => handleOpenTeamDetailDialog(team)} className="team-join-button">
                  팀 정보 보기
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p>아직 이 공모전에 참여중인 팀이 없습니다. 첫 번째 팀을 만들어보세요!</p>
        )}
        
      </div>

      {/* Team Detail Dialog */}
      <Dialog open={showTeamDetailDialog} onClose={handleCloseTeamDetailDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedTeamForDialog?.name}</DialogTitle>
        <DialogContent>
          <div className="team-description-block">
            <p>{selectedTeamForDialog?.description}</p>
          </div>
          <p><strong>현재 멤버</strong><br /> {selectedTeamForDialog?.members.length} / {selectedTeamForDialog?.member_limit}</p>
          <h4>팀 멤버</h4>
          <div className="team-members-container">
            {selectedTeamForDialog?.members.map(member => (
              <div key={member.id} className="team-member-card">
                <Avatar src={member.user.profile_image_url ? `http://127.0.0.1:8000${member.user.profile_image_url}` : '/images/basic_profile.png'} sx={{ width: 32, height: 32 }} />
                <div className="member-details">
                  <span className="member-name">{member.user.full_name}</span>
                  <span className="member-role">({member.role})</span>
                </div>
              </div>
            ))}
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseTeamDetailDialog}>닫기</Button>
        </DialogActions>
      </Dialog>

    </div>
  );
}

export default ContestDetail;