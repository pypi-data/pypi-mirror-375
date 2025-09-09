import httpx
from bs4 import BeautifulSoup as bs

from feedparser import FeedParserDict

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

def generate_feed(channel):
  response = httpx.get(f'https://rumble.com/c/{channel}', headers=HEADERS)
  page_soup = bs(response.content, 'html.parser')
  articles = page_soup.find_all("div", class_="videostream")
  entries = []
  for article in articles:
    if article.find('time') is None:
      continue

    link = f'https://rumble.com{article.find('a')['href']}'
    response = httpx.get(link, headers=HEADERS)
    more_soup = bs(response.content, 'html.parser')
    desc = more_soup.find("p", class_="media-description")
    if desc:
      desc = desc.text.strip()

    else:
      desc = ''

    entries.append(FeedParserDict({
      'title': article.find('h3').text.strip(),
      'published': article.find('time')['datetime'],
      'thumb_url': article.find('img')['src'],
      'link': link,
      'description': desc,
      'summary': desc,
    }))

  return FeedParserDict(
    bozo=False,
    entries=entries,
    feed=FeedParserDict(),
    headers={},
  )
