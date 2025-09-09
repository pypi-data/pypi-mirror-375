import datetime
import pendulum
import socket
import sys
from pathlib import Path

import feedparser
import ffmpeg
import httpx
import yt_dlp

from bs4 import BeautifulSoup
from dateutil import parser
from liquid import parse
from piou import Cli, Option
from slugify import slugify

from ytube_podcast.rumble import generate_feed

cli = Cli(description='Youtube to Podcast Generator')

feedparser.USER_AGENT = f"Podtube CLI/1.0 ({socket.gethostname()})"


@cli.main()
def main(
    channel_id: str = Option(..., help='Channel ID'),
    template: Path = Option(..., help="feed template"),
    channel_type: str = Option("youtube", "-t", "--type", help='Channel Type'),
    feed: Path = Option(Path("feed.xml"), "-f", "--feed", help="output feed", raise_path_does_not_exist=False),
    media_dir: Path = Option(Path('media'), "-m", "--media", help="media output directory"),
    limit: str = Option(50, "-l", "--limit", help='Entry limit'),
    redownload: bool = Option(False, "-r", "--redownload", help='Re-Download All Files'),
  ):

  with template.open('r') as fh:
    tpl_text = fh.read()

  if not media_dir.exists():
    media_dir.mkdir(parents=True)

  context = {
    'utcnow': pendulum.now('UTC').to_rss_string(),
    'entries': []
  }

  if channel_type == 'rumble':
    xmlfeed = generate_feed(channel_id)

  else:
    xmlurl = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    xmlfeed = feedparser.parse(xmlurl)
    if xmlfeed.status != 200:
      print("Failed to get RSS feed. Status code:", xmlfeed.status)
      sys.exit(1)

  for i, entry in enumerate(xmlfeed.entries):
    if i == (limit - 1):
      break

    if channel_type == 'rumble':
      thumb_url = entry.thumb_url

    else:
      thumb_url = entry.media_thumbnail[0]['url']

    media_path = media_dir / (slugify(entry.title) + '.mp3')
    thumb_path = media_dir / (slugify(entry.title) + '.' + thumb_url.split('.')[-1])
    entry['media_path'] = media_path
    entry['thumb_path'] = thumb_path

    dt = parser.parse(entry["published"])
    entry['published'] = pendulum.instance(dt).to_rss_string()

    context['entries'].append(entry)
    if media_path.exists():
      if not redownload:
        print('Skipping Download:', entry.title)
        entry['media_size'] = media_path.stat().st_size
        continue

    print('Downloading:', entry.title)
    with thumb_path.open('wb') as fh:
      response = httpx.get(thumb_url)
      fh.write(response.content)

    opts = {
      'extract_audio': True,
      'format': 'bestaudio',
      'outtmpl': 'output.%(ext)s'
    }
    with yt_dlp.YoutubeDL(opts) as video:
      info_dict = video.extract_info(entry.link, download=True)
      tmp_path = Path(f'output.{info_dict['audio_ext']}')
      (
        ffmpeg
        .input(str(tmp_path))
        .output(str(media_path))
        .run()
      )
      tmp_path.unlink()

    entry['media_size'] = media_path.stat().st_size

  template = parse(tpl_text)
  output = template.render(**context)
  with feed.open('w') as fh:
    fh.write(output)

def run():
  cli.run()

if __name__ == '__main__':
  run()
