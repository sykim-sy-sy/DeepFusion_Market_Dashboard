import requests
import re
from base64 import urlsafe_b64decode

def decode_google_news_url(url):
    try:
        response = requests.get(url, timeout=10)
        # Look for window.location.replace("...") or <c-wiz data-n-v="URL">
        match = re.search(r'data-n-v="([^"]+)"', response.text)
        if match:
            return match.group(1)
        
        # Or look for actual URL in the text
        match = re.search(r'(URL|url)=[\'"]?(https?://[^\'">]+)', response.text)
        if match:
            return match.group(2)
        
        return "Not found"
    except Exception as e:
        return f"Error: {e}"

url = "https://news.google.com/rss/articles/CBMipAFBVV95cUxQQlE2cUhOZUhtZk91ZTRaX3RYdDlJMElyUXZ5OW9WdkxxNnE0aEcwQzU5VzZkcmNWUm1xY2Y0aTRzNVJEM0l2VTVlZUxNbmxMTE9Icjdoamw3M3ZWaUxZUVY0YkRkcm03cWpXanBNWUdXaVl6d3p2ZTRjQUlyQUl2X3g5bDlIUkxxRU5qZ3p6a2ZpWDFvNndrNGd0eHhkamc2NnlfXw?oc=5"
print(decode_google_news_url(url))
