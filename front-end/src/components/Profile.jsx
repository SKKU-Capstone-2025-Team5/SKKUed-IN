import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Profile.css'; // Import the new CSS file

function Profile() {
  const [profile, setProfile] = useState({
    full_name: '',
    major: '',
    age: '',
    phone_number: '',
    introduction: '',
    profile_image_url: '',
    core_skill_tags: '',
    interests: '',
    phone_number_public: true,
    age_public: true,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('No access token found. Please login.');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/profile/me', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const data = response.data;
        // Convert array fields to comma-separated strings for editing
        data.core_skill_tags = (data.core_skill_tags || []).join(', ');
        data.interests = (data.interests || []).join(', ');
        setProfile(data);
        if (data.profile_image_url) {
          setFilePreview(`http://127.0.0.1:8000${data.profile_image_url}`);
        }
      } catch (err) {
        console.error('Failed to fetch profile:', err); // Log the error
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
      alert('Image uploaded successfully!');
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

    // Prepare data for submission, converting strings back to arrays
    const dataToSubmit = {
        ...profile,
        core_skill_tags: profile.core_skill_tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        interests: profile.interests.split(',').map(interest => interest.trim()).filter(interest => interest),
    };

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

  if (loading) {
    return <div className="profile-container">Loading profile...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h2>Profile Settings</h2>
        <Link to="/main" className="back-link">Back to Main</Link>
      </div>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleUpdate} className="profile-form">
        <div>
          <label>Full Name:</label>
          <input type="text" name="full_name" value={profile.full_name || ''} onChange={handleChange} />
        </div>
        <div>
          <label>Major:</label>
          <input type="text" name="major" value={profile.major || ''} onChange={handleChange} />
        </div>
        <div>
          <label>Age:</label>
          <input type="text" name="age" value={profile.age || ''} onChange={handleChange} />
        </div>
        <div>
          <label>Phone Number:</label>
          <input type="text" name="phone_number" value={profile.phone_number || ''} onChange={handleChange} />
        </div>
        <div>
          <label>Introduction:</label>
          <textarea name="introduction" value={profile.introduction || ''} onChange={handleChange} />
        </div>
        <div>
          <label>Profile Image:</label>
          {filePreview && (
            <div className="profile-image-preview">
              <img src={filePreview} alt="Profile Preview" style={{ maxWidth: '150px', maxHeight: '150px', borderRadius: '50%', objectFit: 'cover' }} />
            </div>
          )}
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button type="button" onClick={handleUpload} disabled={!selectedFile}>Upload Image</button>
        </div>
        <div>
          <label>Core Skills (comma-separated):</label>
          <input type="text" name="core_skill_tags" value={profile.core_skill_tags || ''} onChange={handleChange} />
          <div className="skill-tag-container">
            {profile.core_skill_tags.split(',').map((tag, index) => tag.trim() && (
              <span key={index} className="skill-tag">{tag.trim()}</span>
            ))}
          </div>
        </div>
        <div>
          <label>Interests (comma-separated):</label>
          <input type="text" name="interests" value={profile.interests || ''} onChange={handleChange} />
          <div className="interest-tag-container">
            {profile.interests.split(',').map((interest, index) => interest.trim() && (
              <span key={index} className="interest-tag">{interest.trim()}</span>
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