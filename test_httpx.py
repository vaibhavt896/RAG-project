import httpx
import tempfile

url = "https://www.infosys.com/investors/reports-filings/annual-report/annual/documents/infosys-ar-25.pdf"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

try:
    print(f"Downloading {url}...")
    response = httpx.get(url, headers=headers, timeout=60, follow_redirects=True)
    print(f"Status Code: {response.status_code}")
    response.raise_for_status()
    print(f"Downloaded {len(response.content)} bytes.")
except Exception as e:
    print(f"Error: {e}")
