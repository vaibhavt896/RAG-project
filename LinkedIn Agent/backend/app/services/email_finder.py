"""
Email Finder — waterfall: Apollo → Hunter → Skrapp → SMTP permutation.
Stacks free tiers: 50 + 25 + 150 = 225+ lookups/month at zero cost.
"""

import requests
import smtplib
import dns.resolver
from app.config import get_settings

settings = get_settings()


async def find_email(
    first_name: str, last_name: str, company_domain: str
) -> str | None:
    """
    Waterfall email finder. Tries each service in order,
    falls back to SMTP-verified permutation.
    Returns the first verified email, or None.
    """
    email = _try_apollo(first_name, last_name, company_domain)
    if email:
        return email

    email = _try_hunter(first_name, last_name, company_domain)
    if email:
        return email

    email = _try_skrapp(first_name, last_name, company_domain)
    if email:
        return email

    return _permutation_verify(first_name, last_name, company_domain)


def _try_apollo(first: str, last: str, domain: str) -> str | None:
    """Apollo.io — 50 lookups/month free."""
    if not settings.apollo_api_key:
        return None
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/people/match",
            headers={
                "x-api-key": settings.apollo_api_key,
                "Content-Type": "application/json",
            },
            json={"first_name": first, "last_name": last, "domain": domain},
            timeout=10,
        )
        email = resp.json().get("person", {}).get("email")
        if email and "@" in email and not email.startswith("email_"):
            return email
    except Exception:
        pass
    return None


def _try_hunter(first: str, last: str, domain: str) -> str | None:
    """Hunter.io — 25 lookups/month free."""
    if not settings.hunter_api_key:
        return None
    try:
        resp = requests.get(
            "https://api.hunter.io/v2/email-finder",
            params={
                "domain": domain,
                "first_name": first,
                "last_name": last,
                "api_key": settings.hunter_api_key,
            },
            timeout=10,
        )
        data = resp.json().get("data", {})
        email = data.get("email")
        if email and data.get("score", 0) >= 60:
            return email
    except Exception:
        pass
    return None


def _try_skrapp(first: str, last: str, domain: str) -> str | None:
    """Skrapp.io — 150 lookups/month free."""
    if not settings.skrapp_api_key:
        return None
    try:
        resp = requests.post(
            "https://api.skrapp.io/api/v2/find",
            headers={
                "X-Access-Key": settings.skrapp_api_key,
                "Content-Type": "application/json",
            },
            json={"firstName": first, "lastName": last, "domain": domain},
            timeout=10,
        )
        email = resp.json().get("email")
        if email and "@" in email:
            return email
    except Exception:
        pass
    return None


def _permutation_verify(first: str, last: str, domain: str) -> str | None:
    """Generate common email patterns and verify via SMTP. Zero cost."""
    f, l = first.lower(), last.lower()
    candidates = [
        f"{f}.{l}@{domain}",
        f"{f}{l}@{domain}",
        f"{f[0]}{l}@{domain}",
        f"{f}@{domain}",
        f"{f}_{l}@{domain}",
        f"{f[0]}.{l}@{domain}",
    ]
    for email in candidates:
        if _smtp_verify(email, domain):
            return email
    return None


def _smtp_verify(email: str, domain: str) -> bool:
    """
    SMTP verification — checks if mailbox exists without sending email.
    Returns True if address likely valid.
    """
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_host = str(
            sorted(mx_records, key=lambda r: r.preference)[0].exchange
        )
        with smtplib.SMTP(timeout=10) as smtp:
            smtp.connect(mx_host, 25)
            smtp.helo("verify.com")
            smtp.mail("check@verify.com")
            code, _ = smtp.rcpt(email)
            return code == 250
    except Exception:
        return False
