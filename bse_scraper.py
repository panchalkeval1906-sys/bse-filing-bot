import requests

def fetch_bse_announcements():
    # Session use karna zaroori hai taaki cookies maintain rahein aur WAF block na kare
    session = requests.Session()
    
    # Step 1: Main page ko hit karke cookies/session acquire karo
    base_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        print("Establishing secure session with BSE...")
        session.get("https://www.bseindia.com/corporates/ann.html", headers=base_headers, timeout=15)
        
        # Step 2: API headers jisme proper Origin aur Referer ho
        api_headers = {
            'authority': 'api.bseindia.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.bseindia.com',
            'referer': 'https://www.bseindia.com/corporates/ann.html',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/Ann_new/w?strType=C&pageno=1&strScrip=&strCat=-1&strPrevDate=&strToDate=&strFromDate=&strSearch=P"
        
        print("Fetching corporate announcements from BSE API...")
        response = session.get(api_url, headers=api_headers, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                table = data.get('Table', [])
                if table:
                    print(f"\nSuccessfully fetched {len(table)} announcements!\n")
                    for idx, item in enumerate(table[:5], 1):
                        company = item.get('SLONGNAME', 'N/A')
                        subject = item.get('NEWSSUB', 'N/A')
                        date_time = item.get('DT_TM', 'N/A')
                        print(f"{idx}. [{date_time}] {company}")
                        print(f"   Subject: {subject}\n")
                else:
                    print("API responded successfully, but 'Table' list is empty.")
            except json.JSONDecodeError:
                print("Response is not valid JSON (WAF might have blocked with HTML).")
                print(response.text[:300])
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text[:300])
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_bse_announcements()
