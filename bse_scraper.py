import os
import cloudscraper
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def scrape_bse():
    print("Starting BSE scraper with Cloudscraper...")
    
    # Cloudscraper bypasses Cloudflare/anti-bot protection automatically
    scraper = cloudscraper.create_scraper()
    
    try:
        url = "https://www.bseindia.com/corporates/ann.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bseindia.com/"
        }
        
        print("Fetching BSE Announcements page...")
        response = scraper.get(url, headers=headers, timeout=30)
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Table rows ya list items ko dhundhte hain
            rows = soup.find_all('tr')
            print(f"Total rows found: {len(rows)}")
            
            filings_found = 0
            message_text = "📢 *BSE Live Filings Update*\n\n"
            
            for i, row in enumerate(rows[1:8], start=1):
                row_text = row.get_text(strip=True)
                if row_text and len(row_text) > 20:
                    clean_text = row_text.replace('\n', ' - ')
                    # Message chota rakhne ke liye length limit karte hain
                    message_text += f"{i}. {clean_text[:200]}...\n\n"
                    filings_found += 1
            
            if filings_found > 0:
                send_telegram_message(message_text)
                print(f"Sent {filings_found} filings to Telegram.")
            else:
                send_telegram_message("🤖 BSE Bot connected successfully, but no rows matched in HTML structure.")
                print("Page fetched but no valid rows found.")
        else:
            send_telegram_message(f"⚠️ BSE blocked request. Status: {response.status_code}")
            print(f"Blocked with status: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error during scraping: {error_msg}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError aaya hai: {error_msg}")

if __name__ == "__main__":
    scrape_bse()
