import requests
def pagespeed_audit(url, api_key, strategy='mobile'):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {'url': url, 'strategy': strategy, 'key': api_key}
    try:
        resp = requests.get(endpoint, params=params, timeout=10).json()
        lighthouse = resp.get('lighthouseResult', {})
        categories = lighthouse.get('categories', {})
        return {
            'performance': categories.get('performance', {}).get('score'),
            'seo': categories.get('seo', {}).get('score'),
            'accessibility': categories.get('accessibility', {}).get('score'),
            'best_practices': categories.get('best-practices', {}).get('score')
        }
    except:
        return {}