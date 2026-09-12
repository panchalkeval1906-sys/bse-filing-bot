import os
import cloudscraper

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

sent_ids = set()


def send_telegram_message(message):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {
      'chat_id': TELEGRAM_CHAT_ID,
      'text': message,
      'parse_mode': 'Markdown',
  }
  try:
    scraper = cloudscraper.create_scraper()
    scraper.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f'Error sending Telegram: {e}')


def check_bse_filings():
  api_url = 'https://api.bseindia.com/BSEIndiaAPI/api/AnnSubCategoryGetData?strCat=-1&strPrevDate=&strScrip=&strSearch=P&strToDate=&strType=C'

  headers = {
      'Host': 'api.bseindia.com',
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
          ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
      ),
      'Referer': 'https://www.bseindia.com/',
  }

  try:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(api_url, headers=headers, timeout=15)

    if response.status_code != 200:
      print(f'BSE Blocked or Error: {response.status_code}')
      return

    data = response.json()
    announcements = data.get('Table', [])

    # First run par history cache kar lo taaki purane messages na aayein
    global sent_ids
    if not sent_ids:
      for item in announcements:
        fid = str(item.get('NEWSID') or item.get('ROW_ID'))
        if fid:
          sent_ids.add(fid)
      print('Initialized successfully. Filings cached.')
      return

    for item in announcements:
      fid = str(item.get('NEWSID') or item.get('ROW_ID'))
      if fid and fid not in sent_ids:
        sent_ids.add(fid)
        heading = item.get('HEADLINE', 'No Headline')
        scrip_name = item.get('SLONGNAME', 'Unknown Company')
        dt = item.get('NEWS_DT', '')

        msg = (
            f'🚨 *New BSE Filing Alert!*\n\n*Company:* {scrip_name}\n*Headline:*'
            f' {heading}\n*Time:* {dt}'
        )
        send_telegram_message(msg)

  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  check_bse_filings()