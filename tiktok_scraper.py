"""Scrape public TikTok profiles, videos, comments and hashtags with Python. No login, one file."""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

from curl_cffi import requests

BASE = "https://www.tiktok.com"
# Pinned to Safari: a newer Chrome got an empty refusal on video pages in our tests.
BROWSER = "safari184"
HEADERS = {"Accept-Language": "en-US,en;q=0.9"}

PAGE_DATA = re.compile(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', re.S)
EMBED_DATA = re.compile(r'<script id="__FRONTITY_CONNECT_STATE__" type="application/json">(.*?)</script>', re.S)


class ScrapeError(Exception):
    pass


def iso(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat() if ts else None


def to_int(value):
    """TikTok sends exact counts as strings and rounded ones as numbers."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def username_of(value):
    value = value.strip()
    if "/@" in value:
        value = value.split("/@", 1)[1].split("/", 1)[0].split("?", 1)[0]
    return value.lstrip("@").strip("/")


def video_id_of(value):
    """Return (username, video_id) from a video URL or a bare numeric id."""
    value = value.strip()
    if value.isdigit():
        return "_", value  # the page redirects any name to the real author
    match = re.search(r"/@([^/]+)/video/(\d+)", urlparse(value).path)
    if not match:
        raise ScrapeError(f"Not a TikTok video URL: {value} (expected https://www.tiktok.com/@user/video/123...)")
    return match.group(1), match.group(2)


def hashtag_of(value):
    return value.strip().lstrip("#").lower().split("/")[-1]


def clean_embed_video(v):
    """One entry of the video list the embed pages return."""
    return {
        "id": v["id"],
        "url": f"{BASE}/@{v.get('authorUniqueId')}/video/{v['id']}",
        "description": v.get("desc"),
        # The id holds the upload time in its top bits; it is within a minute of the real time.
        "created_at": iso(int(v["id"]) >> 32),
        "username": v.get("authorUniqueId"),
        "play_count": to_int(v.get("playCount")),
        "width": v.get("width"),
        "height": v.get("height"),
        "cover_url": v.get("originCoverUrl") or v.get("coverUrl"),
        "play_url": v.get("playAddr"),
    }


class TikTok:
    def __init__(self, proxy=None):
        proxies = {"http": proxy, "https": proxy} if proxy else None
        self.http = requests.Session(impersonate=BROWSER, proxies=proxies)

    def _get(self, url, what, ok_statuses=(200,)):
        try:
            resp = self.http.get(url, headers=HEADERS, timeout=30)
        except requests.RequestsError as exc:
            raise ScrapeError(f"Network error: {exc}") from exc
        blocked = (
            "TikTok blocked this IP. It does this to datacenter IPs and to some home or residential ones. "
            "Run from a home connection, or pass --proxy with a sticky US residential proxy."
        )
        if "_wafchallengeid" in resp.text[:3000]:
            raise ScrapeError(f"{blocked} (It sent its 'Please wait...' challenge page instead of {what}.)")
        if resp.status_code in (403, 429, 503):
            raise ScrapeError(f"{blocked} (HTTP {resp.status_code} for {what}.)")
        if resp.status_code not in ok_statuses:
            raise ScrapeError(f"TikTok answered HTTP {resp.status_code} for {what}.")
        return resp

    def _page_scope(self, url, scope, what):
        """Load a normal TikTok page and return one scope of its embedded JSON data."""
        html = self._get(url, what).text
        match = PAGE_DATA.search(html)
        if not match:
            raise ScrapeError(f"No data on the page for {what}. TikTok may have changed its pages, or blocked this IP.")
        return json.loads(match.group(1)).get("__DEFAULT_SCOPE__", {}).get(scope)

    def _embed(self, path, what, missing="Not found or not public"):
        """Load a TikTok embed page and return its data block. HTTP 400 means no such item."""
        resp = self._get(f"{BASE}/embed/{path}", what, ok_statuses=(200, 400, 404))
        match = EMBED_DATA.search(resp.text)
        if not match:
            raise ScrapeError(f"No data on the embed page for {what}. TikTok may have changed its pages.")
        data = json.loads(match.group(1)).get("source", {}).get("data", {})
        block = next((v for k, v in data.items() if k.startswith("/embed") and isinstance(v, dict)), None)
        if resp.status_code != 200 or not block or block.get("isError"):
            raise ScrapeError(f"{missing}: {what}")
        return block

    # --- profile ---------------------------------------------------------

    def profile(self, username):
        detail = self._page_scope(f"{BASE}/@{quote(username)}", "webapp.user-detail", f"profile {username}")
        info = (detail or {}).get("userInfo")
        if not info:
            raise ScrapeError(f"Profile not found: {username}")
        user = info["user"]
        # statsV2 has exact counts; the older "stats" block rounds big numbers.
        stats = info.get("statsV2") or info.get("stats") or {}
        link = (user.get("bioLink") or {}).get("link")
        return {
            "id": user.get("id"),
            "username": user.get("uniqueId"),
            "url": f"{BASE}/@{user.get('uniqueId')}",
            "nickname": user.get("nickname"),
            "bio": user.get("signature"),
            "bio_link": link,
            "is_verified": user.get("verified"),
            "is_private": user.get("privateAccount"),
            "created_at": iso(user.get("createTime")),
            "followers_count": to_int(stats.get("followerCount")),
            "following_count": to_int(stats.get("followingCount")),
            "likes_count": to_int(stats.get("heartCount")),
            "videos_count": to_int(stats.get("videoCount")),
            "avatar_url": user.get("avatarLarger"),
        }

    # --- videos ----------------------------------------------------------

    def video(self, url_or_id):
        username, vid = video_id_of(url_or_id)
        detail = self._page_scope(f"{BASE}/@{quote(username)}/video/{vid}", "webapp.video-detail", f"video {vid}")
        if not detail or detail.get("statusCode") != 0:
            raise ScrapeError(f"Video not found or not public: {vid}")
        item = detail["itemInfo"]["itemStruct"]
        author, music, vid_info = item.get("author") or {}, item.get("music") or {}, item.get("video") or {}
        stats = item.get("statsV2") or item.get("stats") or {}
        return {
            "id": item["id"],
            "url": f"{BASE}/@{author.get('uniqueId')}/video/{item['id']}",
            "description": item.get("desc"),
            "created_at": iso(item.get("createTime")),
            "duration_seconds": vid_info.get("duration"),
            "width": vid_info.get("width"),
            "height": vid_info.get("height"),
            "hashtags": [c["title"] for c in item.get("challenges") or [] if c.get("title")],
            "language": item.get("textLanguage"),
            "location": item.get("locationCreated"),
            "is_ad": item.get("isAd"),
            "is_ai_generated": item.get("IsAigc"),
            "play_count": to_int(stats.get("playCount")),
            "like_count": to_int(stats.get("diggCount")),
            "comment_count": to_int(stats.get("commentCount")),
            "share_count": to_int(stats.get("shareCount")),
            "save_count": to_int(stats.get("collectCount")),
            "username": author.get("uniqueId"),
            "nickname": author.get("nickname"),
            "author_is_verified": author.get("verified"),
            "music_id": music.get("id"),
            "music_title": music.get("title"),
            "music_author": music.get("authorName"),
            "music_is_original": music.get("original"),
            "cover_url": vid_info.get("originCover") or vid_info.get("cover"),
            "play_url": vid_info.get("playAddr"),
        }

    def videos(self, username, limit=11, details=False):
        """A creator's latest public videos, from their embed page. It lists about 11 and has no next page."""
        block = self._embed(f"@{quote(username)}", f"videos of {username}")
        out = [clean_embed_video(v) for v in block.get("videoList") or [] if not v.get("privateItem")][:limit]
        if details:
            out = [self.video(v["url"]) for v in out]
        return out

    # --- comments --------------------------------------------------------

    def comments(self, url_or_id, limit=50):
        _, vid = video_id_of(url_or_id)
        out, cursor = [], 0
        while len(out) < limit:
            api = f"{BASE}/api/comment/list/?aid=1988&aweme_id={vid}&count={min(50, limit - len(out))}&cursor={cursor}"
            resp = self._get(api, f"comments of {vid}")
            try:
                data = resp.json()
            except ValueError:
                raise ScrapeError("TikTok returned no comment data for this request. Try another IP.")
            if "total" not in data and not out:
                # A video that does not exist answers with no "total" at all.
                raise ScrapeError(f"Video not found, or comments are turned off: {vid}")
            for c in data.get("comments") or []:
                user = c.get("user") or {}
                out.append({
                    "id": c.get("cid"),
                    "text": c.get("text"),
                    "created_at": iso(c.get("create_time")),
                    "like_count": c.get("digg_count"),
                    "reply_count": c.get("reply_comment_total") or 0,
                    "username": user.get("unique_id"),
                    "nickname": user.get("nickname"),
                })
            if not data.get("has_more") or not data.get("comments"):
                break
            cursor = data.get("cursor")
        return out[:limit]

    # --- hashtags --------------------------------------------------------

    def hashtag(self, name, limit=10):
        """Hashtag totals plus its top videos. The embed page shows a short list, not the whole tag."""
        tag = hashtag_of(name)
        block = self._embed(
            f"tag/{quote(tag)}", f"hashtag #{tag}",
            missing="Hashtag not found, or TikTok does not show it on its embed page (it hides some big tags)",
        )
        info = block.get("embedInfo") or {}
        return {
            "name": tag,
            "url": f"{BASE}/tag/{quote(tag)}",
            "id": info.get("id"),
            "view_count": to_int(info.get("viewCount")),
            "video_count": to_int(info.get("videoCount")),
            "top_videos": [clean_embed_video(v) for v in block.get("videoList") or []][:limit],
        }


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY"), help="proxy URL, e.g. http://user:pass@host:port")
    common.add_argument("-o", "--output", help="write JSON to this file")
    parser = argparse.ArgumentParser(description="Scrape public TikTok data. No login.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("profile", parents=[common], help="public profile").add_argument("usernames", nargs="+")
    sub.add_parser("video", parents=[common], help="one video").add_argument("videos", nargs="+", help="video URL or id")
    p = sub.add_parser("videos", parents=[common], help="a creator's latest videos (about 11)")
    p.add_argument("username")
    p.add_argument("--limit", type=int, default=11)
    p.add_argument("--details", action="store_true", help="fetch each video page for likes, comments, shares and music")
    p = sub.add_parser("comments", parents=[common], help="comments on a video")
    p.add_argument("video", help="video URL or id")
    p.add_argument("--limit", type=int, default=50)
    p = sub.add_parser("hashtag", parents=[common], help="hashtag totals and top videos")
    p.add_argument("name", help="hashtag, with or without the #")
    p.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    try:
        tt = TikTok(args.proxy)
        if args.command == "profile":
            data = [tt.profile(username_of(u)) for u in args.usernames]
        elif args.command == "video":
            data = [tt.video(v) for v in args.videos]
        elif args.command == "videos":
            data = tt.videos(username_of(args.username), args.limit, args.details)
        elif args.command == "comments":
            data = tt.comments(args.video, args.limit)
        else:
            data = tt.hashtag(args.name, args.limit)
    except ScrapeError as exc:
        sys.exit(f"Error: {exc}")

    if args.command in ("profile", "video") and len(data) == 1:
        data = data[0]
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"Saved to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
