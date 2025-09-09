import requests
from bs4 import BeautifulSoup

def analyze_seo(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'lxml')
    except:
        return {}
    seo_report = {
        'title': soup.title.string if soup.title else None,
        'meta_description': None,
        'h1_count': len(soup.find_all('h1')),
        'img_without_alt': len([img for img in soup.find_all('img') if not img.get('alt')])
    }
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        seo_report['meta_description'] = desc_tag.get('content')
    return seo_report