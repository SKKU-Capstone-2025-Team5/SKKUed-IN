import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import {
  Typography, Button, CircularProgress, Alert, Box, Avatar, Select, MenuItem, FormControl, InputLabel, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, IconButton, List, ListItem, ListItemText, ListItemAvatar,
  Card, CardContent, CardActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add'; // Import AddIcon
import CloseIcon from '@mui/icons-material/Close'; // Import CloseIcon
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
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
  const [showContestList, setShowContestList] = useState(false); // State for contest selection list
  const [contests, setContests] = useState([]); // State to store fetched contests
  const [selectedContest, setSelectedContest] = useState(null); // State for selected contest
  const [teamContest, setTeamContest] = useState(null); // State for the contest associated with the team
  const [contestDeadline, setContestDeadline] = useState(null); // State for the contest deadline
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [currentRecommendationIndex, setCurrentRecommendationIndex] = useState(0);
  const [openInviteUserDialog, setOpenInviteUserDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

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
      setTeamContest(response.data.contest); // Initialize teamContest
      if (response.data.contest && response.data.contest.ex_end) {
        setContestDeadline(new Date(response.data.contest.ex_end));
      } else {
        setContestDeadline(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    setRecommendationsLoading(true);
    setError('');
    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('You must be logged in to fetch recommendations.');
      setRecommendationsLoading(false);
      return;
    }
    try {
      const response = await fetch('/api/v1/recommend/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const handleInviteUser = async (userId) => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      alert('Cannot invite user. Make sure you are logged in.');
      return;
    }
  
    try {
      const response = await fetch(`/api/v1/teams/${id}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id_to_invite: userId }),
      });
  
      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          throw new Error(errorText || 'Failed to invite user');
        }
        throw new Error(errorData.detail || 'Failed to invite user');
      }
  
      alert('Invitation sent successfully!');
    } catch (err) {
      alert(`Error inviting user: ${err.message}`);
    }
  };

  const handleSearchUsers = async (query) => {
    if (!query || query.length < 2) { // Changed to query.length < 2
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      const response = await axios.get(`/api/v1/users/search?query=${query}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSearchResults(response.data);
    } catch (err) {
      setError(err.message);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  useEffect(() => {
    fetchTeamDetails();
    fetchRecommendations();
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
      setEditedMemberLimit(newLimit);
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

  const handleToggleContestList = async () => {
    if (!showContestList) { // Only fetch if the list is currently closed and about to open
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) throw new Error('Authentication token not found. Please log in.');

        const response = await axios.get('/api/v1/contests/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setContests(response.data);
      } catch (err) {
        setError(err.message);
      }
    }
    setShowContestList(prev => !prev);
  };

  const handleCloseContestList = () => {
    setShowContestList(false);
    setSelectedContest(null); // Clear selected contest when closing
  };

  const handleSelectContest = async (contest) => {
    setSelectedContest(contest);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      await axios.put(`/api/v1/teams/${id}`, 
        { contest_id: contest.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTeam(prevTeam => ({ ...prevTeam, contest_id: contest.id, contest: contest }));
      setTeamContest(contest);
      if (contest && contest.ex_end) {
        setContestDeadline(new Date(contest.ex_end));
      } else {
        setContestDeadline(null);
      }
      handleCloseContestList();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRemoveContest = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      await axios.put(`/api/v1/teams/${id}`, 
        { contest_id: null }, // Set contest_id to null to remove association
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTeam(prevTeam => ({ ...prevTeam, contest_id: null, contest: null }));
      setTeamContest(null);
      setContestDeadline(null);
    } catch (err) {
      setError(err.message);
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
              <Avatar key={member.id} src={member.user.profile_image_url ? `http://127.0.0.1:8000${member.user.profile_image_url}` : '/images/basic_profile.png'} sx={{ width: 40, height: 40, bgcolor: '#e0e0e0' }} />
            ))}
          </Box>
        </Box>

        <Box className="header-right">
          <Box className="description-and-recommendations">
            <Box className="description-block">
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', alignItems: 'center', mt: 1 }}> {/* Container for buttons */}
                {teamContest ? (
                  <Chip
                    label={`Connected: ${teamContest.ex_name}`}
                    onDelete={isLeader ? handleRemoveContest : undefined}
                    color="primary"
                    variant="outlined"
                    sx={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', mr: 1, mt: 1.5 }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ mr: 1, display: 'inline-block', mt: 1.5 }}>
                    No contest connected
                  </Typography>
                )}
                {isLeader && !isEditingDescription && (
                  <>
                    <IconButton color="primary" onClick={handleToggleContestList}>
                      <AddIcon />
                    </IconButton>
                    <Button variant="outlined" onClick={() => setIsEditingDescription(true)}>Edit</Button>
                  </>
                )}
                {isLeader && isEditingDescription && (
                  <Button variant="contained" onClick={handleDescriptionSave}>Save</Button>
                )}
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
            {isLeader && (
              <Box className="recommendations-section-header">
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                  <Typography variant="h6">Invite</Typography>
                  {isLeader && (
                    <IconButton color="primary" onClick={() => setOpenInviteUserDialog(true)} size="small" sx={{ borderRadius: 0 }}>
                      <AddIcon />
                    </IconButton>
                  )}
                </Box>
                {recommendationsLoading ? (
                  <CircularProgress />
                ) : recommendations.length > 0 ? (
                  <Box className="recommendation-carousel">
                    <IconButton onClick={() => setCurrentRecommendationIndex(prev => (prev - 1 + recommendations.length) % recommendations.length)} size="small">
                      <ChevronLeftIcon />
                    </IconButton>
                    <Card className="recommendation-card">
                      <CardContent sx={{ paddingBottom: '4px !important', display: 'flex', flexDirection: 'column', alignItems: 'center' }}> {/* Further reduced padding and centered content */}
                        <Avatar src={recommendations[currentRecommendationIndex].profile_image_url || '/images/basic_profile.png'} sx={{ width: 40, height: 40, mb: 0.25 }} /> {/* Further reduced size and margin */}
                        <Typography variant="body1" component="div" noWrap> {/* Smaller variant */}
                          {recommendations[currentRecommendationIndex].full_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" noWrap> {/* Smaller variant */}
                          {recommendations[currentRecommendationIndex].major}
                        </Typography>
                      </CardContent>
                      <CardActions sx={{ justifyContent: 'center' }}>
                        <Button size="small" variant="outlined" onClick={() => handleInviteUser(recommendations[currentRecommendationIndex].id)}>Invite</Button>
                      </CardActions>
                    </Card>
                    <IconButton onClick={() => setCurrentRecommendationIndex(prev => (prev + 1) % recommendations.length)} size="small">
                      <ChevronRightIcon />
                    </IconButton>
                  </Box>
                ) : (
                  <Typography>No recommendations available.</Typography>
                )}
              </Box>
            )}
          </Box>
        </Box>
      </div>

      {showContestList && (
        <Dialog open={showContestList} onClose={handleCloseContestList} maxWidth="md" fullWidth> {/* Changed maxWidth to "md" */}
          <DialogTitle sx={{ position: 'sticky', top: 0, zIndex: 1, bgcolor: 'background.paper' }}>
            Select Contest
            <IconButton
              aria-label="close"
              onClick={handleCloseContestList}
              color="primary"
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                borderRadius: '4px', /* Make it rectangular */
                width: '48px', /* Fixed width */
                height: '32px', /* Fixed height */
                minWidth: '48px', /* Ensure it's not too wide */
                padding: 0, /* Remove padding */
              }}
            >
              <CloseIcon sx={{ fontSize: '18px' }} />
            </IconButton>
          </DialogTitle>
          <DialogContent sx={{ overflow: 'visible' }}>
            {contests.length === 0 ? (
              <Typography>No contests available.</Typography>
            ) : (
              <List>
                {contests.map((contest) => (
                  <ListItem button key={contest.id} onClick={() => handleSelectContest(contest)}>
                    <ListItemText 
                      primary={contest.ex_name} 
                      secondary={contest.ex_host}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </DialogContent>
          {/* Removed DialogActions with Close button */}
        </Dialog>
      )}

      <div className="team-detail-body">
        <Box className="team-info-box">
          <Typography variant="h6" sx={{ pl: 1 }}>Team Information</Typography>
          {isLeader ? (
            <>
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
            </>
          ) : (
                                                            <>
                                                              {/* Status Block */}
                                                              <Box sx={{ mt: 0.5, mb: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}> {/* Changed to column for line break */}
                                                                <Typography variant="body2" component="div" sx={{ mb: 0.5 }}>Status</Typography> {/* Larger variant */}
                                                                <Chip label={team.status.charAt(0).toUpperCase() + team.status.slice(1)} size="medium" sx={{ bgcolor: '#A5D6A7', color: 'white', fontWeight: 'bold', fontSize: '1rem' }} /> {/* Larger size and font */}
                                                              </Box>
                                                              {/* Member Limit Block */}
                                                              <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}> {/* Changed to column for line break */}
                                                                <Typography variant="body2" sx={{ mb: 0.5 }}>Member Limit</Typography> {/* Larger variant */}
                                                                <Chip label={team.member_limit} size="medium" sx={{ bgcolor: '#A5D6A7', color: 'white', fontWeight: 'bold', fontSize: '1rem' }} /> {/* Matched color, larger size and font */}
                                                              </Box>
                                                            </>          )}
        </Box>

        <Box className="team-members-box" sx={{ mt: 1 }}>
          <Typography variant="h6">Team Members</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 1 }}>
            <Chip
              avatar={<Avatar src={team.leader.profile_image_url ? `http://127.0.0.1:8000${team.leader.profile_image_url}` : '/images/basic_profile.png'} />}
              label={`${team.leader.full_name} (Leader)`}
              color="primary"
              variant="outlined"
              size="small"
            />
            {team.members && team.members.filter(m => m.user.id !== team.leader_id).map(member => (
              <Chip
                key={member.id}
                avatar={<Avatar src={member.user.profile_image_url ? `http://127.0.0.1:8000${member.user.profile_image_url}` : '/images/basic_profile.png'} />}
                label={`${member.user.full_name} (${member.status})`}
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>

        <Box className="calendar-section">
          <Typography variant="h6">Calendar</Typography>
          <Calendar 
            onChange={setCalendarDate} 
            value={calendarDate} 
            tileClassName={({ date, view }) => {
              if (contestDeadline && view === 'month' && 
                  date.getFullYear() === contestDeadline.getFullYear() &&
                  date.getMonth() === contestDeadline.getMonth() &&
                  date.getDate() === contestDeadline.getDate()) {
                return 'deadline-date';
              }
              return null;
            }}
          />
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

      {/* Invite User Dialog */}
      <Dialog open={openInviteUserDialog} onClose={() => setOpenInviteUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Invite User
          <IconButton
            aria-label="close"
            onClick={() => setOpenInviteUserDialog(false)}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ minHeight: '350px' }}>
          <TextField
            autoFocus
            margin="dense"
            id="user-search"
            label="Search users by name or email"
            type="text"
            fullWidth
            variant="outlined"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              handleSearchUsers(e.target.value);
            }}
          />
          {searchLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {searchResults.length > 0 ? (
                searchResults.slice(0, 3).map((user) => (
                  <ListItem
                    key={user.id}
                    secondaryAction={
                      <Button variant="outlined" size="small" onClick={() => handleInviteUser(user.id)}>
                        Invite
                      </Button>
                    }
                  >
                    <ListItemAvatar>
                      <Avatar src={user.profile_image_url || '/images/basic_profile.png'} />
                    </ListItemAvatar>
                    <ListItemText primary={user.full_name} secondary={user.major} />
                  </ListItem>
                ))
              ) : (
                searchQuery && !searchLoading && <Typography sx={{ mt: 2 }}>No users found.</Typography>
              )}
            </List>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default TeamDetail;