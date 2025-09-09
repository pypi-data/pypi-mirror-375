import aiohttp
import asyncio
from bs4 import BeautifulSoup

class ContentExtractor:
    def __init__(self, url: str):
        self.url = url
        self.structured = {f"h{i}": [] for i in range(1, 7)}
        self.structured["paragraphs"] = []

    async def fetch_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                return await resp.text()

    async def extract(self):
        html = await self.fetch_page()
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted elements
        for tag in soup(["script", "style", "footer", "nav", "header", "aside", "img"]):
            tag.decompose()

        clean_lines = []

        # Loop through all content elements
        for el in soup.find_all(["h1","h2","h3","h4","h5","h6","p","li"]):
            text = el.get_text(strip=True)
            if not text:
                continue

            if el.name in ["h1","h2","h3","h4","h5","h6"]:
                self.structured[el.name].append(text)
                clean_lines.append(f"\n{text}\n")
            else:  # p, li
                self.structured["paragraphs"].append(text)
                clean_lines.append(text)

        clean_text = "\n\n".join(clean_lines)

        return {
            "url": self.url,
            "clean_text": clean_text,
            "structured": self.structured
        }

# Example usage with asyncio
# async def main():
#     extractor = ContentExtractor("https://shailatech.com/digital-marketing-seo")
#     data = await extractor.extract()
#     print(data)
# asyncio.run(main())
