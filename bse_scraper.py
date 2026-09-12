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
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=-1&strPrevDate=&strScrip=&strSearch=C&strToDate=&strFromDate=&strType=C"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bseindia.com/",
            "Origin": "https://www.bseindia.com"
        }
        
        response = scraper.get(api_url, headers=headers, timeout=30)
        print(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            announcements = []
            if isinstance(data, list):
                announcements = data
            elif isinstance(data, dict):
                # Har possible key ko check karte hain jisme list ho sakti hai
                for key in ["Table", "table", "Table1", "TableData", "Announcements", "Annc"]:
                    if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                        announcements = data[key]
                        break
                
                # Agar phir bhi na mile, toh dictionary ki pehli list wali key utha lo
                if not announcements:
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0:
                            announcements = v
                            break
            
            print(f"Total announcements found: {len(announcements)}")
            
            if announcements:
                message_text = "📢 *BSE Live Filings Update*\n\n"
                
                for i, item in enumerate(announcements[:5], start=1):
                    company = item.get("SLONGNAME") or item.get("CompanyName") or item.get("SCRIP_CD") or "Company"
                    headline = item.get("HEADLINE") or item.get("NewsHeadline") or item.get("Heading") or "Headline"
                    date_time = item.get("DT_TM") or item.get("NewsDt") or ""
                    
                    message_text += f"{i}. **{company}**\n📝 {headline}\n🕒 `{date_time}`\n\n"
                
                send_telegram_message(message_text)
                print("Sent filings to Telegram successfully!")
            else:
                # Debug ke liye keys bhejenge taaki pata chale JSON mein kya hai
                keys_found = list(data.keys()) if isinstance(data, dict) else "List format"
                send_telegram_message(f"🤖 API connected! Keys found: `{keys_found}`")
                print(f"Keys found: {keys_found}")
        else:
            send_telegram_message(f"⚠️ BSE API blocked request. Status: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error during fetching: {error_msg}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError: {error_msg}")

if __name__ == "__main__":
    scrape_bse()
