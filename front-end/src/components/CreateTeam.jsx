import React, { useState } from 'react';
import {
  Container, Typography, TextField, Button, Box, Card, CardContent, CardActions,
  CircularProgress, Alert, List, ListItem, ListItemText, ListItemAvatar, Avatar
} from '@mui/material';
import './CreateTeam.css';

function CreateTeam() {
  const [teamName, setTeamName] = useState('');
  const [description, setDescription] = useState('');
  const [memberLimit, setMemberLimit] = useState(2);
  const [createdTeam, setCreatedTeam] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

    try {
      const response = await fetch('/api/v1/teams/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ name: teamName, description, member_limit: parseInt(memberLimit, 10) }),
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
      alert('Team created successfully! Now you can get recommendations.');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('You must be logged in to fetch recommendations.');
      setLoading(false);
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
      
      {!createdTeam ? (
        <Box component="form" onSubmit={handleCreateTeam} className="create-team-form">
          <TextField
            label="Team Name"
            variant="outlined"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Description"
            variant="outlined"
            multiline
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            fullWidth
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
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" variant="contained" className="green-button-contained" disabled={loading} sx={{ mt: 2 }}>
              {loading ? <CircularProgress size={24} /> : 'Create team'}
            </Button>
          </Box>
        </Box>
      ) : (
        <Box>
          <Typography variant="h5" component="h2" gutterBottom>
            Team "{createdTeam.name}" Created!
          </Typography>
          <Button variant="contained" className="green-button-contained" onClick={fetchRecommendations} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Find teammates'}
          </Button>
          
          {recommendations.length > 0 && (
            <Box className="recommendations-section">
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
                    <Button
                      variant="outlined"
                      className="invite-button green-button-outlined"
                      onClick={() => handleInviteUser(user.id)}
                    >
                      Invite
                    </Button>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      )}
    </Container>
  );
}

export default CreateTeam;
