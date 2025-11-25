import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import {
  Container, Typography, Card, CardContent, Button, Grid, Avatar, Chip, CircularProgress, 
  Alert, Box, List, ListItem, ListItemText, Divider
} from '@mui/material';
import './MyTeams.css';

function MyTeams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication token not found. Please log in.');

      const response = await axios.get('/api/v1/teams/my', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeams(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

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

  return (
    <Container className="my-teams-container" sx={{ maxWidth: '800px' }}>
      <Box className="my-teams-header">
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>My Teams</Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/teams/create')}
          sx={{
            backgroundColor: '#A5D6A7',
            color: 'white',
            fontWeight: 'bold',
            textTransform: 'none',
            '&:hover': {
              backgroundColor: '#66BB6A'
            }
          }}
        >
          Create New Team
        </Button>
      </Box>

      {teams.length === 0 ? (
        <Alert severity="info">You are not a member of any teams yet.</Alert>
      ) : (
        <Box className="team-cards-container">
          {teams.map(team => (
            <Card 
              key={team.id}
              className="team-card"
              elevation={3} // Add elevation for a lifted effect
              sx={{
                transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 8px 16px rgba(0,0,0,0.2)'
                },
                backgroundColor: '#fff', // All cards are white
              }}
            >
              <CardContent className="team-card-content">
                <Typography variant="h5" component="h2" gutterBottom className="team-title">
                  <Link to={`/teams/${team.id}`} style={{ textDecoration: 'none', color: 'inherit', fontWeight: 'bold' }}>{team.name}</Link>
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>{team.description}</Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                  <Chip 
                    label={team.status} 
                    sx={{
                      backgroundColor: team.status.toLowerCase() === 'recruiting' ? '#A5D6A7' : undefined,
                      color: team.status.toLowerCase() === 'recruiting' ? 'white' : undefined,
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Container>
  );
}

export default MyTeams;
