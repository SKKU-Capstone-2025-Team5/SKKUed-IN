import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import {
  Typography, Button, CircularProgress, Alert, Box, Avatar, Select, MenuItem, FormControl, InputLabel, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './TeamDetail.css';

function TeamDetail() {
  const { id } = useParams();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [editedDescription, setEditedDescription] = useState('');
  const [teamStatus, setTeamStatus] = useState(''); // State for editable status
  const [editedMemberLimit, setEditedMemberLimit] = useState(0);
  const [calendarDate, setCalendarDate] = useState(new Date()); // State for calendar
  const [openEtcPopup, setOpenEtcPopup] = useState(false); // State for Etc popup

  const getUserId = () => {
    const token = localStorage.getItem('accessToken');
    if (!token) return null;
    try {
      return jwtDecode(token).user_id;
    } catch (e) {
      return null;
    }
  };
  const loggedInUserId = getUserId();

  const fetchTeamDetails = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      const response = await axios.get(`/api/v1/teams/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeam(response.data);
      setEditedDescription(response.data.description || '');
      setTeamStatus(response.data.status); // Set initial status
      setEditedMemberLimit(response.data.member_limit);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeamDetails();
  }, [id]);

  const handleDescriptionSave = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      await axios.put(`/api/v1/teams/${id}`, 
        { description: editedDescription },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTeam(prevTeam => ({ ...prevTeam, description: editedDescription }));
      setIsEditingDescription(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStatusChange = async (event) => {
    const newStatus = event.target.value;
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      await axios.put(`/api/v1/teams/${id}`, 
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTeam(prevTeam => ({ ...prevTeam, status: newStatus }));
      setTeamStatus(newStatus); // Update local state
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMemberLimitChange = async (event) => {
    const newLimit = event.target.value;
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      await axios.put(`/api/v1/teams/${id}`, 
        { member_limit: newLimit },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTeam(prevTeam => ({ ...prevTeam, member_limit: newLimit }));
    } catch (err) {
      setError(err.message);
    }
  };

  const [etcLinkInput, setEtcLinkInput] = useState('');

  const handleEtcLinkOpen = () => {
    setOpenEtcPopup(true);
  };

  const handleEtcLinkClose = () => {
    setOpenEtcPopup(false);
    setEtcLinkInput(''); // Clear input on close
  };

  const handleEtcLinkSubmit = () => {
    if (etcLinkInput) {
      window.open(etcLinkInput, '_blank');
      handleEtcLinkClose();
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">Error: {error}</Alert>;
  if (!team) return <Alert severity="info">Team not found.</Alert>;

  const isLeader = team.leader_id === loggedInUserId;

  const teamStatuses = ["recruiting", "active", "archived"];

  return (
    <div className="team-detail-container">
      <div className="team-detail-header">
        <Box className="header-left">
          <Typography variant="h4" className="team-name">{team.name}</Typography>
          <Box className="sub-profiles">
            {team.members && team.members.map(member => (
              <Avatar key={member.id} sx={{ width: 40, height: 40, bgcolor: '#e0e0e0' }}>
                {member.user.full_name ? member.user.full_name[0] : ''}
              </Avatar>
            ))}
          </Box>
        </Box>

        <Box className="header-right">
          <Box className="description-and-recommendations">
            <Box className="description-block">
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}> {/* Container for buttons */}
                {isLeader && (isEditingDescription ? (
                  <Button variant="contained" onClick={handleDescriptionSave}>Save</Button>
                ) : (
                  <>
                    <Button variant="contained" color="primary">Connect Contest</Button>
                    <Button variant="outlined" onClick={() => setIsEditingDescription(true)}>Edit</Button>
                  </>
                ))}
              </Box>
              {isEditingDescription ? (
                <textarea
                  className="description-input"
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                />
              ) : (
                <Typography 
                  className="description-input"
                  onClick={() => isLeader && setIsEditingDescription(true)}
                  sx={{ cursor: isLeader ? 'pointer' : 'default', minHeight: '80px' }}
                >
                  {team.description || "Click to add description"}
                </Typography>
              )}
            </Box>
            <Box className="recommendations-section-header">
              <Typography variant="h6">Recommended Members</Typography>
              <Typography>Member recommendations coming soon!</Typography>
            </Box>
          </Box>
        </Box>
      </div>

      <div className="team-detail-body">
        <Box className="team-info-box">
          <Typography variant="h6">Team Information</Typography>
          <Typography>
            {isLeader ? (
              <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
                <InputLabel id="team-status-select-label">Status</InputLabel>
                <Select
                  labelId="team-status-select-label"
                  id="team-status-select"
                  value={teamStatus}
                  onChange={handleStatusChange}
                  label="Status"
                >
                  {teamStatuses.map(status => (
                    <MenuItem key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <span>{team.status.charAt(0).toUpperCase() + team.status.slice(1)}</span>
            )}
          </Typography>
          <Typography>
            {isLeader ? (
              <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
                <InputLabel id="member-limit-select-label">Member Limit</InputLabel>
                <Select
                  labelId="member-limit-select-label"
                  id="team-member-limit-select"
                  value={editedMemberLimit}
                  onChange={handleMemberLimitChange}
                  label="Member Limit"
                >
                  {[...Array(10).keys()].map(i => (
                    <MenuItem key={i + 1} value={i + 1}>{i + 1}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <span>{team.member_limit}</span>
            )}
          </Typography>
        </Box>

        <Box className="team-members-box" sx={{ mt: 1 }}>
          <Typography variant="h6">Team Members</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
            <Chip
              avatar={<Avatar>{team.leader?.full_name ? team.leader.full_name[0] : ''}</Avatar>}
              label={`${team.leader.full_name} (Leader)`}
              color="primary"
              variant="outlined"
              size="small"
            />
            {team.members && team.members.filter(m => m.user.id !== team.leader_id).map(member => (
              <Chip
                key={member.id}
                avatar={<Avatar>{member.user.full_name[0]}</Avatar>}
                label={`${member.user.full_name} (${member.status})`}
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>

        <Box className="calendar-section">
          <Typography variant="h6">Calendar</Typography>
          <Calendar onChange={setCalendarDate} value={calendarDate} />
        </Box>

        <Box className="links-section">
          <Typography variant="h6">Integrations</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
            <Button variant="outlined" onClick={() => window.open('https://notion.so', '_blank')}>Notion</Button>
            <Button variant="outlined" onClick={() => window.open('https://github.com', '_blank')}>GitHub</Button>
            <Button variant="outlined" onClick={() => window.open('https://docs.google.com', '_blank')}>Docs</Button>
            <Button variant="outlined" onClick={() => setOpenEtcPopup(true)}>Etc</Button>
          </Box>
        </Box>
      </div>

      <Dialog open={openEtcPopup} onClose={handleEtcLinkClose}>
        <DialogTitle>Enter Custom Link</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="etc-link"
            label="Link URL"
            type="url"
            fullWidth
            variant="standard"
            value={etcLinkInput}
            onChange={(e) => setEtcLinkInput(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEtcLinkClose}>Cancel</Button>
          <Button onClick={handleEtcLinkSubmit}>Go</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default TeamDetail;