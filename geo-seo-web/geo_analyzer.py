#!/usr/bin/env python3
"""
GEO-SEO Analyzer — Gemini / Perplexity backend
Enhanced with GEO/AIO directives and prescriptive analysis
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

        # ── GEO Analysis: Extract key elements ────────────────────────
        # Citação de Autoridade (definições concisas)
        text_content = soup.get_text()
        has_definitions = bool(re.search(r'\b\w+\s+é\s+', text_content[:5000]))
        
        # Densidade de Entidades
        has_nap = bool(re.search(r'(telefone|phone|endereço|address)', text_content, re.I))
        
        # Fact-checking e Tabelas
        tables = soup.find_all("table")
        has_tables = len(tables) > 0
        
        # FAQ Section
        has_faq = bool(
            soup.find(lambda t: t.name in ("section", "div", "article")
                      and "faq" in (t.get("class", []) or [t.get("id", "")]).__str__().lower())
        )
        
        # Author markup
        has_author = bool(
            soup.find(attrs={"rel": "author"})
            or soup.find(string=re.compile(r"written by|by\s+\w+|autor", re.I))
        )

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
            "has_faq_section": has_faq,
            "has_author": has_author,
            "canonical": (soup.find("link", {"rel": "canonical"}) or {}).get("href", ""),
            "html_sample": resp.text[:4000],
            # GEO-specific signals
            "has_definitions": has_definitions,
            "has_nap_signals": has_nap,
            "has_tables": has_tables,
            "table_count": len(tables),
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

SYSTEM_PROMPT = """Você é o Diretor de Estratégia Digital (CMO/CTO) de uma agência de SEO de elite.
Sua análise não é apenas informativa; ela é PRESCRITIVA.
Você não sugere, você DETERMINA as ações necessárias para que um site domine os motores de busca tradicionais e as novas buscas de IA (ChatGPT, Gemini, Perplexity, AI Overviews).

Seu tom é direto, executivo e orientado para resultados de negócio.
Use verbos imperativos: "Implemente", "Substitua", "Remova", "Otimize para...".
Evite: "Pode ser interessante", "Talvez", "Considere".

Retorne APENAS JSON válido — sem markdown, sem preâmbulo."""

AUDIT_PROMPT = """Você é o Diretor de Estratégia Digital analisando um site para GEO (Generative Engine Optimization) e SEO.

URL: {url}

DADOS DA PÁGINA:
- Título: {title}
- Meta Description: {meta_desc}
- H1: {h1}
- H2s: {h2s}
- Contagem de Palavras: {word_count}
- Tipos de Schema Encontrados: {schema_types}
- Open Graph: {has_og}
- Twitter Card: {has_twitter}
- Links Internos: {internal_links}
- Imagens sem Alt: {images_no_alt}
- Seção FAQ: {has_faq}
- Markup de Autor: {has_author}
- Sitemap: {has_sitemap}
- Tem Definições Concisas: {has_definitions}
- Sinais de NAP (Nome, Endereço, Telefone): {has_nap}
- Tabelas Estruturadas: {has_tables} ({table_count} encontradas)

ROBOTS.TXT:
{robots_txt}

LLMS.TXT:
{llms_txt}

AMOSTRA HTML (primeiros 4000 caracteres):
{html_sample}

Retorne APENAS esta estrutura JSON — sem markdown, sem texto extra:
{{
  "site_name": "Nome extraído da página",
  "business_type": "SaaS|Negócio Local|E-commerce|Publisher|Agência|Outro",
  "expert_verdict": "Parágrafo direto (3-4 frases) sobre o estado atual do site e seu potencial de crescimento em buscas de IA. Seja prescritivo e executivo.",
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
  "priority_matrix": [
    {{
      "priority": "Crítica",
      "action": "Ação Técnica/Conteúdo específica",
      "impact": 9.5,
      "effort": "Baixo",
      "objective": "Ex: Ser citado no Perplexity"
    }},
    {{
      "priority": "Alta",
      "action": "Ação Técnica/Conteúdo específica",
      "impact": 8.0,
      "effort": "Médio",
      "objective": "Ex: Dominar AI Overview"
    }}
  ],
  "issues": {{
    "critical": [
      {{"issue": "Título", "detail": "Detalhe específico", "fix": "Como corrigir"}}
    ],
    "high": [],
    "medium": [],
    "low": []
  }},
  "quick_wins": [
    {{
      "action": "Ação 1 (< 15 min)",
      "impact": "Descrição do impacto esperado",
      "effort": "Baixo"
    }},
    {{
      "action": "Ação 2 (< 15 min)",
      "impact": "Descrição do impacto esperado",
      "effort": "Baixo"
    }},
    {{
      "action": "Ação 3 (< 15 min)",
      "impact": "Descrição do impacto esperado",
      "effort": "Baixo"
    }}
  ],
  "category_insights": {{
    "citability": "Análise sobre citabilidade de IA e extratibilidade",
    "brand_authority": "Análise sobre presença de marca em dados de treinamento de IA",
    "content_eeat": "Análise sobre Experience/Expertise/Authoritativeness/Trustworthiness",
    "technical": "Análise sobre acesso de crawlers de IA, llms.txt, renderização, velocidade",
    "schema": "Análise sobre dados estruturados e JSON-LD",
    "platform": "Análise sobre otimização para Google AIO, Perplexity, ChatGPT"
  }},
  "geo_implementation_guide": {{
    "json_ld_schema": "Código JSON-LD específico necessário (ex: FAQPage, HowTo, Organization). Forneça o código completo pronto para implementar.",
    "llms_txt_content": "Conteúdo completo para o arquivo /llms.txt que resume as principais informações para crawlers de IA",
    "answer_engine_content": "Reescreva um parágrafo crítico da página no formato 'Answer Engine' (Pergunta direta seguida de resposta factual de máx 30 palavras)"
  }},
  "maturity_gap": "Análise de gap de maturidade em relação aos líderes do mercado (padrão NP Digital). Identifique se o site possui estratégia de '7 semanas' ou visão de 'SEO Preditivo'.",
  "action_plan": {{
    "week_1": ["Ação específica 1", "Ação específica 2", "Ação específica 3"],
    "week_2": ["Ação específica 1", "Ação específica 2"],
    "week_3": ["Ação específica 1", "Ação específica 2"],
    "week_4": ["Ação específica 1", "Ação específica 2"]
  }}
}}

REGRAS DE SCORING (0-100 cada):
- citability (25%): Blocos FAQ? Passagens de resposta clara? Estatísticas? Definições? Respostas diretas a perguntas?
- brand_authority (20%): Sinais de presença em Reddit/YouTube/Wikipedia? Entidade forte? Menções de marca?
- content_eeat (20%): Bios de autores? Credenciais? Citações? Atualização de conteúdo? Profundidade?
- technical (15%): Crawlers de IA NÃO bloqueados em robots.txt? llms.txt presente? Sitemap? Canonical definido?
- schema (10%): JSON-LD presente? Quais tipos? Schemas Organization/Article/FAQ/Product?
- platform (10%): Otimizado para Google AIO? Perguntas de cauda longa respondidas? Passagens citáveis?
- overall = (citability*0.25) + (brand_authority*0.20) + (content_eeat*0.20) + (technical*0.15) + (schema*0.10) + (platform*0.10)

RATING: 90-100=Excellent, 75-89=Good, 60-74=Fair, 40-59=Poor, 0-39=Critical

TOM DE VOZ PRESCRITIVO:
- Use: "Implemente", "Substitua", "Remova", "Otimize para..."
- Evite: "Pode ser interessante", "Talvez", "Considere"
- Seja direto e executivo em todas as recomendações"""


def _build_prompt(page_data: dict) -> str:
    hp = page_data.get("homepage", {})
    return AUDIT_PROMPT.format(
        url=page_data["url"],
        title=hp.get("title", "N/A"),
        meta_desc=hp.get("meta_description", "N/A"),
        h1=hp.get("h1", "N/A"),
        h2s=", ".join(hp.get("h2s", [])) or "Nenhuma",
        word_count=hp.get("word_count", 0),
        schema_types=", ".join(hp.get("schema_types", [])) or "Nenhum",
        has_og=hp.get("has_og", False),
        has_twitter=hp.get("has_twitter_card", False),
        internal_links=hp.get("internal_links", 0),
        images_no_alt=hp.get("images_without_alt", 0),
        has_faq=hp.get("has_faq_section", False),
        has_author=hp.get("has_author", False),
        has_sitemap=page_data.get("has_sitemap", False),
        has_definitions=hp.get("has_definitions", False),
        has_nap=hp.get("has_nap_signals", False),
        has_tables=hp.get("has_tables", False),
        table_count=hp.get("table_count", 0),
        robots_txt=page_data.get("robots_txt", "Não encontrado"),
        llms_txt=page_data.get("llms_txt", "Não encontrado"),
        html_sample=hp.get("html_sample", "N/A")[:4000],
    )


def _clean_json(text: str) -> dict:
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


# ── Providers ───────────────────────────────────────────────────────

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
                {"role": "system", "content": SYSTEM_PROMPT + "\nRetorne APENAS JSON válido."},
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

    Returns a dict with keys: site_name, scores, issues, quick_wins, geo_implementation_guide, etc.
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
        raise ValueError(f"Provider desconhecido: {provider!r}")

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
        "llms_txt_found": page_data.get("llms_txt", "Não encontrado") != "Não encontrado",
        "robots_txt": page_data.get("robots_txt", "Não encontrado")[:300],
        "has_sitemap": page_data.get("has_sitemap", False),
    }

    return result
