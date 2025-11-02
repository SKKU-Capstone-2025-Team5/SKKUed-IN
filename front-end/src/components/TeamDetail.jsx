import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import {
  Container, Typography, Card, CardContent, Button, Grid, Avatar, List, ListItem, ListItemText,
  Chip, CircularProgress, Alert, Box, ListItemAvatar
} from '@mui/material';
import './TeamDetail.css';

const BACKEND_URL = 'http://127.0.0.1:8000'; // Define your backend URL

function TeamDetail() {
  const { id } = useParams();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [recLoading, setRecLoading] = useState(false);

  const fetchTeamDetails = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      const response = await axios.get(`/api/v1/teams/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeam(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    setRecLoading(true);
    setError('');
    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('You must be logged in to fetch recommendations.');
      setRecLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/v1/recommend/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      const data = await response.json();
      setRecommendations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRecLoading(false);
    }
  };

  useEffect(() => {
    fetchTeamDetails();
  }, [id]);

  useEffect(() => {
    if (team && !loading) {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        console.warn('Access token not found, cannot fetch recommendations automatically.');
        return;
      }

      const isTeamFull = team.members && team.members.length >= team.member_limit;
      let loggedInUserId = null;
      try {
        const decodedToken = jwtDecode(token);
        loggedInUserId = decodedToken.user_id;
      } catch (e) {
        console.error('Error decoding token:', e);
        return; // Exit if token is invalid
      }
      const isLeader = team.leader_id === loggedInUserId;

      if (isLeader && !isTeamFull && recommendations.length === 0) {
        fetchRecommendations();
      }
    }
  }, [team, loading, recommendations.length]); // Added recommendations.length to dependencies

  const handleInviteUser = async (userId) => {
    setError('');
    const token = localStorage.getItem('accessToken');
    if (!token || !team) {
      setError('Cannot invite user. Make sure you are logged in and have a team selected.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/teams/${team.id}/invite`, {
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
      fetchTeamDetails();
    } catch (err) {
      setError(err.message);
      alert(`Error inviting user: ${err.message}`);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!team) return <Alert severity="info">Team not found.</Alert>;

  const isTeamFull = team.members && team.members.length >= team.member_limit;
  
  let loggedInUserId = null;
  const token = localStorage.getItem('accessToken');
  if (token) {
    try {
      const decodedToken = jwtDecode(token);
      loggedInUserId = decodedToken.user_id;
    } catch (e) {
      console.error('Error decoding token in render:', e);
      // Optionally handle invalid token, e.g., clear token and redirect to login
    }
  }
  const isLeader = team.leader_id === loggedInUserId;

    return (
      <Container className="team-detail-container" sx={{ backgroundColor: '#f4f7f6', minHeight: '100vh', py: 3 }}>
        <Box className="team-header">
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>{team.name}</Typography>
          <Typography variant="subtitle1" color="textSecondary">{team.description}</Typography>
          {team.members && team.members.length > 0 && (
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              {team.members.map(member => (
                <Avatar 
                  key={member.id} 
                  src={member.user.profile_image_url || '/images/basic_profile.png'} 
                  alt={member.user.full_name}
                  sx={{ width: 56, height: 56 }} // Increased size
                />
              ))}
            </Box>
          )}
        </Box>
  
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}> {/* Main content area */}
            <Grid container spacing={3}> {/* Nested Grid for Team Info and Team Space */}
              <Grid item xs={12}> {/* Team Info */}
                <Card className="team-info-card">
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Team Information</Typography>
                    <Typography><strong>Status:</strong> {team.status}</Typography>
                    <Typography><strong>Members:</strong> {team.members ? team.members.length : 0} / {team.member_limit}</Typography>
                  </CardContent>
                </Card>
                <Card className="team-members-card">
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Team Members</Typography>
                    <List>
                      {team.members && team.members.length > 0 ? (
                        team.members.map(member => (
                          <ListItem key={member.id}>
                            <ListItemText primary={member.user.full_name} secondary={`Role: ${member.role}, Status: ${member.status}`} />
                          </ListItem>
                        ))
                      ) : (
                        <Typography>No members in this team yet.</Typography>
                      )}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
  
                          <Grid item xs={12}> {/* Team Space Placeholder */}
                            <Box
                              sx={{
                                minHeight: 200, // Make it larger
                                p: 3, // Add padding
                                border: '1px dashed #ccc', // Add a dashed border
                                borderRadius: 2,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                textAlign: 'center',
                                backgroundColor: '#fff',
                                ml: 6, // Push even more to the right
                              }}
                            >
                              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Team Space</Typography>
                              <Typography variant="body2" color="textSecondary">This section is reserved for team activities.</Typography>
                            </Box>
                          </Grid>            </Grid>
          </Grid>
  
          {isLeader && !isTeamFull && (
            <Grid item xs={12} md={4} sx={{ ml: 'auto' }}> {/* Recommendations on the right */}
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Recruit Members</Typography>
                  {recLoading && <CircularProgress size={24} sx={{ mt: 2, display: 'block', mx: 'auto' }} />} 
                  {recommendations.length > 0 && (
                    <Box className="recommendations-section">
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>Recommended Teammates</Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                        {recommendations.map(user => (
                            <Card elevation={1} key={user.id}>
                              <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 1 }}>
                                <Avatar 
                                  src={user.profile_image_url ? `${BACKEND_URL}${user.profile_image_url}` : '/images/basic_profile.png'} 
                                  alt={user.full_name}
                                  sx={{ width: 60, height: 60, mb: 1 }} // Larger avatar for individual cards
                                />
                                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{user.full_name}</Typography>
                                <Typography variant="body2" color="textSecondary">{user.major}</Typography>
                                <Button 
                                  size="small" 
                                  variant="contained" 
                                  onClick={() => handleInviteUser(user.id)}
                                  sx={{
                                    mt: 1,
                                    backgroundColor: '#A5D6A7',
                                    color: 'white',
                                    fontWeight: 'bold',
                                    textTransform: 'none',
                                    '&:hover': {
                                      backgroundColor: '#66BB6A'
                                    }
                                  }}
                                >
                                  Invite
                                </Button>
                              </CardContent>
                            </Card>
                        ))}
                      </Box>
                                      </Box>
                                  )}
                                </CardContent>              </Card>
            </Grid>
          )}
        </Grid>
      </Container>
    );
  }
export default TeamDetail;
