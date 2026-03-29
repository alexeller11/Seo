#!/usr/bin/env python3
"""
GEO-SEO Analyzer — Gemini / Perplexity backend
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# ── Page Fetcher ────────────────────────────────────────────────────────

def fetch_page_data(url: str) -> dict:
    """Fetch and extract comprehensive page data for GEO analysis."""
    data = {
        "url": url,
        "homepage": {},
        "robots_txt": "Not found",
        "llms_txt": "Not found",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; GEOAuditBot/1.0; "
            "+https://github.com/zubair-trabzada/geo-seo-claude)"
        )
    }

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # ── Homepage ────────────────────────────────────────────────────────
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title = soup.find("title")
        meta_desc = soup.find("meta", {"name": "description"})
        h1 = soup.find("h1")

        # Schema markup
        schema_types = []
        for s in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                sd = json.loads(s.string or "")
                if isinstance(sd, list):
                    schema_types.extend(x.get("@type", "") for x in sd if isinstance(x, dict))
                else:
                    t = sd.get("@type", "")
                    if t:
                        schema_types.append(t)
            except Exception:
                pass

        # Internal links
        base_domain = parsed.netloc
        links = soup.find_all("a", href=True)
        internal = sum(
            1 for l in links
            if urlparse(urljoin(url, l["href"])).netloc == base_domain
        )

        imgs = soup.find_all("img")
        imgs_no_alt = sum(1 for i in imgs if not i.get("alt", "").strip())

        data["homepage"] = {
            "title": title.get_text(strip=True) if title else "",
            "meta_description": meta_desc.get("content", "") if meta_desc else "",
            "h1": h1.get_text(strip=True) if h1 else "",
            "h2s": [h.get_text(strip=True) for h in soup.find_all("h2")[:10]],
            "h3s": [h.get_text(strip=True) for h in soup.find_all("h3")[:5]],
            "word_count": len(re.sub(r"\s+", " ", soup.get_text()).split()),
            "schema_types": [t for t in schema_types if t],
            "has_og": bool(soup.find("meta", {"property": "og:title"})),
            "has_twitter_card": bool(soup.find("meta", {"name": "twitter:card"})),
            "internal_links": internal,
            "total_links": len(links),
            "images": len(imgs),
            "images_without_alt": imgs_no_alt,
            "has_faq_section": bool(
                soup.find(lambda t: t.name in ("section", "div", "article")
                          and "faq" in (t.get("class", []) or [t.get("id", "")]).__str__().lower())
            ),
            "has_author": bool(
                soup.find(attrs={"rel": "author"})
                or soup.find(string=re.compile(r"written by|by\s+\w+", re.I))
            ),
            "canonical": (soup.find("link", {"rel": "canonical"}) or {}).get("href", ""),
            "html_sample": resp.text[:4000],
        }
    except Exception as e:
        data["fetch_error"] = str(e)
        data["homepage"] = {}

    # ── robots.txt ──────────────────────────────────────────────────────
    try:
        r = requests.get(f"{base_url}/robots.txt", headers=headers, timeout=8)
        if r.status_code == 200:
            data["robots_txt"] = r.text[:2500]
    except Exception:
        pass

    # ── llms.txt ────────────────────────────────────────────────────────
    try:
        r = requests.get(f"{base_url}/llms.txt", headers=headers, timeout=8)
        if r.status_code == 200:
            data["llms_txt"] = r.text[:1500]
    except Exception:
        pass

    # ── sitemap presence ────────────────────────────────────────────────
    try:
        r = requests.get(f"{base_url}/sitemap.xml", headers=headers, timeout=8)
        data["has_sitemap"] = r.status_code == 200
    except Exception:
        data["has_sitemap"] = False

    return data


# ── Prompt Builder ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a world-class GEO (Generative Engine Optimization) consultant.
GEO optimizes websites to be discovered, cited, and recommended by AI systems
(ChatGPT, Perplexity, Gemini, Google AI Overviews, Bing Copilot).

You analyze websites and return ONLY valid JSON — no markdown, no preamble."""

AUDIT_PROMPT = """Analyze this website and return a GEO+SEO audit as a valid JSON object.

URL: {url}

PAGE DATA:
- Title: {title}
- Meta Description: {meta_desc}
- H1: {h1}
- H2s: {h2s}
- Word Count: {word_count}
- Schema Types Found: {schema_types}
- Has Open Graph: {has_og}
- Has Twitter Card: {has_twitter}
- Internal Links: {internal_links}
- Images Without Alt: {images_no_alt}
- Has FAQ Section: {has_faq}
- Has Author Markup: {has_author}
- Has Sitemap: {has_sitemap}

ROBOTS.TXT:
{robots_txt}

LLMS.TXT:
{llms_txt}

HTML SAMPLE (first 4000 chars):
{html_sample}

Return ONLY this JSON structure — no markdown fences, no extra text:
{{
  "site_name": "Name extracted from page",
  "business_type": "SaaS|Local Business|E-commerce|Publisher|Agency|Other",
  "summary": "2-3 sentence executive summary of the site's GEO health",
  "scores": {{
    "overall": 0,
    "citability": 0,
    "brand_authority": 0,
    "content_eeat": 0,
    "technical": 0,
    "schema": 0,
    "platform": 0
  }},
  "rating": "Excellent|Good|Fair|Poor|Critical",
  "issues": {{
    "critical": [
      {{"issue": "Title", "detail": "Specific detail", "fix": "How to fix"}}
    ],
    "high": [],
    "medium": [],
    "low": []
  }},
  "quick_wins": [
    {{"action": "Action title", "impact": "Expected impact description", "effort": "Low|Medium"}}
  ],
  "category_insights": {{
    "citability": "Insight about AI citability and extractability",
    "brand_authority": "Insight about brand presence across AI training data sources",
    "content_eeat": "Insight about Experience/Expertise/Authoritativeness/Trustworthiness",
    "technical": "Insight about AI crawler access, llms.txt, rendering, speed",
    "schema": "Insight about structured data and JSON-LD",
    "platform": "Insight about optimization for Google AIO, Perplexity, ChatGPT"
  }},
  "action_plan": {{
    "week_1": ["Specific action 1", "Specific action 2", "Specific action 3"],
    "week_2": ["Specific action 1", "Specific action 2"],
    "week_3": ["Specific action 1", "Specific action 2"],
    "week_4": ["Specific action 1", "Specific action 2"]
  }}
}}

SCORING RULES (0-100 each):
- citability (25% weight): FAQ blocks? Clear answer passages? Statistics? Definitions? Direct answers to questions?
- brand_authority (20% weight): Reddit/YouTube/Wikipedia presence signals? Strong entity? Brand mentions?
- content_eeat (20% weight): Author bios? Credentials? Citations? Content freshness? Depth?
- technical (15% weight): AI crawlers NOT blocked in robots.txt? llms.txt present? Has sitemap? Canonical set?
- schema (10% weight): JSON-LD present? What types? Organization/Article/FAQ/Product schemas?
- platform (10% weight): Optimized for Google AIO? Long-tail questions answered? Citable passages?
- overall = (citability*0.25) + (brand_authority*0.20) + (content_eeat*0.20) + (technical*0.15) + (schema*0.10) + (platform*0.10)

RATING: 90-100=Excellent, 75-89=Good, 60-74=Fair, 40-59=Poor, 0-39=Critical"""


def _build_prompt(page_data: dict) -> str:
    hp = page_data.get("homepage", {})
    return AUDIT_PROMPT.format(
        url=page_data["url"],
        title=hp.get("title", "N/A"),
        meta_desc=hp.get("meta_description", "N/A"),
        h1=hp.get("h1", "N/A"),
        h2s=", ".join(hp.get("h2s", [])) or "None",
        word_count=hp.get("word_count", 0),
        schema_types=", ".join(hp.get("schema_types", [])) or "None",
        has_og=hp.get("has_og", False),
        has_twitter=hp.get("has_twitter_card", False),
        internal_links=hp.get("internal_links", 0),
        images_no_alt=hp.get("images_without_alt", 0),
        has_faq=hp.get("has_faq_section", False),
        has_author=hp.get("has_author", False),
        has_sitemap=page_data.get("has_sitemap", False),
        robots_txt=page_data.get("robots_txt", "Not found"),
        llms_txt=page_data.get("llms_txt", "Not found"),
        html_sample=hp.get("html_sample", "N/A")[:4000],
    )


def _clean_json(text: str) -> dict:
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


# ── Providers ───────────────────────────────────────────────────────────

def _run_gemini(prompt: str, api_key: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    resp = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            max_output_tokens=4096,
        ),
    )
    return _clean_json(resp.text)


def _run_perplexity(prompt: str, api_key: str) -> dict:
    import httpx

    resp = httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT + "\nReturn ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 4096,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    return _clean_json(text)


# ── Public API ──────────────────────────────────────────────────────────

def run_audit(url: str, api_key: str, provider: str = "gemini") -> dict:
    """
    Run a full GEO+SEO audit on *url* using the specified AI provider.

    Returns a dict with keys: site_name, scores, issues, quick_wins, etc.
    Raises on error.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    page_data = fetch_page_data(url)
    prompt = _build_prompt(page_data)

    if provider == "gemini":
        result = _run_gemini(prompt, api_key)
    elif provider == "perplexity":
        result = _run_perplexity(prompt, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider!r}")

    # Ensure overall score is calculated correctly
    s = result.get("scores", {})
    if s:
        calculated = round(
            s.get("citability", 0) * 0.25
            + s.get("brand_authority", 0) * 0.20
            + s.get("content_eeat", 0) * 0.20
            + s.get("technical", 0) * 0.15
            + s.get("schema", 0) * 0.10
            + s.get("platform", 0) * 0.10
        )
        result["scores"]["overall"] = calculated

    result["_meta"] = {
        "url": url,
        "provider": provider,
        "llms_txt_found": page_data.get("llms_txt", "Not found") != "Not found",
        "robots_txt": page_data.get("robots_txt", "Not found")[:300],
        "has_sitemap": page_data.get("has_sitemap", False),
    }

    return result
