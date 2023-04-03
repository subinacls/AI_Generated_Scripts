document.getElementById("uploadBtn").addEventListener("click", async () => {
  const repoName = document.getElementById("repoName").value;
  if (!repoName) {
    alert("Please enter a repo name.");
    return;
  }

  chrome.runtime.sendMessage({ action: "uploadCode", repoName });
  window.close();
});
