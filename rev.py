import pandas as pd
import bs4
import requests
import os
import re
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}
def sanitize_filename(name):
    # Remove invalid filename characters (Windows)
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def save_img(url, default_filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch page {url}: {e}")
        return

    soup = bs4.BeautifulSoup(response.content, 'html.parser')

    # Find the <td> with class 'infobox-image'
    td = soup.find('td', class_='infobox-image')
    if td is None:
        print(f"No infobox-image found for {url}")
        return
    img = td.find('img', class_='mw-file-element')
    if img is None:
        print(f"No mw-file-element image found for {url}")
        return

    # Try to get the page title (person name) from <h1 id="firstHeading">
    name = None
    h1 = soup.find('h1', id='firstHeading')
    if h1:
        span = h1.find('span', class_='mw-page-title-main')
        if span:
            name = span.text.strip()
        else:
            name = h1.text.strip()
    if not name:
        name = 'No_name_found'
    filename = f"images/{sanitize_filename(name)}.jpg"

    img_src = img['src']
    # Wikipedia images start with //
    if img_src.startswith('//'):
        img_url = 'https:' + img_src
    elif img_src.startswith('http'):
        img_url = img_src
    else:
        print(f"Unknown image src format: {img_src}")
        return

    try:
        img_resp = requests.get(img_url, headers=headers, stream=True, timeout=10)
        img_resp.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in img_resp.iter_content(1024):
                f.write(chunk)
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Failed to download or save image {img_url}: {e}")

# --- Main code ---

df = pd.read_csv(r"extracted_links.csv")

os.makedirs("images", exist_ok=True)
for i, (_, row) in enumerate(df.iterrows()):
    if i >= 1500:
        break
    url = row['URL']
    try:
        save_img(url, rf"images\img_{i}.jpg")
    except Exception as e:
        print(f"Error occurred while saving image {i}: {e}")
