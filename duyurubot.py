import requests
from bs4 import BeautifulSoup
import json
import time
import os

# Ortam değişkenlerinden Telegram ayarlarını al
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_announcements():
    url = "https://elk.yildiz.edu.tr/duyurular"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Duyuru başlıklarını al (siteye göre selector değişebilir)
    announcements = []
    for item in soup.select("div.mb-4.d-flex.announcement"):
        # title and date selectors may need adjustment based on actual HTML structure
        titleitem = item.select_one("div.date-link.ps-4")
        dateitem = item.select_one(".date")
        title = titleitem.get_text(strip=True) if titleitem else ""
        date = dateitem.get_text(strip=True) if dateitem else ""
        # Try to get the link from an <a> tag inside the announcement
        linkitem = item.select_one("a")
        link = linkitem["href"] if linkitem and linkitem.has_attr("href") else None
        link = "https://elk.yildiz.edu.tr" + link
        announcements.append({"title": title, "link": link, "date": date})
    return announcements

def load_seen():
    if os.path.exists("seen.json"):
        with open("seen.json", "r") as f:
            return json.load(f)
    return []

def save_seen(data):
    with open("seen.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    seen = load_seen()
    current = get_announcements()

    new = [a for a in current if a not in seen]

    if new:
        for ann in new:
            send_telegram(f"Yeni Duyuru: {ann['title']}\nLink: {ann['link']}\n Tarih: {ann['date']}")
        save_seen(current)

if __name__ == "__main__":
    main()
