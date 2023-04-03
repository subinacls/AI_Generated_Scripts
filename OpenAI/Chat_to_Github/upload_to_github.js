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

function fetchGeneratedPythonCode() {
  // Implement this function to fetch the generated Python code from the chat.
}

async function getAccessToken() {
  // Implement this function to fetch the user's GitHub access token.
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

