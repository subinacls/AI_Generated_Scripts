import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def check_protocol(target):
    """
    Check if the target supports HTTPS, fallback to HTTP if not.
    """
    try:
        response = requests.head(f"https://{target}", timeout=5)
        if response.status_code:
            return "https"
    except requests.ConnectionError:
        return "http"

def is_valid_url(base_url, url):
    """
    Checks if a given URL belongs to the same domain as the base URL and is not an external link.
    """
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"] and parsed_base.netloc == parsed_url.netloc

def get_directory_path(url):
    """
    Extracts the directory path from a URL, ignoring any file name or query parameters.
    """
    parsed_url = urlparse(url)
    if "." in parsed_url.path.split("/")[-1]:
        return "/".join(parsed_url.path.split("/")[:-1])
    return parsed_url.path

def test_directory_listing(url):
    """
    Checks if directory listing is enabled for a given URL and prints the result.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and ("<title>Index of" in response.text or "Parent Directory" in response.text):
            print(f"Directory listing found: {url}")
            return True
    except requests.RequestException as e:
        print(f"Failed to access {url}: {e}")
    return False

def crawl_and_check_directory_listing(target, base_url, url, max_depth, current_depth=0, urls_found=None, checked_directories=None):
    if urls_found is None:
        urls_found = set()
    if checked_directories is None:
        checked_directories = set()
    if current_depth > max_depth:
        return
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            if not is_valid_url(base_url, href) or href in urls_found:
                continue
            urls_found.add(href)
            directory_path = urljoin(base_url, get_directory_path(href))
            if directory_path not in checked_directories:
                checked_directories.add(directory_path)
                if test_directory_listing(directory_path):
                    print(f"Directory listing enabled at: {directory_path}")
            # Recursive call to scan the found URL
            crawl_and_check_directory_listing(target, base_url, href, max_depth, current_depth+1, urls_found, checked_directories)
    except requests.RequestException as e:
        print(f"Error crawling {url}: {e}")

# Example usage
if __name__ == "__main__":
    target = "TARGETHERE"  # Change to your target (IP:PORT, DNS:PORT)
    protocol = check_protocol(target)
    base_url = f"{protocol}://{target}"
    max_depth = 3  # Adjust as necessary
    print(f"Starting crawl on {base_url}...")
    crawl_and_check_directory_listing(target, base_url, base_url, max_depth)
    print("Crawl completed.")
