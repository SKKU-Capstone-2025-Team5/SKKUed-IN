import React, { useState, useEffect, useRef, useCallback } from 'react';
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
          setConversations(data);
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
      };

      return () => {
        socket.current.close();
      };
    }
  }, [selectedConversation, userId]);

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

    const latestMessageContent = convo.latest_message ? convo.latest_message.content : 'No messages yet';

    return { name, latestMessageContent };
  };

  return (
    <div className="messenger-container">
      <div className="messenger-sidebar">
        <div className="messenger-sidebar-header">
          <h3>Conversations</h3>
          <button className="new-conversation-button" onClick={() => setShowNewConversationModal(true)}>+</button>
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
                  teamMembers.slice(0, 3).map((member) => (
                    member.user ? (
                      <div key={member.id} className="new-conversation-member-item" onClick={() => startNewConversationWithUser(member.user)}>
                        {member.user.full_name} ({member.user.email}) {member.user.id === userId && "(me)"}
                      </div>
                    ) : null
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
            <div className="messenger-message-list">
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
                        {msg.reply_to_message_id && (
                          <div className="messenger-reply-indicator">
                            Replying to message ID: {msg.reply_to_message_id}
                          </div>
                        )}
                        <p>{msg.content}</p>
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
              <button type="submit">Send</button>
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