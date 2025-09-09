import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
from collections import deque
import hashlib
import time
import re
from contextlib import asynccontextmanager
import xml.etree.ElementTree as ET

class WebsiteAuditor:
    def __init__(self, url, sitemap=True, max_pages=100):
        self.url = url
        self.sitemap = sitemap
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque()
        self.report = {
            "pages": [],
            "errors": [],
            "broken_links": [],
            "duplicates": {"titles": [], "descriptions": [], "contents": []},
            "favicon": False,
            "summary": {}
        }
        self.titles = {}
        self.descriptions = {}
        self.contents = {}

        self.sitemap_urls = set()
        self.robots_disallow = []

    # ----------------- URL helpers -----------------
    def normalize_url(self, url):
        url = url.strip()
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return None
        clean = parsed._replace(fragment="", query="")
        return urlunparse(clean).rstrip("/")

    def is_valid_http(self, url):
        return bool(self.normalize_url(url))

    def is_allowed_by_robots(self, url):
        parsed = urlparse(url)
        path = parsed.path
        for rule in self.robots_disallow:
            if path.startswith(rule):
                return False
        return True

    # ----------------- HTTP -----------------
    @asynccontextmanager
    async def aiohttp_session(self):
        async with aiohttp.ClientSession() as session:
            yield session

    async def fetch(self, session, url):
        try:
            start = time.time()
            async with session.get(url, timeout=15) as resp:
                text = await resp.text(errors="ignore")
                load_time = round(time.time() - start, 2)
                return resp.status, text, load_time
        except Exception as e:
            self.report["errors"].append({"url": url, "error": str(e)})
            return None, None, None

    # ----------------- Sitemap & Robots -----------------
    async def parse_robots_txt(self, session, domain):
        robots_url = urljoin(domain, "/robots.txt")
        status, text, _ = await self.fetch(session, robots_url)
        if status != 200 or not text:
            return
        for line in text.splitlines():
            line = line.strip()
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path: self.robots_disallow.append(path)

    async def parse_sitemap(self, session, domain):
        sitemap_url = urljoin(domain, "/sitemap.xml")
        status, text, _ = await self.fetch(session, sitemap_url)
        if status != 200 or not text:
            return
        try:
            root = ET.fromstring(text)
            for url_tag in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                loc = url_tag.text.strip()
                normalized = self.normalize_url(loc)
                if normalized:
                    self.sitemap_urls.add(normalized)
        except ET.ParseError:
            pass

    # ----------------- Duplicates -----------------
    def hash_content(self, text):
        return hashlib.md5(text.encode("utf-8")).hexdigest() if text else None

    def check_duplicates(self, url, title, desc, content_hash):
        if title:
            if title in self.titles and self.titles[title] != url:
                self.report["duplicates"]["titles"].append({"url": url, "duplicate_of": self.titles[title], "title": title})
            else:
                self.titles[title] = url
        if desc:
            if desc in self.descriptions and self.descriptions[desc] != url:
                self.report["duplicates"]["descriptions"].append({"url": url, "duplicate_of": self.descriptions[desc], "description": desc})
            else:
                self.descriptions[desc] = url
        if content_hash:
            if content_hash in self.contents and self.contents[content_hash] != url:
                self.report["duplicates"]["contents"].append({"url": url, "duplicate_of": self.contents[content_hash]})
            else:
                self.contents[content_hash] = url

    # ----------------- Page audit -----------------
    async def audit_page(self, session, url, domain):
        status, html, load_time = await self.fetch(session, url)
        if not status or status != 200:
            self.report["errors"].append({"url": url, "status": status})
            return []

        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title else ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        robots = robots_tag["content"].strip() if robots_tag and robots_tag.get("content") else None
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        keywords = keywords_tag["content"].strip() if keywords_tag and keywords_tag.get("content") else None

        og_tags = {tag["property"]: tag.get("content", "") for tag in soup.find_all("meta", property=re.compile("^og:"))}

        content_hash = self.hash_content(soup.get_text(" ", strip=True))
        self.check_duplicates(url, title, desc, content_hash)

        issues = []

        if not title: issues.append("Missing title")
        elif len(title) > 60: issues.append("Title too long (>60 chars)")
        if not desc: issues.append("Missing meta description")
        elif len(desc) > 160: issues.append("Description too long (>160 chars)")

        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
        if not h1_tags: issues.append("Missing H1")
        if len(h1_tags) > 1: issues.append("Duplicate H1 tags")
        if len(set(h2_tags)) < len(h2_tags): issues.append("Duplicate H2 tags")

        # Images
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src")
            if src:
                img_url = urljoin(url, src)
                if self.is_valid_http(img_url):
                    img_status, _, _ = await self.fetch(session, img_url)
                    if not img_status or img_status >= 400:
                        issues.append(f"Broken image: {img_url}")
                if not img.get("alt"):
                    issues.append(f"Image missing alt: {img_url}")
                if not img.get("loading"):
                    issues.append(f"Image missing lazy loading: {img_url}")

        # CSS & JS
        assets = []
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href:
                css_url = urljoin(url, href)
                if self.is_valid_http(css_url): assets.append(css_url)
        for script in soup.find_all("script", src=True):
            js_url = urljoin(url, script["src"])
            if self.is_valid_http(js_url): assets.append(js_url)

        asset_tasks = [self.fetch(session, a) for a in assets]
        results = await asyncio.gather(*asset_tasks, return_exceptions=True)
        for i, res in enumerate(results):
            if isinstance(res, tuple):
                st, _, _ = res
                if not st or st >= 400:
                    issues.append(f"Broken asset: {assets[i]}")

        # Internal links
        links = []
        for a in soup.find_all("a", href=True):
            raw_link = urljoin(url, a["href"])
            link = self.normalize_url(raw_link)
            if not link or domain not in link: 
                continue
            if not self.is_allowed_by_robots(link): 
                continue
            links.append(link)

            anchor_text = a.get_text(strip=True)
            if not anchor_text or len(anchor_text) < 2:
                issues.append(f"Anchor text too short or empty: {link}")

        # Favicon
        if not self.report["favicon"]:
            for fav in ["/favicon.ico", "/favicon.png"]:
                fav_url = f"{domain.rstrip('/')}{fav}"
                fav_status, _, _ = await self.fetch(session, fav_url)
                if fav_status and fav_status == 200:
                    self.report["favicon"] = True
                    break

        self.report["pages"].append({
            "url": url,
            "status": status,
            "title": title,
            "description": desc,
            "robots": robots,
            "keywords": keywords,
            "og_tags": og_tags,
            "load_time": load_time,
            "issues": issues
        })

        return links

    # ----------------- Crawl -----------------
    async def crawl(self):
        parsed = urlparse(self.url if self.url.startswith("http") else "https://" + self.url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        self.queue.append(domain)

        async with aiohttp.ClientSession() as session:
            # Parse robots.txt
            await self.parse_robots_txt(session, domain)
            # Parse sitemap if enabled
            if self.sitemap:
                await self.parse_sitemap(session, domain)
                for s_url in self.sitemap_urls:
                    if s_url not in self.visited:
                        self.queue.append(s_url)

            while self.queue and len(self.visited) < self.max_pages:
                page = self.queue.popleft()
                normalized_page = self.normalize_url(page)
                if not normalized_page or normalized_page in self.visited: 
                    continue
                self.visited.add(normalized_page)
                new_links = await self.audit_page(session, normalized_page, domain)
                for l in new_links:
                    if l not in self.visited and len(self.visited) + len(self.queue) < self.max_pages:
                        self.queue.append(l)

    # ----------------- Run -----------------
    async def run(self):
        await self.crawl()
        self.report["summary"] = {
            "total_pages": len(self.report["pages"]),
            "errors": len(self.report["errors"]),
            "broken_links": len(self.report.get("broken_links", [])),
            "duplicates": {
                "titles": len(self.report["duplicates"]["titles"]),
                "descriptions": len(self.report["duplicates"]["descriptions"]),
                "contents": len(self.report["duplicates"]["contents"])
            }
        }
        return self.report
