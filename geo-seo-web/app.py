#!/usr/bin/env python3
"""
GEO-SEO Web App — Flask + Gemini/Perplexity
Deploy on Railway with one click.
"""

import ipaddress
import json
import os
import socket
import threading
import uuid
from collections import deque
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# In-memory audit store (max 50 recent audits)
_audits: dict[str, dict] = {}
_audit_order: deque = deque(maxlen=50)

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
DEFAULT_PERPLEXITY_KEY = os.environ.get("PERPLEXITY_API_KEY", "")


# ── Helpers ─────────────────────────────────────────────────────────────

def _is_safe_url(url: str) -> bool:
    """Valida URL para prevenir SSRF — bloqueia IPs privados/locais."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except (socket.gaierror, ValueError):
            pass
        return True
    except Exception:
        return False


def _store_audit(audit_id: str, data: dict):
    _audits[audit_id] = data
    if audit_id not in _audit_order:
        _audit_order.appendleft(audit_id)
    # Trim old entries
    while len(_audit_order) > 50:
        old = _audit_order.pop()
        _audits.pop(old, None)


def _run_audit_bg(audit_id: str, url: str, api_key: str, provider: str):
    """Background thread: run audit and update store."""
    from geo_analyzer import run_audit

    try:
        result = run_audit(url, api_key, provider)
        _audits[audit_id].update({"status": "done", "result": result})
    except Exception as exc:
        _audits[audit_id].update({"status": "error", "error": str(exc)})


# ── Routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    recent = [
        {"id": aid, **_audits[aid]}
        for aid in list(_audit_order)[:8]
        if aid in _audits
    ]
    return render_template("index.html", recent=recent,
                           has_gemini_key=bool(DEFAULT_GEMINI_KEY),
                           has_perplexity_key=bool(DEFAULT_PERPLEXITY_KEY))


@app.route("/audit", methods=["POST"])
def start_audit():
    url = request.form.get("url", "").strip()
    provider = request.form.get("provider", "gemini")

    # API key: form field takes priority, then env var
    if provider == "gemini":
        api_key = request.form.get("api_key", "").strip() or DEFAULT_GEMINI_KEY
    else:
        api_key = request.form.get("api_key", "").strip() or DEFAULT_PERPLEXITY_KEY

    if not url:
        return redirect(url_for("index"))

    # Validar URL para prevenir SSRF
    if not _is_safe_url(url):
        return render_template(
            "index.html",
            error="URL inválida ou não permitida. Use uma URL pública com http:// ou https://.",
            recent=[],
            has_gemini_key=bool(DEFAULT_GEMINI_KEY),
            has_perplexity_key=bool(DEFAULT_PERPLEXITY_KEY),
        )

    if not api_key:
        return render_template(
            "index.html",
            error=f"Por favor, insira sua {provider.title()} API key.",
            recent=[],
            has_gemini_key=False,
            has_perplexity_key=False,
        )

    audit_id = uuid.uuid4().hex[:10]
    _store_audit(audit_id, {
        "status": "running",
        "url": url,
        "provider": provider,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    t = threading.Thread(
        target=_run_audit_bg,
        args=(audit_id, url, api_key, provider),
        daemon=True,
    )
    t.start()

    return redirect(url_for("results", audit_id=audit_id))


@app.route("/results/<audit_id>")
def results(audit_id: str):
    audit = _audits.get(audit_id)
    if not audit:
        return redirect(url_for("index"))
    return render_template("results.html", audit_id=audit_id, audit=audit)


@app.route("/api/status/<audit_id>")
def api_status(audit_id: str):
    audit = _audits.get(audit_id)
    if not audit:
        return jsonify({"status": "not_found"}), 404
    return jsonify(audit)


@app.route("/history")
def history():
    recent = [
        {"id": aid, **_audits[aid]}
        for aid in list(_audit_order)
        if aid in _audits
    ]
    return render_template("history.html", audits=recent)


# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
