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
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def scrape_bse():
    print("Starting BSE scraper for all filings...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Navigating to BSE India Results page...")
            page.goto("https://www.bseindia.com/corporates/Comp_Results.aspx", timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # Thoda wait karte hain taaki table load ho jaye
            time.sleep(3)
            
            # Table rows ko select karne ka try karte hain (BSE results table)
            # Yahan hum saari rows utha rahe hain bina kisi filter ke
            rows = page.locator("table tr").all()
            
            filings_found = 0
            message_text = "📢 *BSE All Filings Update*\n\n"
            
            # Pehle kuch rows ko extract karte hain (jaise top 5-10 filings taaki spam na ho)
            for i, row in enumerate(rows[1:10], start=1):  
                row_text = row.inner_text().strip()
                if row_text:
                    clean_text = row_text.replace('\n', ' - ')
                    message_text += f"{i}. {clean_text}\n\n"
                    filings_found += 1
            
            if filings_found > 0:
                send_telegram_message(message_text)
                print(f"Sent {filings_found} filings to Telegram.")
            else:
                send_telegram_message("🤖 BSE Bot run ho gaya hai, par abhi table mein koi row nahi mili.")
                print("No rows found in table.")
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error during scraping: {error_msg}")
            send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError aaya hai: {error_msg}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_bse()
