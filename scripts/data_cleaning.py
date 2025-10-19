import re
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "../data/raw_text/")
CLEAN_DIR = os.path.join(BASE_DIR, "../data/cleaned/")
os.makedirs(CLEAN_DIR, exist_ok=True)

domain_keywords = {
    "Ethics": ["virtue", "good", "moral", "duty", "right", "wrong", "happiness"],
    "Epistemology": ["knowledge", "truth", "belief", "certainty", "understanding"],
    "Metaphysics": ["existence", "being", "reality", "substance", "cause", "universe"]
}

def clean_text(text):
    text = re.sub(r'(?s).*START OF THE PROJECT GUTENBERG.*?\n', '', text)
    text = re.sub(r'End of the Project Gutenberg.*', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=800):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def tag_chunk(chunk):
    tags = []
    lower = chunk.lower()
    for domain, keywords in domain_keywords.items():
        if any(word in lower for word in keywords):
            tags.append(domain)
    return tags or ["General"]

# Clean and save
for fname in os.listdir(RAW_DIR):
    if fname.endswith(".txt"):
        path = os.path.join(RAW_DIR, fname)
        if not os.path.exists(path):
            print(f"⚠️ File not found: {path}")
            continue
        print(fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        cleaned = clean_text(text)
        with open(os.path.join(CLEAN_DIR, fname), "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"✅ Cleaned {fname}")

# Chunking
for fname in os.listdir(CLEAN_DIR):
    if fname.endswith(".txt"):
        path = os.path.join(CLEAN_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        jsonl_path = os.path.join(CLEAN_DIR, fname.replace(".txt", "_chunks.jsonl"))
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                json.dump({"text": chunk}, f)
                f.write("\n")
        print(f"✅ Chunked {fname} into {len(chunks)} parts")

# Tagging chunks
for chunk_file in os.listdir(CLEAN_DIR):
    if chunk_file.endswith("_chunks.jsonl"):
        chunks = []
        with open(os.path.join(CLEAN_DIR, chunk_file), "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                data["domains"] = tag_chunk(data["text"])
                chunks.append(data)
        with open(os.path.join(CLEAN_DIR, chunk_file), "w", encoding="utf-8") as f:
            for c in chunks:
                json.dump(c, f)
                f.write("\n")
        print(f"✅ Tagged domains for {chunk_file}")
