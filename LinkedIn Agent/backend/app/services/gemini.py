"""
Gemini 1.5 Flash — AI message generation.
Free tier: 1,500 requests/day, 1M tokens/minute.
Get your key: https://aistudio.google.com (no credit card)
"""

import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

# Configure once at module level
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.85,
                "top_p": 0.95,
                "max_output_tokens": 1500,
            },
        )
    return _model


SYSTEM_INSTRUCTION = """
You are writing LinkedIn outreach messages for {user_name}.
Write in first person AS {user_name}. These are their words, not yours.

HARD RULES:
- NEVER open with: "I came across your profile", "I hope this finds you well",
  "I wanted to reach out", "I noticed", "I recently came across"
- ALWAYS reference something SPECIFIC: a post they wrote, a company announcement,
  a specific project, a recent hire, or a funding round
- Connection note: MAX 290 characters. No em-dashes. No exclamation marks.
- Sound like a thoughtful senior professional. Never like a marketer.
- ONE ask only. Never ask multiple questions.
- Short paragraphs. Real sentences.
- Never use: "synergy", "leverage", "touch base", "circle back"
"""


async def generate_outreach_messages(
    user_name: str,
    target_role: str,
    relevant_resume_chunks: list[str],
    recipient_name: str,
    recipient_title: str,
    company_name: str,
    recent_posts: list[str],
    company_news: str,
    signal_type: str,
    signal_detail: str,
    job_title: str = "",
) -> dict:
    """Generate all 5 outreach messages in a single Gemini call."""

    context_prompt = f"""
=== WHO I AM ===
Name: {user_name}
Applying for: {target_role}
My most relevant experience for this company:
{chr(10).join(f'- {chunk}' for chunk in relevant_resume_chunks)}

=== WHO I AM WRITING TO ===
Name: {recipient_name}
Title: {recipient_title} at {company_name}
Their most recent post: "{recent_posts[0] if recent_posts else 'No recent posts found'}"
Another post: "{recent_posts[1] if len(recent_posts) > 1 else ''}"

=== COMPANY CONTEXT ===
{company_name} recent news: {company_news}
Currently hiring for: {job_title if job_title else 'general interest'}
Why reaching out now: {signal_type} — {signal_detail}

=== GENERATE EXACTLY THESE 5 SECTIONS ===

CONNECTION_NOTE:
(Max 290 characters. Reference their post or company news.)

MESSAGE_DAY9:
(Max 900 characters. 3 short paragraphs.
Para 1: Specific reference to them or their company.
Para 2: Your relevant experience briefly.
Para 3: One clear easy ask.)

MESSAGE_DAY14:
(Max 400 characters. Different angle. Add value. Never say "just following up".)

EMAIL_SUBJECT:
(Max 55 characters. Specific, not generic.)

EMAIL_BODY:
(Max 180 words. Different angle again. More formal.)
"""

    full_prompt = (
        SYSTEM_INSTRUCTION.replace("{user_name}", user_name)
        + "\n\n"
        + context_prompt
    )
    model = _get_model()
    response = model.generate_content(full_prompt)
    return parse_message_sections(response.text)


def parse_message_sections(raw: str) -> dict:
    """Parse Gemini's response into labeled message sections."""
    sections = {}
    labels = [
        "CONNECTION_NOTE",
        "MESSAGE_DAY9",
        "MESSAGE_DAY14",
        "EMAIL_SUBJECT",
        "EMAIL_BODY",
    ]
    for i, label in enumerate(labels):
        start = raw.find(f"{label}:")
        if start == -1:
            sections[label.lower()] = ""
            continue
        start += len(label) + 1
        end = (
            raw.find(f"{labels[i + 1]}:", start)
            if i + 1 < len(labels)
            else len(raw)
        )
        sections[label.lower()] = raw[start:end].strip()
    return sections
