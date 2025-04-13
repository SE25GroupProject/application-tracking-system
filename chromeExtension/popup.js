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
  const resumeSelect = document.getElementById('resume-select');

  const BASE_URL = 'http://127.0.0.1:5000';

  let currentToken = null;
  let selectedProfile = null;
  let selectedResumeIdx = null;

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
    try {
      const response = await fetch(`${BASE_URL}/getProfileList`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const contentType = response.headers.get('Content-Type');
      const rawBody = await response.text();

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

  const populateResumes = async () => {
    const token = await getToken();
    if (!token) {
      apiResult.textContent = 'Not logged in';
      return;
    }
    try {
      const response = await fetch(`${BASE_URL}/resume`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const contentType = response.headers.get('Content-Type');
      const rawBody = await response.text();

      if (!contentType || !contentType.includes('application/json')) {
        apiResult.textContent = 'Error: Server returned non-JSON response';
        return;
      }

      const data = JSON.parse(rawBody);
      if (response.ok) {
        resumeSelect.innerHTML = '';
        if (data.filenames.length === 0) {
          const option = document.createElement('option');
          option.value = '';
          option.textContent = 'No resumes available';
          option.disabled = true;
          resumeSelect.appendChild(option);
        } else {
          data.filenames.forEach((filename, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = filename;
            resumeSelect.appendChild(option);
          });
          resumeSelect.value = data.filenames.length > 0 ? '0' : '';
          selectedResumeIdx = resumeSelect.value;
        }
      } else {
        apiResult.textContent = `Error fetching resumes: ${data.error || 'Unknown error'}`;
      }
    } catch (error) {
      apiResult.textContent = `Error fetching resumes: ${error.message}`;
    }
  };

  const fetchProfileData = async (profileId) => {
    const token = await getToken();
    if (!token) {
      apiResult.textContent = 'Not logged in';
      return;
    }
    try {
      const response = await fetch(`${BASE_URL}/getProfile/${profileId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const contentType = response.headers.get('Content-Type');
      const rawBody = await response.text();

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
      const response = await fetch(`${BASE_URL}/getProfileList`, {
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
        populateResumes();
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
      const data = JSON.parse(rawBody);

      if (response.ok && data.token) {
        currentToken = data.token;
        chrome.storage.local.set({ token: data.token, profile: data.profile }, () => {
          authSection.style.display = 'none';
          contentSection.style.display = 'block';
          userNameSpan.textContent = data.profile.fullName || 'User';
          apiResult.textContent = 'Login successful';
          populateProfiles();
          populateResumes();
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

  resumeSelect.addEventListener('change', () => {
    selectedResumeIdx = resumeSelect.value;
  });

  autofillBtn.addEventListener('click', async () => {
    if (!selectedProfile) {
      apiResult.textContent = 'Please select a profile first';
      return;
    }
    if (selectedResumeIdx === null) {
      apiResult.textContent = 'Please select a resume first';
      return;
    }

    // Fetch resume file
    let resumeBlob = null;
    let resumeFilename = null;
    try {
      const token = await getToken();
      const response = await fetch(`${BASE_URL}/resume/${selectedResumeIdx}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        resumeBlob = await response.blob();
        resumeFilename = response.headers.get('x-filename') || `resume_${selectedResumeIdx}.pdf`;
      } else {
        const data = await response.json();
        apiResult.textContent = `Error fetching resume: ${data.error || 'Unknown error'}`;
        return;
      }
    } catch (error) {
      apiResult.textContent = `Error fetching resume: ${error.message}`;
      return;
    }

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0].id;
      chrome.scripting.executeScript({
        target: { tabId },
        function: autofillForm,
        args: [selectedProfile, resumeBlob, resumeFilename]
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
          resumeSelect.innerHTML = '';
          selectedProfile = null;
          selectedResumeIdx = null;
        });
      } else {
        apiResult.textContent = `Error: ${data.error || 'Unknown error'}`;
      }
    } catch (error) {
      apiResult.textContent = `Error: ${error.message}`;
    }
  });
});

function autofillForm(profile, resumeBlob, resumeFilename) {
  const fieldMappings = {
    fullName: ['name', 'fullName', 'full_name', 'applicant_name'],
    firstName: ['firstName', 'first_name', 'givenName', 'given_name'],
    lastName: ['lastName', 'last_name', 'surname', 'familyName', 'family_name'],
    email: ['email', 'email_address', 'applicant_email'],
    phone_number: ['phone', 'phone_number', 'telephone'],
    address: ['address', 'street_address', 'location'],
    addressLine1: ['addressLine1', 'address_line1', 'streetAddress', 'street_address1', 'address1'],
    city: ['city', 'town', 'city_name', 'candidate-location'],
    state: ['state', 'region', 'state_province', 'province'],
    zipCode: ['zip', 'zipCode', 'zip_code', 'postal', 'postalCode', 'postal_code'],
    institution: ['education', 'institution', 'school'],
    skills: ['skills', 'qualifications'],
    job_levels: ['experience', 'job_level'],
    locations: ['preferred_location', 'location_preference']
  };

  const setFieldValue = (field, value) => {
    if (!value && value !== '') return; // Allow empty string for lastName
    const possibleNames = fieldMappings[field] || [];
    possibleNames.forEach(name => {
      // Handle text inputs and textareas
      const inputs = document.querySelectorAll(`input[name="${name}"], input[id="${name}"], textarea[name="${name}"], textarea[id="${name}"]`);
      inputs.forEach(input => {
        if (input.type === 'text' || input.type === 'email' || input.type === 'tel' || input.tagName.toLowerCase() === 'textarea' || input.getAttribute('role') === 'combobox') {
          input.value = Array.isArray(value) ? value.join(', ') : value;
          // Dispatch input event
          const inputEvent = new Event('input', { bubbles: true });
          input.dispatchEvent(inputEvent);
          // Dispatch change event
          const changeEvent = new Event('change', { bubbles: true });
          input.dispatchEvent(changeEvent);
          // For comboboxes like React Select, simulate Enter to select
          if (input.getAttribute('role') === 'combobox') {
            const keydownEvent = new KeyboardEvent('keydown', {
              bubbles: true,
              key: 'Enter',
              code: 'Enter',
              keyCode: 13
            });
            input.dispatchEvent(keydownEvent);
          }
        }
      });
      // Handle select elements
      const selects = document.querySelectorAll(`select[name="${name}"], select[id="${name}"]`);
      selects.forEach(select => {
        const options = Array.from(select.options);
        const option = options.find(opt => opt.value === value || opt.textContent === value || opt.value.toLowerCase() === value.toLowerCase());
        if (option) {
          select.value = option.value;
          const changeEvent = new Event('change', { bubbles: true });
          select.dispatchEvent(changeEvent);
        }
      });
    });
  };

  // Parse address into components
  let addressLine1 = '';
  let city = '';
  let state = '';
  let zipCode = '';
  if (profile.address) {
    const address = profile.address.trim().replace(/\s+/g, ' ');
    const parts = address.split(',').map(part => part.trim());
    const lastPart = parts[parts.length - 1] || '';
    const secondLastPart = parts[parts.length - 2] || '';
    const stateZipMatch = lastPart.match(/^([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$/i);
    if (stateZipMatch) {
      state = stateZipMatch[1];
      zipCode = stateZipMatch[2];
      city = secondLastPart;
      addressLine1 = parts.slice(0, parts.length - 2).join(', ');
    } else {
      if (parts.length >= 2) {
        city = secondLastPart;
        addressLine1 = parts.slice(0, parts.length - 2).join(', ');
      } else {
        addressLine1 = address;
      }
    }
  }

  // Handle resume file upload first
  if (resumeBlob && resumeFilename) {
    const fileInputs = document.querySelectorAll('input[type="file"][name*="resume"], input[type="file"][id*="resume"], input[type="file"][name*="file"], input[type="file"][id*="file"]');
    if (fileInputs.length > 0) {
      const file = new File([resumeBlob], resumeFilename, { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInputs.forEach(input => {
        input.files = dataTransfer.files;
        const changeEvent = new Event('change', { bubbles: true });
        input.dispatchEvent(changeEvent);
      });
    }
  }

  // Split fullName into firstName and lastName
  let firstName = '';
  let lastName = '';
  if (profile.fullName) {
    const nameParts = profile.fullName.trim().split(' ');
    firstName = nameParts[0] || '';
    lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : '';
  }

  // Fill text fields after a short delay to avoid form reset
  setTimeout(() => {
    Object.keys(fieldMappings).forEach(field => {
      if (field === 'firstName') {
        setFieldValue(field, firstName);
      } else if (field === 'lastName') {
        setFieldValue(field, lastName);
      } else if (field === 'fullName') {
        setFieldValue(field, profile.fullName || '');
      } else if (field === 'addressLine1') {
        setFieldValue(field, addressLine1);
      } else if (field === 'city') {
        setFieldValue(field, city);
      } else if (field === 'state') {
        setFieldValue(field, state);
      } else if (field === 'zipCode') {
        setFieldValue(field, zipCode);
      } else if (field === 'address') {
        setFieldValue(field, profile.address || '');
      } else {
        setFieldValue(field, profile[field]);
      }
    });

    // Handle skills separately
    if (profile.skills && Array.isArray(profile.skills)) {
      const skillFields = document.querySelectorAll('input[name*="skill"], textarea[name*="skill"]');
      profile.skills.forEach((skill, index) => {
        if (skillFields[index]) {
          skillFields[index].value = skill;
          const inputEvent = new Event('input', { bubbles: true });
          skillFields[index].dispatchEvent(inputEvent);
        }
      });
    }

    // Verify fields are still filled after a short period
    setTimeout(() => {
      let fieldsEmpty = false;
      Object.keys(fieldMappings).forEach(field => {
        const possibleNames = fieldMappings[field] || [];
        possibleNames.forEach(name => {
          const inputs = document.querySelectorAll(`input[name="${name}"], input[id="${name}"], textarea[name="${name}"], textarea[id="${name}"]`);
          inputs.forEach(input => {
            if ((input.type === 'text' || input.type === 'email' || input.type === 'tel' || input.tagName.toLowerCase() === 'textarea' || input.getAttribute('role') === 'combobox') && !input.value) {
              fieldsEmpty = true;
            }
          });
        });
      });
      if (fieldsEmpty) {
        // Reapply autofill if fields are cleared
        Object.keys(fieldMappings).forEach(field => {
          if (field === 'firstName') {
            setFieldValue(field, firstName);
          } else if (field === 'lastName') {
            setFieldValue(field, lastName);
          } else if (field === 'fullName') {
            setFieldValue(field, profile.fullName || '');
          } else if (field === 'addressLine1') {
            setFieldValue(field, addressLine1);
          } else if (field === 'city') {
            setFieldValue(field, city);
          } else if (field === 'state') {
            setFieldValue(field, state);
          } else if (field === 'zipCode') {
            setFieldValue(field, zipCode);
          } else if (field === 'address') {
            setFieldValue(field, profile.address || '');
          } else {
            setFieldValue(field, profile[field]);
          }
        });
        if (profile.skills && Array.isArray(profile.skills)) {
          const skillFields = document.querySelectorAll('input[name*="skill"], textarea[name*="skill"]');
          profile.skills.forEach((skill, index) => {
            if (skillFields[index]) {
              skillFields[index].value = skill;
              const inputEvent = new Event('input', { bubbles: true });
              skillFields[index].dispatchEvent(inputEvent);
            }
          });
        }
      }
    }, 1000); // Check after 1 second
  }, 500); // Initial fill after 500ms
}
