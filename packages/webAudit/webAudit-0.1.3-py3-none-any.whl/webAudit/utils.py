import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import deque
import hashlib
import time


def process_sitemap(sitemap_url):
        """Recursively process sitemap.xml files"""
        resp, _ = self._get(sitemap_url)
        if resp and resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "xml")
            for loc in soup.find_all("loc"):
                link = loc.get_text().strip()
                if link in self.visited or len(self.visited) >= self.max_pages:
                    continue
                self.visited.add(link)
                if link.endswith(".xml"):
                    # sitemap pointing to another sitemap
                    process_sitemap(link)
                else:
                    # normal page
                    new_links = self.audit_page(link, domain)
                    self.queue.extend(new_links)