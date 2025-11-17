import React, { useState, useEffect, useRef, useCallback } from 'react';
import { IconButton, Button } from '@mui/material'; // Import IconButton and Button
import AddIcon from '@mui/icons-material/Add'; // Import AddIcon
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import axios from 'axios'; // Import axios
import './Messenger.css';

const Messenger = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [showNewConversationModal, setShowNewConversationModal] = useState(false);
  const [teamMembers, setTeamMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchedUsers, setSearchedUsers] = useState([]); // Changed from searchedUser to searchedUsers
  const socket = useRef(null);
  const messagesEndRef = useRef(null); // Ref for the end of messages
  const userId = JSON.parse(localStorage.getItem('user'))?.id;
  console.log('Messenger component rendering. userId:', userId); // Log userId at component render

  // Debounce function
  const debounce = (func, delay) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, delay);
    };
  };

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await fetch('/api/v1/conversations/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          const sortedConversations = data.sort((a, b) => {
            if (!a.latest_message) return 1;
            if (!b.latest_message) return -1;
            return new Date(b.latest_message.created_at) - new Date(a.latest_message.created_at);
          });
          setConversations(sortedConversations);
        } else {
          console.error('Failed to fetch conversations');
        }
      } catch (error) {
        console.error('Error fetching conversations:', error);
      }
    };

    fetchConversations();
  }, []);

  useEffect(() => {
    if (showNewConversationModal) {
      const fetchTeamMembers = async () => {
        try {
          const response = await fetch('/api/v1/teams/my', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
          });
          if (response.ok) {
            const teams = await response.json();
            const uniqueTeamMembers = new Map();
            teams.forEach(team => {
              team.members.forEach(member => {
                if (member.user.id !== userId) { // Exclude current user
                  uniqueTeamMembers.set(member.user.id, member.user);
                }
              });
            });
            setTeamMembers(Array.from(uniqueTeamMembers.values()));
          } else {
            console.error('Failed to fetch team members');
          }
        } catch (error) {
          console.error('Error fetching team members:', error);
        }
      };
      fetchTeamMembers();
    }
  }, [showNewConversationModal, userId]);

  const handleSearchQueryChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    console.log('Search Query:', query); // Log search query
    performSearch(query);
  };

  const performSearch = useCallback(debounce(async (query) => {
    if (query.trim() === '') {
      setSearchedUsers([]);
      return;
    }
    try {
      const url = `/api/v1/users/search?query=${query}`;
      console.log('Fetching search results from:', url); // Log URL
      const response = await fetch(url , {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      console.log('Search API Response OK:', response.ok); // Log response status
      if (response.ok) {
        const users = await response.json();
        console.log('Users found:', users); // Log users data
        setSearchedUsers(users.filter(user => user.id !== userId).slice(0, 3)); // Exclude current user and limit to 3
      } else {
        console.error('Failed to search users');
        setSearchedUsers([]);
      }
    } catch (error) {
      console.error('Error searching users:', error);
      setSearchedUsers([]);
    }
  }, 300), [userId]); // Debounce for 300ms

  useEffect(() => {
    if (selectedConversation) {
      const fetchMessages = async () => {
        try {
          const response = await fetch(`/api/v1/conversations/${selectedConversation.id}/messages`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
          });
          if (response.ok) {
            const data = await response.json();
            setMessages(data);
          } else {
            console.error('Failed to fetch messages');
          }
        } catch (error) {
          console.error('Error fetching messages:', error);
        }
      };

      fetchMessages();
    }
  }, [selectedConversation]);

  useEffect(() => {
    if (userId) {
      socket.current = new WebSocket(`ws://localhost:8000/api/v1/ws/${userId}`);

      socket.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (selectedConversation && message.conversation_id === selectedConversation.id) {
          setMessages((prevMessages) => [...prevMessages, message]);
        }

        setConversations(prevConversations => {
          const updatedConversations = prevConversations.map(convo => {
            if (convo.id === message.conversation_id) {
              return { ...convo, latest_message: message };
            }
            return convo;
          });

          return updatedConversations.sort((a, b) => {
            if (!a.latest_message) return 1;
            if (!b.latest_message) return -1;
            return new Date(b.latest_message.created_at) - new Date(a.latest_message.created_at);
          });
        });
      };

      return () => {
        socket.current.close();
      };
    }
  }, [selectedConversation, userId]);



  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages, selectedConversation]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() === '' || !selectedConversation) return;

    try {
      const response = await fetch(`/api/v1/conversations/${selectedConversation.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({ content: newMessage }),
      });

      if (response.ok) {
        setNewMessage('');
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const startNewConversationWithUser = async (member) => {
    try {
      // Check if a conversation with this user already exists
      const existingConversation = conversations.find(convo => 
        convo.participants.some(p => p.id === member.id)
      );

      if (existingConversation) {
        setSelectedConversation(existingConversation);
        setShowNewConversationModal(false);
        return;
      }

      // If not, create a new conversation
      const requestBody = { participant_ids: [Number(member.id), Number(userId)], type: "dm" };
      console.log('Request Body for new conversation:', requestBody, 'member.id:', member.id, 'userId:', userId); // Log request body and individual IDs
      const response = await fetch('/api/v1/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const newConvo = await response.json();
        setConversations((prev) => [newConvo, ...prev]);
        setSelectedConversation(newConvo);
        setShowNewConversationModal(false);
      } else {
        console.error('Failed to create new conversation');
      }
    } catch (error) {
      console.error('Error starting new conversation:', error);
    }
  };

  const getConversationDisplayData = (convo, currentUserId) => {
    let name = 'Conversation';
    if (convo.type === 'dm') {
      const otherParticipant = convo.participants.find(p => p.id !== currentUserId);
      if (otherParticipant) {
        name = otherParticipant.full_name;
      }
    } else if (convo.type === 'team') {
      name = 'Team Chat'; // Placeholder
    }

    const latestMessageContent = convo.latest_message ? (() => {
      try {
        const parsedContent = JSON.parse(convo.latest_message.content);
        if (parsedContent.type === 'team_invitation') {
          return `${parsedContent.inviter_name} has invited you to join ${parsedContent.team_name}!`;
        }
      } catch (e) {
        // Not JSON, or not an invitation type, fall through to default
      }
      return convo.latest_message.content;
    })() : 'No messages yet';

    return { name, latestMessageContent };
  };

  const handleInvitationResponse = async (token, accept) => {
    try {
      const response = await axios.post(`/api/v1/teams/invitations/${token}/respond`, 
        null, // No request body
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
          params: {
            accept: accept,
          },
        }
      );
      if (response.status === 200) {
        alert(accept ? 'Invitation accepted!' : 'Invitation rejected.');
        // Optionally refresh conversations or navigate
        // navigate(`/teams/${response.data.team_id}`); // If accepted, navigate to team page
        // For now, just refresh messages and conversations
        setSelectedConversation(null); // Clear selected conversation to force re-fetch
        // Trigger re-fetch of conversations
        const fetchConversations = async () => {
          try {
            const response = await fetch('/api/v1/conversations/', {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
              },
            });
            if (response.ok) {
              const data = await response.json();
              const sortedConversations = data.sort((a, b) => {
                if (!a.latest_message) return 1;
                if (!b.latest_message) return -1;
                return new Date(b.latest_message.created_at) - new Date(a.latest_message.created_at);
              });
              setConversations(sortedConversations);
            } else {
              console.error('Failed to fetch conversations');
            }
          } catch (error) {
            console.error('Error fetching conversations:', error);
          }
        };
        fetchConversations();

      } else {
        alert('Failed to respond to invitation.');
      }
    } catch (error) {
      console.error('Error responding to invitation:', error.response ? error.response.data : error);
      alert(`Error: ${error.response?.data?.detail || 'Failed to respond to invitation.'}`);
    }
  };

  const InvitationMessage = ({ message, onRespond, selectedConversation, userId }) => {
    const [invitationStatus, setInvitationStatus] = useState(null);
    let invitationData;

    try {
      invitationData = JSON.parse(message.content);
      if (invitationData.type !== 'team_invitation') {
        return <p>{message.content}</p>;
      }
    } catch (e) {
      return <p>{message.content}</p>;
    }

    const { team_name, inviter_name, token } = invitationData;
    const inviter = message.sender;
    const invited = selectedConversation.participants.find(p => p.id !== inviter.id);


    useEffect(() => {
      const fetchInvitationStatus = async () => {
        try {
          const response = await fetch(`/api/v1/teams/invitations/${token}/status`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
          });
          if (response.ok) {
            const data = await response.json();
            setInvitationStatus(data.status);
          } else {
            console.error('Failed to fetch invitation status');
          }
        } catch (error) {
          console.error('Error fetching invitation status:', error);
        }
      };

      if (token) {
        fetchInvitationStatus();
      }
    }, [token]);

    const handleRespond = (accept) => {
      onRespond(token, accept);
      setInvitationStatus(accept ? 'accepted' : 'rejected');
    };

    return (
      <div className="messenger-invitation-card">
        <p><strong>{inviter_name}</strong> has invited you to join team <strong>{team_name}</strong>.</p>
        {message.sender.id !== userId && invitationStatus === 'pending' && (
          <div className="messenger-invitation-actions">
            <button className="accept-button" onClick={() => handleRespond(true)}>Accept</button>
            <button className="reject-button" onClick={() => handleRespond(false)}>Reject</button>
          </div>
        )}
        {invitationStatus === 'accepted' && (
          <p>
            {userId === invited.id
              ? 'You have accepted this invitation.'
              : `${invited.full_name} has accepted the invitation.`}
          </p>
        )}
        {invitationStatus === 'rejected' && (
          <p>
            {userId === invited.id
              ? 'You have rejected this invitation.'
              : `${invited.full_name} has rejected the invitation.`}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="messenger-container">
      <div className="messenger-sidebar">
        <div className="messenger-sidebar-header">
          <h3>Conversations</h3>
          <IconButton
            color="primary"
            onClick={() => setShowNewConversationModal(true)}
            sx={{
              width: '60px',
              height: '40px',
              borderRadius: '4px',
              // Override default IconButton padding if necessary
              padding: '8px', // Adjust padding to control icon size within the button
            }}
          >
            <AddIcon />
          </IconButton>
        </div>
        {showNewConversationModal && (
          <div className="new-conversation-modal">
            <div className="new-conversation-modal-content">
              <div className="new-conversation-modal-header">
                <h4>Start New Conversation</h4>
                <button className="close-modal-button" onClick={() => setShowNewConversationModal(false)}>X</button>
              </div>
              <input
                type="text"
                placeholder="Search all users by name or email..."
                className="new-conversation-search-input"
                value={searchQuery}
                onChange={handleSearchQueryChange}
              />
              {searchedUsers.length > 0 && (
                <div className="searched-users-results">
                  <h4>Search Results</h4>
                  {searchedUsers.map((user) => (
                    user.id !== userId && (
                      <div key={user.id} className="searched-user-profile">
                        <p>{user.full_name} ({user.email}) {user.id === userId && "(me)"}</p>
                        <button onClick={() => startNewConversationWithUser(user)}>Start Chat</button>
                      </div>
                    )
                  ))}
                </div>
              )}
              <div className="new-conversation-member-list">
                <h4>My Team Members</h4>
                {teamMembers.length > 0 ? (
                  teamMembers.map((member) => ( // Removed slice(0, 3)
                    <div key={member.id} className="new-conversation-member-item" onClick={() => startNewConversationWithUser(member)}>
                      {member.full_name} ({member.email}) {member.id === userId && "(me)"}
                    </div>
                  ))
                ) : (
                  <p>No team members found.</p>
                )}
              </div>
            </div>
          </div>
        )}
        <div className="messenger-conversation-list">
          {conversations.map((convo) => {
            const { name, latestMessageContent, otherParticipantProfileImage } = getConversationDisplayData(convo, userId);
            const conversationName = name || (selectedConversation?.participants?.find(p => p.id !== userId)?.full_name);
            return (
              <div
                key={convo.id}
                className={`messenger-conversation-item ${selectedConversation?.id === convo.id ? 'selected' : ''}`}
                onClick={() => setSelectedConversation(convo)}
              >
                {otherParticipantProfileImage && (
                  <img src={otherParticipantProfileImage} alt="Profile" className="messenger-conversation-profile-picture" />
                )}
                <div className="messenger-conversation-info"> {/* New wrapper for name and message */}
                  <p className="messenger-conversation-name">{conversationName}</p>
                  <p className="messenger-latest-message">{latestMessageContent}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="messenger-chat-window">
        {selectedConversation ? (
          <>
            <div className="messenger-chat-header">
              <h3>{getConversationDisplayData(selectedConversation, userId).name}</h3>
            </div>
            <div className="messenger-message-list" ref={messagesEndRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`messenger-message-item ${msg.sender.id === userId ? 'sent' : 'received'}`}>
                  {msg.sender.id !== userId && ( // Only show profile for received messages on the left
                    <img src={msg.sender.profile_image_url} alt={msg.sender.full_name} className="messenger-profile-picture" />
                  )}
                  <div className="messenger-message-content-wrapper"> {/* New wrapper for header and bubble */}
                    <div className="messenger-message-header">
                      <span className="messenger-sender-name">{msg.sender.full_name}</span>
                    </div>
                    <div className="messenger-message-bubble">
                      <div className="messenger-message-content">
                        {(() => {
                          try {
                            const parsedContent = JSON.parse(msg.content);
                            if (parsedContent.type === 'team_invitation') {
                              return <InvitationMessage message={msg} onRespond={handleInvitationResponse} selectedConversation={selectedConversation} userId={userId} />;
                            }
                          } catch (e) {
                            // Not JSON, or not an invitation type, render as plain text
                          }
                          return (
                            <>
                              {msg.reply_to_message_id && (
                                <div className="messenger-reply-indicator">
                                  Replying to message ID: {msg.reply_to_message_id}
                                </div>
                              )}
                              <p>{msg.content}</p>
                            </>
                          );
                        })()}
                      </div>
                      <div className="messenger-message-time-container">
                        <span className="messenger-message-time">{new Date(msg.created_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                  {msg.sender.id === userId && ( // Only show profile for sent messages on the right
                    <img src={msg.sender.profile_image_url} alt={msg.sender.full_name} className="messenger-profile-picture" />
                  )}
                </div>
              ))}
            </div>
            <form className="messenger-message-input-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
              />
              <button type="submit" disabled={newMessage.trim() === ''}>Send</button>
            </form>
          </>
        ) : (
          <div className="messenger-no-conversation-selected">
            <p>Select a conversation to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Messenger;