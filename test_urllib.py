import urllib.request
import certifi
import ssl

url = "https://www.infosys.com/investors/reports-filings/annual-report/annual/documents/infosys-ar-25.pdf"

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
)

context = ssl.create_default_context(cafile=certifi.where())

try:
    print(f"Downloading {url} with urllib...")
    with urllib.request.urlopen(req, context=context, timeout=60) as response:
        content = response.read()
    print(f"Downloaded {len(content)} bytes. Status: {response.status}")
except Exception as e:
    print(f"Error: {e}")
