import os
import requests
import cloudscraper

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
    print("Fetching BSE Announcements via official API...")
    
    scraper = cloudscraper.create_scraper()
    
    try:
        # BSE ka official JSON API endpoint for live corporate announcements
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=-1&strPrevDate=&strScrip=&strSearch=C&strToDate=&strFromDate=&strType=C"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bseindia.com/"
        }
        
        response = scraper.get(api_url, headers=headers, timeout=30)
        print(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # BSE API list ya dictionary return karta hai
            announcements = data.get("Table", []) if isinstance(data, dict) else data
            
            print(f"Total announcements fetched: {len(announcements)}")
            
            if announcements:
                message_text = "📢 *BSE Live Filings Update*\n\n"
                
                # Top 5-6 filings ko format karke bhejte hain
                for i, item in enumerate(announcements[:6], start=1):
                    company = item.get("SLONGNAME", "Unknown Company")
                    headline = item.get("HEADLINE", "No Headline")
                    date_time = item.get("DT_TM", "")
                    
                    message_text += f"{i}. **{company}**\n📝 {headline}\n🕒 `{date_time}`\n\n"
                
                send_telegram_message(message_text)
                print("Sent filings to Telegram successfully!")
            else:
                send_telegram_message("🤖 BSE API connected, but announcements list was empty.")
                print("No announcements found in JSON.")
        else:
            send_telegram_message(f"⚠️ BSE API blocked request. Status: {response.status_code}")
            print(f"Blocked with status: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error during fetching: {error_msg}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError aaya hai: {error_msg}")

if __name__ == "__main__":
    scrape_bse()
