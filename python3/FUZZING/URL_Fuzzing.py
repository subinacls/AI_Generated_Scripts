import asyncio
import aiohttp
from itertools import product, zip_longest
from collections import defaultdict

class AsyncWebURLFuzzer:
    def __init__(self, base_url, directories=None, filenames=None, extensions=None, mode='cluster_bomb', dry_run=False):
        self.base_url = base_url.rstrip('/')
        self.directories = directories if directories is not None else ['']
        self.filenames = filenames if filenames is not None else ['index']
        self.extensions = extensions if extensions is not None else ['.html', '.php']
        self.mode = mode
        self.dry_run = dry_run
        self.status_code_categories = defaultdict(list)

    async def content_sorter(self):
        """
        Asynchronously attempts to locate the default content of a web server by iterating through
        user-specified (or default) directories, filenames, and extensions, using the
        specified mode ('cluster_bomb' or 'pitchfork'). Utilizes aiohttp for async HTTP requests if not in dry_run mode.
        """
        urls = self._generate_urls()
        
        if self.dry_run:
            # Print and save the URLs without making HTTP requests
            self._save_urls('dry_run_urls.txt', urls)
        else:
            # Perform the HTTP requests asynchronously
            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.ensure_future(self._try_combination(session, url)) for url in urls]
                await asyncio.gather(*tasks)
                
            self._report_status_codes()

    def _report_status_codes(self):
        """
        Reports and saves URLs categorized by their HTTP status code.
        """
        for category, urls in self.status_code_categories.items():
            filename = f'{category}_urls.txt'
            print(f"\nHTTP {category} URLs:")
            for url in urls:
                print(url)
            self._save_urls(filename, urls)

    def _generate_urls(self):
        """
        Generates all possible URLs based on the specified mode ('cluster_bomb' or 'pitchfork').
        """
        urls = []
        if self.mode == 'cluster_bomb':
            for combination in product(self.directories, self.filenames, self.extensions):
                urls.append(self._construct_url(combination))
        elif self.mode == 'pitchfork':
            for items in zip_longest(self.directories, self.filenames, self.extensions):
                if None not in items:
                    urls.append(self._construct_url(items))
        return urls

    def _construct_url(self, combination):
        """
        Constructs a URL from a combination of directory, filename, and extension.
        """
        return f"{self.base_url}/{combination[0]}/{combination[1]}{combination[2]}".rstrip('/')

    async def _try_combination(self, session, url):
        """
        Asynchronously tries a URL and categorizes it based on its HTTP status code.
        """
        try:
            async with session.get(url) as response:
                category = f'{response.status // 100}xx'
                self.status_code_categories[category].append(url)
        except aiohttp.ClientError as e:
            print(f"Request failed: {e}")

    def _save_urls(self, filename, urls):
        """
        Saves URLs to a file.
        """
        with open(filename, 'w') as file:
            for url in urls:
                file.write(url + '\n')

# Example usage
async def main():
    url = "http://example.com"  # Replace with the actual URL
    mode = "cluster_bomb"  # Choose between 'cluster_bomb' and 'pitchfork'
    dry_run = False  # Set to True for dry run mode
    locator = AsyncWebURLFuzzer(url, mode=mode, dry_run=dry_run)
    await locator.content_sorter()

if __name__ == "__main__":
    asyncio.run(main())
