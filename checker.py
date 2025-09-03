import requests, hashlib, pdfplumber
from bs4 import BeautifulSoup
from datetime import datetime
from models import db, MonitoredFile

def get_pdf_text(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    with open("temp.pdf", "wb") as f:
        f.write(r.content)
    text = ""
    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def hash_content(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def get_dynamic_url(page_url, keyword):
    r = requests.get(page_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        if href.lower().endswith(".pdf") and keyword.lower() in link.text.lower():
            return href
    return None

def check_file(mf: MonitoredFile):
    dynamic_url = get_dynamic_url(mf.url, mf.name)
    if not dynamic_url:
        print(f"⚠️ Could not find PDF for {mf.name}")
        return False

    content = get_pdf_text(dynamic_url)
    new_hash = hash_content(content)

    changed = False
    if mf.last_hash != new_hash:
        changed = True
        mf.last_changed = datetime.utcnow()
        mf.last_hash = new_hash

    mf.last_checked = datetime.utcnow()
    db.session.commit()
    return changed