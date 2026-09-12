import os
import requests

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

def fetch_bse_announcements():
    session = requests.Session()
    
    # Optional: Agar tere paas koi proxy hai toh yahan set kar (e.g., "http://username:password@proxyserver:port")
    # Free GitHub Actions par bina proxy ke BSE block marega hi marega kyunki IP data center ka hai.
    proxy_url = os.environ.get("PROXY_URL") # GitHub Secrets me proxy dal sakta hai agar ho toh
    if proxy_url:
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        print("Using custom proxy for requests...")

    base_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        print("Establishing secure session with BSE...")
        session.get("https://www.bseindia.com/corporates/ann.html", headers=base_headers, timeout=15)
        
        api_headers = {
            'authority': 'api.bseindia.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.bseindia.com',
            'referer': 'https://www.bseindia.com/corporates/ann.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/Ann_new/w?strType=C&pageno=1&strScrip=&strCat=-1&strPrevDate=&strToDate=&strFromDate=&strSearch=P"
        
        print("Fetching corporate announcements from BSE API...")
        response = session.get(api_url, headers=api_headers, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                table = []
                if isinstance(data, dict):
                    table = data.get('Table', [])
                elif isinstance(data, list):
                    table = data
                    
                if table:
                    print(f"Successfully fetched {len(table)} announcements!")
                    message_text = "📢 *BSE Live Filings Update*\n\n"
                    
                    for idx, item in enumerate(table[:5], 1):
                        company = item.get('SLONGNAME') or item.get('CompanyName') or item.get('scripname') or 'Company'
                        subject = item.get('NEWSSUB') or item.get('HEADLINE') or item.get('NewsHeadline') or 'Headline'
                        date_time = item.get('DT_TM') or item.get('NewsDt') or ''
                        
                        message_text += f"{idx}. **{company}**\n📝 {subject}\n🕒 `{date_time}`\n\n"
                    
                    send_telegram_message(message_text)
                else:
                    send_telegram_message("🤖 API connected successfully, but announcements table was empty.")
            except Exception as json_err:
                snippet = response.text[:150].replace('\n', ' ')
                print(f"Failed to parse JSON. Snippet: {snippet}")
                send_telegram_message(f"⚠️ BSE returned HTML instead of JSON (WAF Blocked). Snippet: `{snippet}`")
        else:
            send_send_msg = f"⚠️ BSE API blocked request with status: {response.status_code}"
            send_telegram_message(send_send_msg)
            
    except Exception as e:
        error_msg = str(e)
        print(f"An error occurred: {e}")
        send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError: {error_msg}")

if __name__ == "__main__":
    fetch_bse_announcements()
