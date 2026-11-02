import urllib.request, re, gzip

url = 'https://www.amazon.com/dp/B07QXJYTZ7'
req = urllib.request.Request(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read()
        try:
            html = gzip.decompress(data).decode('utf-8', errors='ignore')
        except:
            html = data.decode('utf-8', errors='ignore')
        print('Status:', resp.status, 'HTML length:', len(html))
        if 'validateCaptcha' in html or 'Type the characters' in html:
            print('Encountered Amazon Captcha!')
        else:
            titles = re.findall(r'data-hook="review-title"[^>]*>.*?<span>(.*?)</span>', html, re.DOTALL)
            bodies = re.findall(r'data-hook="review-body"[^>]*>.*?<span>(.*?)</span>', html, re.DOTALL)
            print(f'Found {len(titles)} titles, {len(bodies)} bodies')
            for t, b in zip(titles[:5], bodies[:5]):
                clean_t = re.sub(r'<[^>]+>', '', t).strip()
                clean_b = re.sub(r'<[^>]+>', '', b).strip()
                print('TITLE:', clean_t)
                print('BODY:', clean_b[:300])
                print('-'*40)
except Exception as e:
    print('Error:', e)
