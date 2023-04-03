const API_BASE = "https://api.github.com";

chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
  if (request.action === "uploadCode") {
    const { repoName } = request;

    const code = fetchGeneratedPythonCode(); // Implement this function to fetch the generated Python code from the chat.

    const accessToken = await getAccessToken(); // Implement this function to fetch the user's GitHub access token.
    if (!accessToken) {
      alert("Access token not found. Please authenticate with GitHub.");
      return;
    }

    try {
      const repo = await createPrivateRepo(accessToken, repoName);
      await uploadPythonCode(accessToken, repo, code);
      alert("Python code successfully uploaded!");
    } catch (error) {
      console.error(error);
      alert("Error uploading Python code.");
    }
  }
});

function fetchGeneratedPythonCode(callback) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.executeScript(
      tabs[0].id,
      { code: '(' + extractPythonCode.toString() + ')();' },
      (results) => {
        callback(results[0]);
      }
    );
  });
}

function extractPythonCode() {
  const messages = document.querySelectorAll('.message');
  const pythonCodeRegex = /^```python([\s\S]*?)```$/;
  let pythonCode = '';

  for (const message of messages) {
    const content = message.textContent;
    const match = content.match(pythonCodeRegex);

    if (match) {
      pythonCode += match[1] + '\n';
    }
  }

  return pythonCode.trim();
}

async function getAccessToken() {
  const clientId = "<YOUR_CLIENT_ID>";
  const clientSecret = "<YOUR_CLIENT_SECRET>";
  const redirectUri = `https://${chrome.runtime.id}.chromiumapp.org/callback`;

  return new Promise(async (resolve, reject) => {
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=repo&redirect_uri=${redirectUri}`;

    chrome.identity.launchWebAuthFlow({ url: authUrl, interactive: true }, async (redirectUrl) => {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        reject("Error during authentication.");
        return;
      }

      const urlParams = new URLSearchParams(redirectUrl.split("?")[1]);
      const code = urlParams.get("code");

      if (!code) {
        reject("Error getting authorization code.");
        return;
      }

      const response = await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret,
          code: code,
          redirect_uri: redirectUri,
        }),
      });

      if (!response.ok) {
        reject("Error getting access token.");
        return;
      }

      const data = await response.json();
      const accessToken = data.access_token;

      if (!accessToken) {
        reject("Error getting access token.");
        return;
      }

      resolve(accessToken);
    });
  });
}

async function createPrivateRepo(accessToken, repoName) {
  const response = await fetch(`${API_BASE}/user/repos`, {
    method: "POST",
    headers: {
      Authorization: `token ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: repoName,
      private: true,
    }),
  });
