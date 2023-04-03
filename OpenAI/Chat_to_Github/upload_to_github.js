const API_BASE = "https://api.github.com";

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === "uploadCode") {
    const { repoName } = message;
    const code = fetchGeneratedPythonCode();
    const accessToken = await getAccessToken();

    if (!accessToken) {
      alert("Access token not found. Please authenticate with GitHub.");
      return;
    }

    try {
      const repo = await getExistingRepo(accessToken, repoName);
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
async function getExistingRepo(accessToken, repoName) {
  const response = await fetch(`https://api.github.com/repos/${repoName}`, {
    headers: {
      Authorization: `token ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Error fetching repo: ${response.statusText}`);
  }

  return await response.json();
}

async function uploadPythonCode(accessToken, repo, code) {
  const { git: { trees, commits } } = repo.default_branch;
  const treeResponse = await fetch(`https://api.github.com/repos/${repo.full_name}/git/trees/${trees.sha}`, {
    headers: {
      Authorization: `token ${accessToken}`,
    },
  });
  const baseTree = await treeResponse.json();

  const createTreeResponse = await fetch(`https://api.github.com/repos/${repo.full_name}/git/trees`, {
    method: "POST",
    headers: {
      Authorization: `token ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      base_tree: baseTree.sha,
      tree: [
        {
          path: "generated_code.py",
          mode: "100644",
          type: "blob",
          content: code,
        },
      ],
    }),
  });
  const newTree = await createTreeResponse.json();

  const createCommitResponse = await fetch(`https://api.github.com/repos/${repo.full_name}/git/commits`, {
    method: "POST",
    headers: {
      Authorization: `token ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: "Upload generated Python code",
      tree: newTree.sha,
      parents: [commits.sha],
    }),
  });
  const newCommit = await createCommitResponse.json();

  await fetch(`https://api.github.com/repos/${repo.full_name}/git/refs/heads/${repo.default_branch}`, {
    method: "PATCH",
    headers: {
      Authorization: `token ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sha: newCommit.sha,
    }),
  });
}
