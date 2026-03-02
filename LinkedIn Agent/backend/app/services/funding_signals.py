"""
Funding Signals — Google News RSS (free, no API key needed).
Catches funding rounds, hiring pushes, and job posting spikes.
"""

import feedparser
import httpx
from datetime import datetime, timedelta


async def get_company_signals(company_name: str) -> dict:
    """
    Scan multiple signal sources for a company. Returns the highest-scoring signal.
    Signal types: funding, hiring_push, job_posting_spike.
    """
    if not company_name:
        return {"type": "none", "detail": "", "score": 0}

    signals = []

    funding = await _check_funding_news(company_name)
    if funding:
        signals.append({"type": "funding", "detail": funding, "score": 85})

    hiring = await _check_hiring_news(company_name)
    if hiring:
        signals.append({"type": "hiring_push", "detail": hiring, "score": 70})

    job_count = await _count_recent_jobs(company_name)
    if job_count >= 3:
        signals.append({
            "type": "job_posting_spike",
            "detail": f"{job_count} new relevant roles posted recently",
            "score": 65,
        })

    if not signals:
        return {"type": "none", "detail": "", "score": 0}

    return max(signals, key=lambda s: s["score"])


async def _check_funding_news(company: str) -> str | None:
    """Search Google News RSS for funding announcements."""
    queries = [
        f'"{company}" funding raised series',
        f'"{company}" investment million billion',
    ]
    cutoff = datetime.now() - timedelta(days=90)

    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                if not hasattr(entry, "published_parsed") or not entry.published_parsed:
                    continue
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date < cutoff:
                    continue
                title = entry.title.lower()
                if any(
                    kw in title
                    for kw in ["raises", "raised", "funding", "series", "million", "billion"]
                ):
                    return entry.title
        except Exception:
            continue
    return None


async def _check_hiring_news(company: str) -> str | None:
    """Search Google News RSS for hiring/expansion announcements."""
    query = f'"{company}" hiring expanding team growth 2025 OR 2026'
    url = f"https://news.google.com/rss/search?q={query}&hl=en"
    try:
        feed = feedparser.parse(url)
        cutoff = datetime.now() - timedelta(days=60)
        for entry in feed.entries[:5]:
            if not hasattr(entry, "published_parsed") or not entry.published_parsed:
                continue
            pub_date = datetime(*entry.published_parsed[:6])
            if pub_date > cutoff:
                return entry.title
    except Exception:
        pass
    return None


async def _count_recent_jobs(company: str) -> int:
    """Count recent job postings on LinkedIn (public, no login)."""
    try:
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={company.replace(' ', '%20')}&f_TPR=r604800"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0"
                },
                follow_redirects=True,
                timeout=15,
            )
            return min(resp.text.count("job-search-card"), 20)
    except Exception:
        return 0
