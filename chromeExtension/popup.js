document.addEventListener('DOMContentLoaded', () => {
    const authSection = document.getElementById('auth-section');
    const contentSection = document.getElementById('content-section');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const fullNameInput = document.getElementById('fullName');
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');
    const googleBtn = document.getElementById('google-btn');
    const fetchDataBtn = document.getElementById('fetch-data-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userNameSpan = document.getElementById('user-name');
    const apiResult = document.getElementById('api-result');
  
    const BASE_URL = 'http://127.0.0.1:5000';
  
    // Check if user is logged in
    chrome.storage.local.get(['token', 'profile'], (result) => {
      if (result.token && result.profile) {
        authSection.style.display = 'none';
        contentSection.style.display = 'block';
        userNameSpan.textContent = result.profile.fullName || 'User';
      }
    });
  
    // Login
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
        const data = await response.json();
  
        if (response.ok) {
          chrome.storage.local.set({ token: data.token, profile: data.profile }, () => {
            authSection.style.display = 'none';
            contentSection.style.display = 'block';
            userNameSpan.textContent = data.profile.fullName || 'User';
            apiResult.textContent = 'Login successful';
          });
        } else {
          apiResult.textContent = `Error: ${data.error}`;
        }
      } catch (error) {
        apiResult.textContent = `Error: ${error.message}`;
      }
    });
  
    // Signup
    signupBtn.addEventListener('click', async () => {
      const username = usernameInput.value;
      const password = passwordInput.value;
      const fullName = fullNameInput.value;
      if (!username || !password || !fullName) {
        apiResult.textContent = 'Please enter username, password, and full name';
        return;
      }
  
      try {
        const response = await fetch(`${BASE_URL}/users/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, fullName })
        });
        const data = await response.json();
  
        if (response.ok) {
          apiResult.textContent = 'Signup successful! Please log in.';
          fullNameInput.value = ''; // Clear fullName field
        } else {
          apiResult.textContent = `Error: ${data.error}`;
        }
      } catch (error) {
        apiResult.textContent = `Error: ${error.message}`;
      }
    });
  
    // Google OAuth (workaround for extension popup)
    googleBtn.addEventListener('click', () => {
      // Open Google auth in a new tab, as redirects are tricky in popups
      chrome.runtime.sendMessage({ action: 'startGoogleAuth' }, (response) => {
        if (response && response.error) {
          apiResult.textContent = `Google Auth Error: ${response.error}`;
        }
      });
    });
  
    // Fetch protected data (example)
    fetchDataBtn.addEventListener('click', async () => {
      chrome.storage.local.get(['token'], async (result) => {
        if (!result.token) {
          apiResult.textContent = 'Not logged in';
          return;
        }
  
        try {
          const response = await fetch(`${BASE_URL}/protected-endpoint`, { // Replace with your actual endpoint
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${result.token}`,
              'Content-Type': 'application/json'
            }
          });
          const data = await response.json();
  
          if (response.ok) {
            apiResult.textContent = JSON.stringify(data, null, 2);
          } else {
            apiResult.textContent = `Error: ${data.error}`;
          }
        } catch (error) {
          apiResult.textContent = `Error: ${error.message}`;
        }
      });
    });
  
    // Logout
    logoutBtn.addEventListener('click', async () => {
      chrome.storage.local.get(['token'], async (result) => {
        if (!result.token) {
          apiResult.textContent = 'Not logged in';
          return;
        }
  
        try {
          const response = await fetch(`${BASE_URL}/users/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${result.token}`,
              'Content-Type': 'application/json'
            }
          });
          const data = await response.json();
  
          if (response.ok) {
            chrome.storage.local.remove(['token', 'profile'], () => {
              authSection.style.display = 'block';
              contentSection.style.display = 'none';
              apiResult.textContent = 'Logged out successfully';
              usernameInput.value = '';
              passwordInput.value = '';
            });
          } else {
            apiResult.textContent = `Error: ${data.error}`;
          }
        } catch (error) {
          apiResult.textContent = `Error: ${error.message}`;
        }
      });
    });
  });