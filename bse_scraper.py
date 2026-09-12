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
    print("Starting Stealth BSE scraper...")
    captured_data = []

    with sync_playwright() as p:
        # Launch browser with anti-detection flags to bypass security walls
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()

        # Mask automation properties so BSE thinks it's a real human browser
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Listen to network responses to catch the BSE API JSON naturally
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
            # Step 1: Visit BSE Home first to pass any security/cookie challenges cleanly
            print("Visiting BSE Home page...")
            page.goto("https://www.bseindia.com/", timeout=60000)
            time.sleep(5)
            
            # Step 2: Now navigate to the corporate announcements page
            print("Navigating to Announcements page...")
            page.goto("https://www.bseindia.com/corporates/ann.aspx", timeout=60000)
            
            # Give enough time for the page to load and trigger background API requests
            print("Waiting for live data to load...")
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
            print("Sent announcements to Telegram successfully!")
        else:
            send_telegram_message("🤖 Browser caught API response, but announcements list was empty.")
    else:
        send_telegram_message("⚠️ Security challenge active. WAF blocked the stealth run.")

if __name__ == "__main__":
    scrape_bse()
