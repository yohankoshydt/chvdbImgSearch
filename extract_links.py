import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
def extract_full_links(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    full_links = []
    seen = set()
    for tag in soup.find_all('a', href=True):
        abs_url = urljoin(url, tag['href'])
        if abs_url.startswith("http") and abs_url not in seen:
            full_links.append(abs_url)
            seen.add(abs_url)
    return full_links


# --- Usage Example ---
if __name__ == "__main__":
    page_url = input("Enter the webpage URL: ").strip()
    out_csv = "extracted_links.csv"

    try:
        links = extract_full_links(page_url)
        df = pd.DataFrame({'url': links})
        df.to_csv(out_csv, index=False)
        print(f"Saved {len(df)} links to {out_csv}")
    except Exception as e:
        print(f"Error: {e}")
