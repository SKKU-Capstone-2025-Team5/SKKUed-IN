import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Profile.css'; // Import the new CSS file

// Predefined skills and interests
const DEFAULT_SKILLS = [
  "Python", "Java", "C++", "SQL", "R", "NLP", "ML", "DL", "React", "Node.js",
  "Docker", "AWS", "Pandas", "TensorFlow", "Figma", "UI/UX"
];

const DEFAULT_INTERESTS = [
  "Backend", "Frontend", "Full-Stack", "Cloud", "AI",
  "Recommender", "Analytics", "Fintech", "Startup", "Hackathon"
];

function Profile() {
  const [profile, setProfile] = useState({
    full_name: '',
    major: '',
    age: '',
    phone_number: '',
    introduction: '',
    profile_image_url: '',
    phone_number_public: true,
    age_public: true,
  });
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [customSkill, setCustomSkill] = useState('');
  const [customInterest, setCustomInterest] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  useEffect(() => {
    console.log('Profile component mounted or re-mounted. Fetching profile...');
    const fetchProfile = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('No access token found. Please login.');
        setLoading(false);
        console.log('No access token found.');
        return;
      }

      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/profile/me', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const data = response.data;
        console.log('Fetched profile data:', data);
        setProfile(data);
        const skillsFromData = data.skills ? data.skills.map(s => s.name) : [];
        const interestsFromData = data.interests ? data.interests.map(i => i.name) : [];
        setSelectedSkills(skillsFromData);
        setSelectedInterests(interestsFromData);
        console.log('Selected Skills after fetch:', skillsFromData);
        console.log('Selected Interests after fetch:', interestsFromData);

        if (data.profile_image_url) {
          setFilePreview(`http://127.0.0.1:8000${data.profile_image_url}`);
        }
      } catch (err) {
        console.error('Failed to fetch profile:', err);
        setError('Failed to fetch profile. Please login again.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfile(prevState => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) {
      setFilePreview(URL.createObjectURL(file));
    } else {
      setFilePreview(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.post('http://127.0.0.1:8000/api/v1/uploads/uploadfile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });
      const imageUrl = response.data.url;
      setProfile(prevState => ({
        ...prevState,
        profile_image_url: imageUrl
      }));

      // Automatically update the profile in the backend with the new image URL
      await axios.put('http://127.0.0.1:8000/api/v1/profile/me', { profile_image_url: imageUrl }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      alert('Image uploaded and profile updated successfully!');
      setError('');
    } catch (err) {
      console.error('Upload error:', err.response ? err.response.data : err);
      setError('Failed to upload image. Check console for details.');
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('accessToken');
    setError('');

    const dataToSubmit = {
        ...profile,
        skills: selectedSkills,
        interests: selectedInterests,
    };

    console.log('Data being submitted:', dataToSubmit);
    console.log('Selected Skills being submitted:', selectedSkills);
    console.log('Selected Interests being submitted:', selectedInterests);

    try {
      await axios.put('http://127.0.0.1:8000/api/v1/profile/me', dataToSubmit, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      alert('Profile updated successfully!');
    } catch (err) {
        console.error('Update error:', err.response ? err.response.data : err);
        setError('Failed to update profile. Check console for details.');
    }
  };

  const toggleSkill = (skill) => {
    console.log('Toggling skill:', skill);
    setSelectedSkills(prev => {
      const newState = prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill];
      console.log('New selectedSkills state:', newState);
      return newState;
    });
  };

  const addCustomSkill = () => {
    if (customSkill && !selectedSkills.includes(customSkill)) {
      console.log('Adding custom skill:', customSkill);
      setSelectedSkills(prev => {
        const newState = [...prev, customSkill];
        console.log('New selectedSkills state:', newState);
        return newState;
      });
      setCustomSkill('');
    }
  };

  const toggleInterest = (interest) => {
    console.log('Toggling interest:', interest);
    setSelectedInterests(prev => {
      const newState = prev.includes(interest) ? prev.filter(i => i !== interest) : [...prev, interest];
      console.log('New selectedInterests state:', newState);
      return newState;
    });
  };

  const addCustomInterest = () => {
    if (customInterest && !selectedInterests.includes(customInterest)) {
      console.log('Adding custom interest:', customInterest);
      setSelectedInterests(prev => {
        const newState = [...prev, customInterest];
        console.log('New selectedInterests state:', newState);
        return newState;
      });
      setCustomInterest('');
    }
  };

  if (loading) {
    return <div className="profile-container">Loading profile...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h2>My Page</h2>
      </div>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleUpdate} className="profile-form">
        <div className="profile-image-section">
          <div className="profile-left-col">
            <div className="profile-image-controls"> {/* New wrapper for horizontal layout */}
              <div className="profile-image-preview">
                {filePreview ? (
                  <img src={filePreview} alt="Profile Preview" />
                ) : (
                  <div className="profile-image-placeholder">No Image</div>
                )}
              </div>
              <div className="profile-image-upload">
                <input type="file" id="file-upload" accept="image/*" onChange={handleFileChange} />
                <label htmlFor="file-upload" className="file-upload-label">Choose File</label>
                <button type="button" onClick={handleUpload} disabled={!selectedFile}>Upload Image</button>
              </div>
            </div> {/* End of profile-image-controls */}
          </div>
          <div className="profile-right-col">
            <div>
              <label>Full Name:</label>
              <input type="text" name="full_name" value={profile.full_name || ''} onChange={handleChange} />
            </div>
            <div>
              <label>Age:</label>
              <input type="text" name="age" value={profile.age || ''} onChange={handleChange} />
            </div>
          </div>
        </div>
        <div className="profile-major-phone-section"> {/* New section for Major and Phone Number */}
          <div>
            <label>Major:</label>
            <input type="text" name="major" value={profile.major || ''} onChange={handleChange} />
          </div>
          <div>
            <label>Phone Number:</label>
            <input type="text" name="phone_number" value={profile.phone_number || ''} onChange={handleChange} />
          </div>
        </div>
        <div>
          <label>Introduction:</label>
          <textarea name="introduction" value={profile.introduction || ''} onChange={handleChange} />
        </div>

        {/* Skills Selection */}
        <div>
          <label>Core Skills:</label>
          <div className="tag-selection-container">
            {DEFAULT_SKILLS.map(skill => (
              <button 
                key={skill} 
                type="button" 
                className={`tag-button ${selectedSkills.includes(skill) ? 'selected' : ''}`}
                onClick={() => toggleSkill(skill)}
              >
                {skill}
              </button>
            ))}
          </div>
          <div className="custom-tag-input">
            <input 
              type="text" 
              value={customSkill} 
              onChange={(e) => setCustomSkill(e.target.value)} 
              placeholder="Add custom skill"
            />
            <button type="button" onClick={addCustomSkill}>Add</button>
          </div>
          <div className="selected-tags">
            {selectedSkills.map((skill, index) => (
              <span key={index} className="selected-tag">{skill} <button type="button" onClick={() => toggleSkill(skill)}>x</button></span>
            ))}
          </div>
        </div>

        {/* Interests Selection */}
        <div>
          <label>Interests:</label>
          <div className="tag-selection-container">
            {DEFAULT_INTERESTS.map(interest => (
              <button 
                key={interest} 
                type="button" 
                className={`tag-button ${selectedInterests.includes(interest) ? 'selected' : ''}`}
                onClick={() => toggleInterest(interest)}
              >
                {interest}
              </button>
            ))}
          </div>
          <div className="custom-tag-input">
            <input 
              type="text" 
              value={customInterest} 
              onChange={(e) => setCustomInterest(e.target.value)} 
              placeholder="Add custom interest"
            />
            <button type="button" onClick={addCustomInterest}>Add</button>
          </div>
          <div className="selected-tags">
            {selectedInterests.map((interest, index) => (
              <span key={index} className="selected-tag">{interest} <button type="button" onClick={() => toggleInterest(interest)}>x</button></span>
            ))}
          </div>
        </div>

        <div>
          <label>
            <input type="checkbox" name="phone_number_public" checked={profile.phone_number_public || false} onChange={handleChange} />
            Make phone number public
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" name="age_public" checked={profile.age_public || false} onChange={handleChange} />
            Make age public
          </label>
        </div>
        <button type="submit">Update Profile</button>
      </form>
    </div>
  );
}

export default Profile;