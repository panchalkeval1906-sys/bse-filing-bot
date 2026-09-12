import os
import time
import requests
from playwright.sync_api import sync_playwright

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
        requests.post(url, json=payload, timeout=10)
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def scrape_bse():
    print("Starting BSE scraper with Network Interception...")
    captured_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Listen to network responses to catch the BSE API JSON directly as it loads
        def handle_response(response):
            if "Ann_new" in response.url or "AnnSubCategoryGetData" in response.url:
                try:
                    json_data = response.json()
                    if json_data:
                        captured_data.append(json_data)
                except:
                    pass

        page.on("response", handle_response)

        try:
            print("Navigating to BSE Announcements page...")
            page.goto("https://www.bseindia.com/corporates/ann.aspx", timeout=60000)
            
            # Give browser enough time to execute JS and fetch the API data
            print("Waiting for data to load...")
            time.sleep(8)
            
        except Exception as e:
            print(f"Navigation error: {e}")
        finally:
            browser.close()

    # Process the captured API data
    if captured_data:
        data = captured_data[0]
        announcements = []
        if isinstance(data, list):
            announcements = data
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    announcements = v
                    break
        
        if announcements:
            message_text = "📢 *BSE Live Filings Update*\n\n"
            for i, item in enumerate(announcements[:5], start=1):
                company = item.get("SLONGNAME") or item.get("CompanyName") or item.get("scripname") or "Company"
                headline = item.get("HEADLINE") or item.get("NewsHeadline") or item.get("heading") or "Headline"
                date_time = item.get("DT_TM") or item.get("NewsDt") or ""
                
                message_text += f"{i}. **{company}**\n📝 {headline}\n🕒 `{date_time}`\n\n"
            
            send_telegram_message(message_text)
            print("Sent announcements to Telegram!")
        else:
            send_telegram_message("🤖 Browser caught API response, but the announcements list was empty.")
    else:
        send_telegram_message("⚠️ Playwright could not intercept the API response. Security challenge active.")

if __name__ == "__main__":
    scrape_bse()
