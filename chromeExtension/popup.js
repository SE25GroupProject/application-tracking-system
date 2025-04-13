document.addEventListener('DOMContentLoaded', () => {
    const authSection = document.getElementById('auth-section');
    const contentSection = document.getElementById('content-section');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('login-btn');
    const fetchDataBtn = document.getElementById('fetch-data-btn');
    const autofillBtn = document.getElementById('autofill-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userNameSpan = document.getElementById('user-name');
    const apiResult = document.getElementById('api-result');
    const profileSelect = document.getElementById('profile-select');
  
    const BASE_URL = 'http://127.0.0.1:5000';
  
    let currentToken = null;
    let selectedProfile = null;
  
    const getToken = async () => {
      return currentToken || (await new Promise(resolve => {
        chrome.storage.local.get(['token'], (result) => resolve(result.token));
      }));
    };
  
    const populateProfiles = async () => {
      const token = await getToken();
      if (!token) {
        apiResult.textContent = 'Not logged in';
        return;
      }
      console.log('populateProfiles Token:', token);
      try {
        const response = await fetch(`${BASE_URL}/users/getProfileList`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('getProfileList Response Status:', response.status);
        console.log('getProfileList Response Headers:', [...response.headers.entries()]);
        const contentType = response.headers.get('Content-Type');
        const rawBody = await response.text();
        console.log('getProfileList Raw Response Body:', rawBody);
  
        if (!contentType || !contentType.includes('application/json')) {
          apiResult.textContent = 'Error: Server returned non-JSON response';
          return;
        }
  
        const data = JSON.parse(rawBody);
        if (response.ok) {
          profileSelect.innerHTML = '';
          if (data.profiles.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No profiles available';
            option.disabled = true;
            profileSelect.appendChild(option);
          } else {
            data.profiles.forEach(profile => {
              const option = document.createElement('option');
              option.value = profile.profileid;
              option.textContent = `${profile.profileName} ${profile.isDefault ? '(Default)' : ''}`;
              profileSelect.appendChild(option);
            });
            profileSelect.value = data.default_profile;
            if (!profileSelect.value && data.profiles.length > 0) {
              profileSelect.value = data.profiles[0].profileid;
              fetchProfileData(data.profiles[0].profileid);
            } else {
              fetchProfileData(data.default_profile);
            }
          }
        } else {
          apiResult.textContent = `Error fetching profiles: ${data.error || 'Unknown error'}`;
        }
      } catch (error) {
        apiResult.textContent = `Error fetching profiles: ${error.message}`;
      }
    };
  
    const fetchProfileData = async (profileId) => {
      const token = await getToken();
      if (!token) {
        apiResult.textContent = 'Not logged in';
        return;
      }
      console.log('fetchProfileData Token:', token);
      try {
        const response = await fetch(`${BASE_URL}/users/getProfile/${profileId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('getProfile Response Status:', response.status);
        console.log('getProfile Response Headers:', [...response.headers.entries()]);
        const contentType = response.headers.get('Content-Type');
        const rawBody = await response.text();
        console.log('getProfile Raw Response Body:', rawBody);
  
        if (!contentType || !contentType.includes('application/json')) {
          apiResult.textContent = 'Error: Server returned non-JSON response';
          return;
        }
  
        const data = JSON.parse(rawBody);
        if (response.ok) {
          selectedProfile = data;
          apiResult.textContent = `Selected profile: ${data.profileName}`;
        } else {
          apiResult.textContent = `Error fetching profile: ${data.error || 'Unknown error'}`;
        }
      } catch (error) {
        apiResult.textContent = `Error fetching profile: ${error.message}`;
      }
    };
  
    const validateToken = async (token) => {
      try {
        const response = await fetch(`${BASE_URL}/users/getProfileList`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        return response.ok;
      } catch (error) {
        return false;
      }
    };
  
    chrome.storage.local.get(['token', 'profile'], async (result) => {
      if (result.token && result.profile) {
        currentToken = result.token;
        const isValid = await validateToken(result.token);
        if (isValid) {
          authSection.style.display = 'none';
          contentSection.style.display = 'block';
          userNameSpan.textContent = result.profile.fullName || 'User';
          populateProfiles();
        } else {
          chrome.storage.local.remove(['token', 'profile'], () => {
            apiResult.textContent = 'Session expired. Please log in again.';
          });
        }
      }
    });
  
    loginBtn.addEventListener('click', async () => {
      const username = usernameInput.value;
      const password = passwordInput.value;
      if (!username || !password) {
        apiResult.textContent = 'Please enter username and password';
        return;
      }
  
      try {
        const response = await fetch(`${BASE_URL}/users/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const rawBody = await response.text();
        console.log('login Raw Response Body:', rawBody);
        const data = JSON.parse(rawBody);
        console.log('Login Response Status:', response.status);
        console.log('Login Response Data:', data);
        console.log('Is response.ok?', response.ok);
  
        if (response.ok && data.token) {
          currentToken = data.token;
          chrome.storage.local.set({ token: data.token, profile: data.profile }, () => {
            console.log('Token stored:', data.token);
            chrome.storage.local.get(['token'], (result) => {
              console.log('Token retrieved after storage:', result.token);
            });
            authSection.style.display = 'none';
            contentSection.style.display = 'block';
            userNameSpan.textContent = data.profile.fullName || 'User';
            apiResult.textContent = 'Login successful';
            populateProfiles();
          });
        } else {
          apiResult.textContent = `Login failed: ${data.error || 'Unknown error'}`;
        }
      } catch (error) {
        apiResult.textContent = `Error: ${error.message}`;
      }
    });
  
    profileSelect.addEventListener('change', () => {
      const profileId = profileSelect.value;
      fetchProfileData(profileId);
    });
  
    fetchDataBtn.addEventListener('click', async () => {
      const token = await getToken();
      if (!token) {
        apiResult.textContent = 'Not logged in';
        return;
      }
      console.log('fetchDataBtn Token:', token);
      try {
        const response = await fetch(`${BASE_URL}/users/protected-endpoint`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('protected-endpoint Response Status:', response.status);
        console.log('protected-endpoint Response Headers:', [...response.headers.entries()]);
        const contentType = response.headers.get('Content-Type');
        const rawBody = await response.text();
        console.log('protected-endpoint Raw Response Body:', rawBody);
  
        if (!contentType || !contentType.includes('application/json')) {
          apiResult.textContent = 'Error: Server returned non-JSON response';
          return;
        }
  
        const data = JSON.parse(rawBody);
        if (response.ok) {
          apiResult.textContent = JSON.stringify(data, null, 2);
        } else {
          apiResult.textContent = `Error: ${data.error || 'Unknown error'}`;
        }
      } catch (error) {
        apiResult.textContent = `Error: ${error.message}`;
      }
    });
  
    autofillBtn.addEventListener('click', () => {
      if (!selectedProfile) {
        apiResult.textContent = 'Please select a profile first';
        return;
      }
  
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tabId = tabs[0].id;
        chrome.scripting.executeScript({
          target: { tabId },
          function: autofillForm,
          args: [selectedProfile]
        }, (results) => {
          if (chrome.runtime.lastError) {
            apiResult.textContent = `Error: ${chrome.runtime.lastError.message}`;
          } else {
            apiResult.textContent = 'Autofill attempted. Check the webpage.';
          }
        });
      });
    });
  
    logoutBtn.addEventListener('click', async () => {
      const token = await getToken();
      if (!token) {
        apiResult.textContent = 'Not logged in';
        return;
      }
      try {
        const response = await fetch(`${BASE_URL}/users/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        const rawBody = await response.text();
        console.log('logout Raw Response Body:', rawBody);
        const data = JSON.parse(rawBody);
  
        if (response.ok) {
          chrome.storage.local.remove(['token', 'profile'], () => {
            currentToken = null;
            authSection.style.display = 'block';
            contentSection.style.display = 'none';
            apiResult.textContent = 'Logged out successfully';
            usernameInput.value = '';
            passwordInput.value = '';
            profileSelect.innerHTML = '';
            selectedProfile = null;
          });
        } else {
          apiResult.textContent = `Error: ${data.error || 'Unknown error'}`;
        }
      } catch (error) {
        apiResult.textContent = `Error: ${error.message}`;
      }
    });
  });
  
  // Autofill function (unchanged)
  function autofillForm(profile) {
    const fieldMappings = {
      fullName: ['name', 'fullName', 'full_name', 'applicant_name'],
      email: ['email', 'email_address', 'applicant_email'],
      phone_number: ['phone', 'phone_number', 'telephone'],
      address: ['address', 'street_address', 'location'],
      institution: ['education', 'institution', 'school'],
      skills: ['skills', 'qualifications'],
      job_levels: ['experience', 'job_level'],
      locations: ['preferred_location', 'location_preference']
    };
  
    const setFieldValue = (field, value) => {
      if (!value) return;
      const possibleNames = fieldMappings[field] || [];
      possibleNames.forEach(name => {
        const inputs = document.querySelectorAll(`input[name="${name}"], input[id="${name}"], textarea[name="${name}"], textarea[id="${name}"]`);
        inputs.forEach(input => {
          if (input.type === 'text' || input.type === 'email' || input.type === 'tel' || input.tagName.toLowerCase() === 'textarea') {
            if (field === 'fullName' && (name.includes('firstName') || name.includes('first_name'))) {
              input.value = profile.fullName.split(' ')[0];
            } else if (field === 'fullName' && (name.includes('lastName') || name.includes('last_name'))) {
              input.value = profile.fullName.split(' ').slice(1).join(' ');
            } else {
              input.value = Array.isArray(value) ? value.join(', ') : value;
            }
          }
        });
        const selects = document.querySelectorAll(`select[name="${name}"], select[id="${name}"]`);
        selects.forEach(select => {
          const options = Array.from(select.options);
          const option = options.find(opt => opt.value === value || opt.textContent === value);
          if (option) select.value = option.value;
        });
      });
    };
  
    Object.keys(fieldMappings).forEach(field => {
      setFieldValue(field, profile[field]);
    });
  
    if (profile.skills && Array.isArray(profile.skills)) {
      const skillFields = document.querySelectorAll('input[name*="skill"], textarea[name*="skill"]');
      profile.skills.forEach((skill, index) => {
        if (skillFields[index]) skillFields[index].value = skill;
      });
    }
  }
  