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
    print("Starting BSE scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Ek real browser jaisa user-agent set karte hain taaki BSE block na kare
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print("Navigating to BSE India Results page...")
            page.goto("https://www.bseindia.com/corporates/Comp_Results.aspx", timeout=60000)
            
            # Table load hone ka wait karte hain
            print("Waiting for table to load...")
            page.wait_for_selector("table", timeout=15000)
            time.sleep(5)  # Extra buffer for dynamic rows
            
            # Saari rows nikalte hain
            rows = page.locator("table tr").all()
            print(f"Total rows found: {len(rows)}")
            
            filings_found = 0
            message_text = "📢 *BSE Live Filings Update*\n\n"
            
            # Top rows ko grab karte hain
            for i, row in enumerate(rows[1:8], start=1):
                row_text = row.inner_text().strip()
                if row_text and len(row_text) > 10:  
                    clean_text = row_text.replace('\n', ' - ')
                    message_text += f"{i}. {clean_text}\n\n"
                    filings_found += 1
            
            if filings_found > 0:
                send_telegram_message(message_text)
                print(f"Sent {filings_found} filings to Telegram.")
            else:
                send_telegram_message("🤖 BSE Bot chal gaya hai, par table rows empty hain ya structure alag hai.")
                print("Table found but no valid rows extracted.")
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error during scraping: {error_msg}")
            send_telegram_message(f"⚠️ *BSE Bot Error*\n\nError aaya hai: {error_msg}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_bse()
