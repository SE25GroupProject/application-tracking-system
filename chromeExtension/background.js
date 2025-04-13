chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'startGoogleAuth') {
      // Start Google OAuth by opening the auth URL
      chrome.identity.launchWebAuthFlow({
        url: 'http://127.0.0.1:5000/users/signupGoogle',
        interactive: true
      }, (redirectUrl) => {
        if (chrome.runtime.lastError || !redirectUrl) {
          sendResponse({ error: chrome.runtime.lastError?.message || 'No redirect URL' });
          return;
        }
  
        // Parse token, expiry, and userId from redirect URL
        const url = new URL(redirectUrl);
        const token = url.searchParams.get('token');
        const expiry = url.searchParams.get('expiry');
        const userId = url.searchParams.get('userId');
  
        if (token && userId) {
          // Fetch user profile to mimic /users/login response
          fetch('http://127.0.0.1:5000/users/profile', { // Adjust if you have a profile endpoint
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
            .then((response) => response.json())
            .then((data) => {
              chrome.storage.local.set({ token, profile: data.profile || { fullName: userId } }, () => {
                sendResponse({ success: true });
              });
            })
            .catch((error) => {
              sendResponse({ error: error.message });
            });
        } else {
          sendResponse({ error: 'Missing token or userId' });
        }
      });
      return true; // Keep sendResponse async
    }
  });