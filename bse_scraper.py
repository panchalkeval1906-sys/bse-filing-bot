import os
import requests
import feedparser

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
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def scrape_bse():
    print("Fetching BSE Corporate Announcements via RSS Feed...")
    
    # BSE official public RSS feed for corporate announcements (unblocked by WAF)
    rss_url = "https://www.bseindia.com/xml/rss/RssCorporates.xml"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        response = requests.get(rss_url, headers=headers, timeout=30)
        print(f"RSS Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the XML/RSS feed data
            feed = feedparser.parse(response.content)
            entries = feed.entries
            
            print(f"Total RSS items found: {len(entries)}")
            
            if entries:
                message_text = "📢 *BSE Live Filings Update (RSS)*\n\n"
                
                for i, entry in enumerate(entries[:5], start=1):
                    title = entry.get("title", "No Title")
                    link = entry.get("link", "#")
                    published = entry.get("published", "")
                    
                    message_text += f"{i}. 📝 {title}\n🕒 `{published}`\n🔗 [View Filing]({link})\n\n"
                
                send_telegram_message(message_text)
                print("Sent RSS announcements to Telegram successfully!")
            else:
                send_telegram_message("🤖 RSS feed fetched successfully, but entries list was empty.")
        else:
            send_telegram_message(f"⚠️ RSS feed blocked. Status: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error fetching RSS: {error_msg}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError: {error_msg}")

if __name__ == "__main__":
    scrape_bse()
