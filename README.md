# TikTok Scraper (Python)

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Last verified](https://img.shields.io/badge/last%20verified-2026--10--13-brightgreen.svg)](#how-we-keep-it-working)

Scrape public TikTok profiles, videos, comments and hashtags with Python. No login, no API key, one file.

> **Need this at scale?** The script is for learning and small jobs. The [ToolzerHub TikTok API](https://toolzerhub.com/apis/tiktok?utm_source=github&utm_medium=readme&utm_campaign=tiktok-scraper) returns profiles, videos, full paged hashtag video lists and videos by sound (plus TikTok Shop products) as JSON from any server, with no blocks to handle. 100 free credits a month, no card needed.

## What it scrapes

| Command | What you get |
|---|---|
| `profile <username>...` | Bio, link in bio, verified flag, join date, and exact follower, following, like and video counts |
| `video <url>...` | One video with its caption, hashtags, play, like, comment, share and save counts, author, music, cover and play links |
| `videos <username>` | A creator's latest public videos (about 11) with caption, date, play count and links |
| `comments <url>` | Comments on a video with text, date, likes, reply count and author |
| `hashtag <name>` | Total views and videos for a hashtag, plus a short list of its top videos |

## Quick start

```bash
git clone https://github.com/toolzerhub/tiktok-scraper.git
cd tiktok-scraper
pip install -r requirements.txt
python tiktok_scraper.py profile nasa
```

More examples:

```bash
python tiktok_scraper.py profile nasa natgeo duolingo -o profiles.json
python tiktok_scraper.py video https://www.tiktok.com/@nasa/video/7665075736742530317
python tiktok_scraper.py videos natgeo --limit 5 -o natgeo-videos.json
python tiktok_scraper.py videos nasa --details
python tiktok_scraper.py comments https://www.tiktok.com/@nasa/video/7665075736742530317 --limit 100 -o comments.json
python tiktok_scraper.py hashtag cooking --limit 5
```

Every command takes `-o file.json` to save the result and `--proxy URL` to route through a proxy. The script also reads `HTTPS_PROXY`. A user can be a name (`nasa`, `@nasa`) or a profile URL. A video can be a URL or just its numeric id. `videos --details` opens each video page too, so you also get exact likes, comments, shares and music.

## Example output

`python tiktok_scraper.py profile nasa`

```json
{
  "id": "7664638705177150477",
  "username": "nasa",
  "url": "https://www.tiktok.com/@nasa",
  "nickname": "NASA",
  "bio": "Making the seemingly impossible, possible.✨",
  "bio_link": "science.nasa.gov/feature/artemis-ii-preliminary-lunar-science-report",
  "is_verified": true,
  "is_private": false,
  "created_at": "2026-07-20T15:55:49+00:00",
  "followers_count": 2066914,
  "following_count": 23,
  "likes_count": 10963107,
  "videos_count": 56,
  "avatar_url": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/e5143212a59c09a008bf50f487d..."
}
```

`python tiktok_scraper.py video https://www.tiktok.com/@nasa/video/7665075736742530317`

```json
{
  "id": "7665075736742530317",
  "url": "https://www.tiktok.com/@nasa/video/7665075736742530317",
  "description": "Something big just landed on TikTok.",
  "created_at": "2026-07-21T20:09:02+00:00",
  "duration_seconds": 25,
  "width": 720,
  "height": 1280,
  "hashtags": [],
  "language": "en",
  "location": "US",
  "is_ad": false,
  "is_ai_generated": false,
  "play_count": 1600000,
  "like_count": 103600,
  "comment_count": 3024,
  "share_count": 3258,
  "save_count": 7534,
  "username": "nasa",
  "nickname": "NASA",
  "author_is_verified": true,
  "music_id": "7665075815390645006",
  "music_title": "original sound",
  "music_author": "NASA",
  "music_is_original": true,
  "cover_url": "https://p16-common-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/o0HdfAsh9SB9VEQqqXFfDBgq90rHH...",
  "play_url": "https://v16-webapp-prime.us.tiktok.com/video/tos/useast5/tos-useast5-ve-0068c001-tx/okRjOkUA..."
}
```

`python tiktok_scraper.py videos nasa --limit 5` (one video shown)

```json
[
  {
    "id": "7665075736742530317",
    "url": "https://www.tiktok.com/@nasa/video/7665075736742530317",
    "description": "Something big just landed on TikTok.",
    "created_at": "2026-07-21T20:08:37+00:00",
    "username": "nasa",
    "play_count": 1600000,
    "width": 720,
    "height": 1280,
    "cover_url": "https://p16-common-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/o0HdfAsh9SB9VEQqqXFfDBgq90rHH...",
    "play_url": "https://v19.tiktokcdn-us.com/2da38597edbc0f974ebe30aba5882cd4/6ad11b41/video/tos/useast5/tos..."
  }
]
```

`python tiktok_scraper.py comments https://www.tiktok.com/@nasa/video/7665075736742530317 --limit 10` (two comments shown)

```json
[
  {
    "id": "7665263325262201622",
    "text": "Howdy partners! 🚀✨",
    "created_at": "2026-07-22T08:17:14+00:00",
    "like_count": 7688,
    "reply_count": 68,
    "username": "europeanspaceagency",
    "nickname": "ESA"
  },
  {
    "id": "7665081157037802254",
    "text": "TO THE MOON!! 🚀",
    "created_at": "2026-07-21T20:30:12+00:00",
    "like_count": 4713,
    "reply_count": 63,
    "username": "usedgov",
    "nickname": "U.S. Department of Education"
  }
]
```

`python tiktok_scraper.py hashtag cooking --limit 3` (one video shown)

```json
{
  "name": "cooking",
  "url": "https://www.tiktok.com/tag/cooking",
  "id": "18973",
  "view_count": 555276407059,
  "video_count": 19194526,
  "top_videos": [
    {
      "id": "7125823187908070661",
      "url": "https://www.tiktok.com/@simplefood4you/video/7125823187908070661",
      "description": "I LOVE GARLIC 🙊🧄 #garlic #recipe #cooking #foodie #foodtiktok #food #foryou #fyp",
      "created_at": "2022-07-29T15:53:19+00:00",
      "username": "simplefood4you",
      "play_count": 23500000,
      "width": 576,
      "height": 1024,
      "cover_url": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-p-0068/e984510bf215417ca7406af3f9813ffb_...",
      "play_url": "https://v19.tiktokcdn-us.com/732c28b402111d20d246f4b2adda61a6/6ad11b40/video/tos/useast2a/to..."
    }
  ]
}
```

Long links are shortened here. The full outputs for every command are in [examples/](examples).

## Fields

### profile

| Field | Description |
|---|---|
| id | TikTok's numeric user id |
| username | The @handle, without the @ |
| url | Profile link |
| nickname | Display name |
| bio | Bio text |
| bio_link | Link in the bio, or null |
| is_verified | Verified badge |
| is_private | Private account flag |
| created_at | When the account was created, ISO 8601 UTC |
| followers_count, following_count | Exact counts as integers |
| likes_count | Total likes across all videos |
| videos_count | Number of videos |
| avatar_url | Profile picture link (signed, it expires) |

### video

| Field | Description |
|---|---|
| id, url | Video id and link |
| description | Caption |
| created_at | Upload time, ISO 8601 UTC |
| duration_seconds, width, height | Video length and size |
| hashtags | Hashtags in the caption, without the # |
| language, location | Caption language and country code TikTok reports, when it has them |
| is_ad, is_ai_generated | Flags |
| play_count, like_count, comment_count, share_count, save_count | Counts as integers |
| username, nickname, author_is_verified | The author |
| music_id, music_title, music_author, music_is_original | The sound used |
| cover_url | Cover image link (signed, it expires) |
| play_url | MP4 link (signed, it expires). See Limits |

### videos

| Field | Description |
|---|---|
| id, url, description | Video id, link and caption |
| created_at | Upload time, ISO 8601 UTC, read from the video id (within a minute of the real time) |
| username | The author |
| play_count | Plays. TikTok rounds big numbers here. Use `--details` for the other counts |
| width, height | Video size |
| cover_url, play_url | Cover image and MP4 links (signed, they expire) |

With `--details` each item has the same fields as `video`.

### comments

| Field | Description |
|---|---|
| id | Comment id |
| text | Comment text |
| created_at | ISO 8601 UTC |
| like_count, reply_count | Likes and number of replies |
| username, nickname | The commenter |

### hashtag

| Field | Description |
|---|---|
| name, url | Hashtag and its page |
| id | TikTok's numeric hashtag id |
| view_count, video_count | Totals for the whole hashtag |
| top_videos | Same fields as `videos` |

## How it works

1. `profile` and `video` ask for the public page (`tiktok.com/@user` and `tiktok.com/@user/video/ID`) as Safari. The page already holds its data as JSON in a `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">` tag.
2. `videos` and `hashtag` ask for TikTok's embed pages (`tiktok.com/embed/@user` and `tiktok.com/embed/tag/name`), the pages other sites use to show TikTok widgets. They carry a short video list as JSON in a `<script id="__FRONTITY_CONNECT_STATE__">` tag. `comments` calls the comments endpoint the web page uses (`/api/comment/list/`), which answers with plain JSON.
3. Each reply is cleaned into the fields above. Counts become integers, times become ISO 8601 UTC, and the raw blobs are dropped.

## Limits

- Public data only.
- `videos` returns about 11 videos and has no next page. A creator's full video list and keyword search are not available to this script: TikTok only serves them to its own signed web app.
- `hashtag` returns the totals and a short list of top videos, not the whole hashtag. TikTok hides a few very big tags (for example `travel`) from its embed pages, and the script then says so.
- `play_url` from `video` needs the cookies the page request set and a `Referer: https://www.tiktok.com/` header. The `play_url` in `videos` and `hashtag` opens as it is. All of these links expire after a day or two.
- TikTok blocks many datacenter IPs, and some residential ones too. The reply is a tiny "Please wait..." page or an HTTP 503, and the script exits with a "TikTok blocked this IP" error. In our runs every US residential exit worked and several exits elsewhere did not. Run it from a home connection, or pass `--proxy` (a sticky US residential proxy works best).
- No retries, no concurrency. That is on purpose: the script stays short enough to read in one sitting.
- It breaks when TikTok changes its pages. See "How we keep it working".

## Scaling up

The script is for learning and small jobs. At scale you run into blocks, changing page formats and proxy costs. The [ToolzerHub TikTok API](https://toolzerhub.com/apis/tiktok?utm_source=github&utm_medium=readme&utm_campaign=tiktok-scraper) handles all of that:

| | This script | ToolzerHub API |
|---|---|---|
| Data | Profile, video, latest ~11 videos, comments, hashtag totals with a short top list | Profile, video, hashtag details, paged hashtag videos, paged videos by sound (5 TikTok endpoints), plus 16 TikTok Shop endpoints |
| Blocks and proxies | Your problem | Handled |
| When TikTok changes | Wait for a fix here | Fixed on our side |
| Cost | Free, plus your proxy | 100 free credits a month, then from $0.99 per 1,000 calls |

## How we keep it working

Every command is run against live TikTok pages before each update, and the "last verified" badge shows the last day they all passed. If something breaks, [open an issue](https://github.com/toolzerhub/tiktok-scraper/issues).

## FAQ

**Is scraping TikTok legal?**
Scraping publicly available data is generally allowed in many places, but it depends on your country, what you collect and how you use it. Read the Legal section below.

**Why am I getting blocked?**
TikTok blocks most cloud and datacenter IP addresses and some residential ones. Use a home connection or a sticky US residential proxy, and slow down.

**Can it get every video under a hashtag or a sound?**
No. The script only sees a short top list. The [ToolzerHub API](https://toolzerhub.com/apis/tiktok?utm_source=github&utm_medium=readme&utm_campaign=tiktok-scraper) pages through the full video list for a hashtag and for a sound.

## Related scrapers

- [instagram-scraper](https://github.com/toolzerhub/instagram-scraper): public Instagram profiles, posts, comments and search
- [reddit-scraper](https://github.com/toolzerhub/reddit-scraper): public subreddits, posts, comments, search and user posts
- [threads-scraper](https://github.com/toolzerhub/threads-scraper): public Threads profiles, posts, replies and search

## Legal and responsible use

This project is for education and for collecting **publicly available** data. You are responsible for how you use it.

- **Public data only.** The script reads pages anyone can see without an account. Do not use it to get around logins, paywalls, CAPTCHAs or other access controls.
- **Terms and robots rules.** TikTok's terms of service may restrict automated access. Read them and decide for yourself; following them is your responsibility.
- **Personal data.** Profiles and comments can contain personal data. Laws such as the GDPR (EU and UK) and the CCPA (California) may apply. Collect only what you need, have a lawful basis, keep it secure, delete it when you no longer need it, and respect people's requests to access or erase their data.
- **Copyright.** Posts, images and videos belong to their creators. Do not republish them without permission.
- **Be gentle.** Keep request rates low and do not disrupt the service.
- **No warranty.** The software is provided "as is" under the MIT License, without warranty of any kind. The authors are not liable for any claim or damage arising from its use.
- **Not affiliated.** This project is not affiliated with, endorsed by or sponsored by TikTok Ltd. or ByteDance Ltd. TikTok is a trademark of TikTok Ltd.
- **Takedown requests.** If you own rights in something here and want it changed or removed, email contact@toolzerhub.com.

This section is not legal advice. If you are unsure, talk to a lawyer.

## License

[MIT](LICENSE) © ToolzerHub
