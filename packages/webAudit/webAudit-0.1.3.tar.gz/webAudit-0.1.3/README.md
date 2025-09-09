# webAudit

**webAudit** is an async Python library and CLI tool for website auditing, content extraction, SEO analysis, crawling, and PageSpeed Insights. It allows developers and website owners to quickly analyze websites for SEO, performance, and content quality.

---

## Features

- **Website Audit**: Crawl a site and generate a comprehensive audit report (status codes, headings, meta tags, internal links, broken links, load time, and more).  
- **Content Extraction**: Extract clean text from any page.  
- **SEO Analysis**: Analyze title, meta description, H1 count, and images without alt attributes.  
- **Website Crawl**: Crawl a site and list URLs with optional HTTP status check.  
- **PageSpeed Insights**: Run Google PageSpeed API audits for performance, SEO, accessibility, and best practices.  
- **Test-All Command**: Run all checks sequentially for quick testing.  

---

## Installation

### From PyPI
```bash
pip install webAudit
```

### Or from source
```bash
git clone https://github.com/amjadkhan345/Website_audit
cd Website_audit
pip install .
```

> After installation, the CLI command `webAudit` will be available globally.

---

## CLI Usage

### 1️⃣ Audit a Website
```bash
webAudit audit https://example.com --max-pages 20 --sitemap
```
- `--max-pages` → Maximum pages to crawl (default: 50)  
- `--sitemap` → Use sitemap URLs for crawling  

**Output:** Progress bar and CSV report `audit_report.csv`.

---

### 2️⃣ Extract Page Content
```bash
webAudit extract https://example.com/page 
```


**Output:** Clean extracted text.

---

### 3️⃣ SEO Analysis
```bash
webAudit seo https://example.com
```

**Output Example:**
```json
{
  "title": "Example Page",
  "meta_description": "This is an example website",
  "h1_count": 2,
  "img_without_alt": 3
}
```

---

### 4️⃣ Crawl a Website
```bash
webAudit crawl https://example.com 
```


**Output:** List of discovered URLs with optional HTTP status.

---

### 5️⃣ PageSpeed Insights
```bash
webAudit pagespeed https://example.com YOUR_API_KEY --strategy mobile
```
- `--strategy mobile|desktop` → Run PageSpeed for mobile or desktop (default: mobile)  

**Output Example:**
```json
{
  "performance": 0.85,
  "seo": 0.92,
  "accessibility": 0.88,
  "best_practices": 0.95
}
```

---



## Class & Function-Based Usage

You can also use **webAudit** programmatically in your Python code.

### 1️⃣ Website Audit
```python
import asyncio
from webAudit.auditor import WebsiteAuditor

async def audit_site():
    auditor = WebsiteAuditor("https://example.com", max_pages=10, sitemap=True)
    report = await auditor.run()
    print(report)

asyncio.run(audit_site())
```

---

### 2️⃣ Content Extraction
```python
import asyncio
from webAudit.extractor import ContentExtractor

async def extract_content():
    extractor = ContentExtractor("https://example.com/page")
    content = await extractor.extract()
    print(content)

asyncio.run(extract_content())
```

---

### 3️⃣ SEO Analysis
```python
from webAudit.seo import analyze_seo

seo_report = analyze_seo("https://example.com")
print(seo_report)
```

---

### 4️⃣ Crawl a Website
```python
import asyncio
from webAudit.crawler import async_crawl_with_links

async def crawl_site():
    pages = await async_crawl_with_links("https://example.com", max_pages=10)
    print(pages)

asyncio.run(crawl_site())
```

---

### 5️⃣ PageSpeed Insights
```python
from webAudit.pagespeed import pagespeed_audit

result = pagespeed_audit("https://example.com", api_key="YOUR_API_KEY", strategy="mobile")
print(result)
```

---

## Requirements

- Python 3.10+  
- `aiohttp`  
- `beautifulsoup4`  
- `lxml`  
- `tqdm`  

> Install dependencies via pip:  
```bash
pip install -r requirements.txt
```

---

## Contributing

1. Fork the repository  
2. Create a new branch (`git checkout -b feature-name`)  
3. Make your changes  
4. Commit (`git commit -m "Add new feature"`)  
5. Push (`git push origin feature-name`)  
6. Open a Pull Request  

---

## License

[MIT License](LICENSE)  

---

## Contact

For questions or support:  
- Email: `info@shailatech.com`  
- GitHub: [https://github.com/amjadkhan345/Website_audit](https://github.com/amjadkhan345/Website_audit)
