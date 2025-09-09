import argparse
import asyncio
import csv
import json
from tqdm.asyncio import tqdm
from .auditor import WebsiteAuditor
from .extractor import ContentExtractor   # <-- new extractor


def parse_args():
    parser = argparse.ArgumentParser(
        description="Async Website Auditor with SEO checks"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Audit subcommand ---
    audit_parser = subparsers.add_parser("audit", help="Audit a website")
    audit_parser.add_argument("url", help="Target website URL")
    audit_parser.add_argument("--sitemap", action="store_true", help="Use sitemap for crawling")
    audit_parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to audit")

    # --- Extract subcommand ---
    extract_parser = subparsers.add_parser("extract", help="Extract clean text from a page")
    extract_parser.add_argument("url", help="Page URL to extract content from")
    extract_parser.add_argument(
        "--mode",
        choices=["smart"],
        default="smart",
        help="Extraction mode (default: smart)",
    )

    return parser.parse_args()


# ----------------------
# AUDIT
# ----------------------
async def run_audit(args):
    auditor = WebsiteAuditor(args.url, sitemap=args.sitemap, max_pages=args.max_pages)

    print(f"Starting full website audit for {args.url} ...")

    visited_pages = set()

    async def crawl_with_progress():
        async for page_url in async_crawl_with_progress(auditor):
            visited_pages.add(page_url)
            tqdm_bar.update(1)

    async def async_crawl_with_progress(auditor):
        """Generator that yields pages as they are crawled"""
        queue = [auditor.url]
        domain = auditor.url

        async with auditor.aiohttp_session() as session:
            while queue and len(visited_pages) < auditor.max_pages:
                page = queue.pop(0)
                if page in visited_pages:
                    continue
                visited_pages.add(page)
                # audit_page now returns internal links for further crawling
                new_links = await auditor.audit_page(session, page, domain)
                for l in new_links:
                    if l not in visited_pages and len(visited_pages) + len(queue) < auditor.max_pages:
                        queue.append(l)
                yield page

    tqdm_bar = tqdm(total=args.max_pages, desc="Auditing pages", ncols=100)
    await crawl_with_progress()
    tqdm_bar.close()

    # Run final SEO/completeness analysis
    report = await auditor.run()

    print("Audit completed!")
    print(report)

    # Save report
    csv_file = "audit_report.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "url", "status", "title", "description", "robots", "keywords",
            "og_tags", "h1", "h2", "internal_links", "broken_links",
            "load_time", "issues"
        ])
        writer.writeheader()
        for page in report["pages"]:
            writer.writerow(page)

    print(f"Report saved as {csv_file}")


# ----------------------
# EXTRACT
# ----------------------
async def run_extract(args):
    #extractor = ContentExtractor()
    #extracted =asyncio.run(extract(args.url))
    extractor = ContentExtractor(args.url)
    result = await extractor.extract()
    print(result)


def run_cli():
    args = parse_args()
    if args.command == "audit":
        asyncio.run(run_audit(args))
    elif args.command == "extract":
        asyncio.run(run_extract(args))


if __name__ == "__main__":
    run_cli()
