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
    print("Initializing BSE scraper with session cookies...")
    
    # Create a cloudscraper session to maintain cookies & bypass WAF
    scraper = cloudscraper.create_scraper()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bseindia.com/corporates/ann.aspx",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        # Step 1: Hit the main page first to establish valid cookies and bypass Cloudflare/WAF
        print("Visiting main page to establish session...")
        main_page = scraper.get("https://www.bseindia.com/corporates/ann.aspx", timeout=30)
        print(f"Main page status: {main_page.status_code}")
        
        # Step 2: Now call the official JSON API using the exact same session object
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/Ann_new/w?strType=C&pageno=1&strScrip=&strCat=-1&strPrevDate=&strToDate=&strFromDate=&strSearch=P"
        
        print("Fetching data from BSE API...")
        response = scraper.get(api_url, headers=headers, timeout=30)
        print(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception as json_err:
                snippet = response.text[:150].replace('\n', ' ')
                print(f"Failed to parse JSON. Response starts with: {snippet}")
                send_telegram_message(f"⚠️ BSE returned HTML instead of JSON. Snippet: `{snippet}`")
                return
            
            announcements = []
            if isinstance(data, list):
                announcements = data
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list) and len(v) > 0:
                        announcements = v
                        break
            
            print(f"Total announcements found: {len(announcements)}")
            
            if announcements:
                message_text = "📢 *BSE Live Filings Update*\n\n"
                
                for i, item in enumerate(announcements[:5], start=1):
                    company = item.get("SLONGNAME") or item.get("CompanyName") or item.get("scripname") or "Company"
                    headline = item.get("HEADLINE") or item.get("NewsHeadline") or item.get("heading") or "Headline"
                    date_time = item.get("DT_TM") or item.get("NewsDt") or ""
                    
                    message_text += f"{i}. **{company}**\n📝 {headline}\n🕒 `{date_time}`\n\n"
                
                send_telegram_message(message_text)
                print("Sent filings to Telegram successfully!")
            else:
                send_telegram_message("🤖 API connected successfully, but announcement list was empty.")
        else:
            send_telegram_message(f"⚠️ BSE API blocked request with status: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error during execution: {error_msg}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError: {error_msg}")

if __name__ == "__main__":
    scrape_bse()
