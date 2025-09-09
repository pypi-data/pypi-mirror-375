import scrapy
from urllib.parse import urljoin
import requests

class AuditSpider(scrapy.Spider):
    name = "audit_spider"
    custom_settings = {'LOG_LEVEL': 'ERROR'}

    def __init__(self, url, max_pages=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.visited = set()
        self.max_pages = max_pages
        self.pages = []

    def parse(self, response):
        if len(self.visited) >= self.max_pages:
            return
        self.visited.add(response.url)
        self.pages.append(response.url)
        for link in response.css('a::attr(href)').getall():
            url = urljoin(response.url, link)
            if url not in self.visited:
                yield scrapy.Request(url, callback=self.parse)

def check_links(urls):
    results = []
    for url in urls:
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            status = r.status_code
        except requests.RequestException:
            status = None
        results.append({'url': url, 'status': status})
    return results