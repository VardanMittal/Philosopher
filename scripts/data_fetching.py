import requests
import pandas as pd
import os
from tqdm import tqdm

##################### Config #########################

dir = lambda x: os.path.join(os.path.dirname(__file__), x)
DATA_DIR = "../data/raw_text"
os.makedirs(dir(DATA_DIR), exist_ok=True)
METADATA = dir("metadata.csv")

######################## GUTENBERG #########################

def search_guttenberg(author, book):
    """Search for a book in Project Gutenberg using Gutendex API."""
    url = f"https://gutendex.com/books/?search={author}%20{book}&languages=en"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code} fetching {book}")
        return []
    return response.json().get("results", [])

def download_gutenberg_txt(res, book):
    """Download the first matching Gutenberg book as plain text."""
    if not res:
        return None
    try:
        formats = res[0].get("formats", {})
        txt_url = formats.get("text/plain; charset=utf-8") or formats.get("text/plain; charset=us-ascii")
        if not txt_url:
            return None

        text = requests.get(txt_url, timeout=30).text
        filepath = os.path.join(DATA_DIR, f"{book.replace('/', '_')}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return filepath
    except Exception:
        return None

######################## MAIN LOOP WITH METADATA UPDATE ################

data = pd.read_csv(METADATA)

for idx, row in tqdm(data.iterrows(), total=len(data), desc="📚 Downloading Philosophers"):
    philosopher = row["philosopher"]
    work_title = row["work_title"]
    source = row["source"]

    if row.get("done", False):
        continue

    file_path = None

    try:
        # Try Gutenberg first
        res = search_guttenberg(philosopher, work_title)
        file_path = download_gutenberg_txt(res, work_title)

        if file_path:
            tqdm.write(f"✅ Gutenberg: {work_title}")
        else:
            tqdm.write(f"⚠️ Not found: {work_title}")

    except Exception as e:
        tqdm.write(f"❌ Failed: {work_title} ({e})")

    if file_path:
        data.at[idx, 'done'] = True
        data.at[idx, 'local_path'] = file_path
        data.to_csv(METADATA, index=False)
