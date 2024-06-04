import sys
import requests
from bs4 import BeautifulSoup

class GoogleSearch:
    def __init__(self, query):
        self.query = query

    def search_and_return(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        search_results = []
        for start in range(0, 100, 10):  # Adjust the range and step to get more results
            url = f"https://www.google.com/search?q={self.query}&start={start}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            for g in soup.find_all('div', class_='g'):
                link = g.find('a')
                if link and 'href' in link.attrs:
                    title = g.find('h3').text if g.find('h3') else 'No title'
                    description = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else 'No description'
                    search_results.append({
                        'title': title,
                        'link': link['href'],
                        'description': description
                    })
        return search_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python sys.argv[0] <query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    google_search = GoogleSearch(query)
    results = google_search.search_and_return()
    for idx, result in enumerate(results, start=1):
        print(f"{idx}. {result['title']}\n   Link: {result['link']}\n   Description: {result['description']}\n")
if __name__ == "__main__":
    main()
