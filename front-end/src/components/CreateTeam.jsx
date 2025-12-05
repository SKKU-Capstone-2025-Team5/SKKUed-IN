import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom'; // Added useLocation
import {
  Container, Typography, TextField, Button, Box, Card, CardContent, CardActions,
  CircularProgress, Alert, List, ListItem, ListItemText, ListItemAvatar, Avatar
} from '@mui/material';
import './CreateTeam.css';

function CreateTeam() {
  const navigate = useNavigate();
  const location = useLocation(); // Get current location
  const queryParams = new URLSearchParams(location.search);
  const contestId = queryParams.get('contestId'); // Get contestId from URL

  const [teamName, setTeamName] = useState('');
  const [description, setDescription] = useState('');
  const [memberLimit, setMemberLimit] = useState(2);
  const [createdTeam, setCreatedTeam] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);

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

  useEffect(() => {
    if (createdTeam) {
      fetchRecommendations();
    }
  }, [createdTeam]); // Fetch recommendations when createdTeam changes

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('You must be logged in to create a team.');
      setLoading(false);
      return;
    }

    const teamData = {
      name: teamName,
      description,
      member_limit: parseInt(memberLimit, 10),
    };

    if (contestId) { // Add contest_id if present
      teamData.contest_id = parseInt(contestId, 10);
    }

    try {
      const response = await fetch('/api/v1/teams/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(teamData), // Use teamData
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          throw new Error(errorText || 'Failed to create team');
        }
        throw new Error(errorData.detail || 'Failed to create team');
      }

      const newTeam = await response.json();
      setCreatedTeam(newTeam);
      alert('Team created successfully! You can now invite recommended teammates.');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteUser = async (userId) => {
    const token = localStorage.getItem('accessToken');
    if (!token || !createdTeam) {
      setError('Cannot invite user. Make sure you are logged in and have created a team.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/teams/${createdTeam.id}/invite`, {
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
      setError(err.message);
      alert(`Error inviting user: ${err.message}`);
    }
  };

  return (
    <Container className="create-team-container">
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        Create New Team
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      
      {!createdTeam && (
        <Box component="form" onSubmit={handleCreateTeam} className="create-team-form">
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Team Name"
            variant="outlined"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            required
            fullWidth
            sx={{ flex: 1 }}
          />
          <TextField
            label="Member Limit"
            variant="outlined"
            type="number"
            value={memberLimit}
            onChange={(e) => setMemberLimit(e.target.value)}
            inputProps={{ min: 2 }}
            required
            fullWidth
            sx={{ flex: 1 }}
          />
        </Box>
        <TextField
          label="Description"
          variant="outlined"
          multiline
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          fullWidth
          sx={{ mb: 2 }}
        />
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button type="submit" variant="contained" className="green-button-contained" disabled={loading} sx={{ mt: 2 }}>
            {loading ? <CircularProgress size={24} /> : 'Create team'}
          </Button>
        </Box>
      </Box>
      )}

      {createdTeam && (
        <>
          {recommendationsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            recommendations.length > 0 && (
              <Box className="recommendations-section" sx={{ mt: 4 }}>
                <Typography variant="h6" component="h3">Recommended Teammates</Typography>
                <List className="recommendations-list">
                  {recommendations.map((user) => (
                    <ListItem key={user.id} className="recommendation-item">
                      <ListItemAvatar>
                        <Avatar src={user.profile_image_url || '/images/basic_profile.png'} />
                      </ListItemAvatar>
                      <ListItemText
                        primary={user.full_name}
                        secondary={
                          <>
                            <Typography component="span" variant="body2" color="text.primary">
                              {user.email}
                            </Typography>
                            {` — Major: ${user.major}`}
                          </>
                        }
                      />
                      <Box sx={{ width: '100%', display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                        <Button
                          variant="outlined"
                          className="invite-button green-button-outlined"
                          onClick={() => handleInviteUser(user.id)}
                          disabled={!createdTeam} // Disable invite button if no team is created yet
                        >
                          Invite
                        </Button>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )
          )}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button variant="contained" className="green-button-contained" onClick={() => navigate(`/teams/${createdTeam.id}`)}>
              Go to Team Page
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
}

export default CreateTeam;