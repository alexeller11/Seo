# GEO-SEO Auditor 🤖

Ferramenta de auditoria GEO+SEO que roda na web, usando **Gemini** (grátis) ou **Perplexity** como motor de IA.  
Deploy em 1 clique no **Railway**.

---

## O que analisa

| Categoria | Peso | O que mede |
|---|---|---|
| AI Citability | 25% | Quão citável é o conteúdo para IAs (FAQ, definições, estatísticas) |
| Brand Authority | 20% | Presença de marca em fontes treinadas pelas IAs |
| Content E-E-A-T | 20% | Experiência, Expertise, Autoridade, Confiabilidade |
| Technical GEO | 15% | robots.txt, llms.txt, sitemap, crawlers de IA |
| Schema Markup | 10% | JSON-LD, tipos de schema, completude |
| Platform Optim. | 10% | Google AIO, ChatGPT Browse, Perplexity Citations |

---

## Deploy no Railway (recomendado)

### 1. Faça fork ou clone este repositório no GitHub

### 2. Crie um projeto no Railway
- Acesse [railway.app](https://railway.app)
- New Project → Deploy from GitHub repo → selecione este repositório

### 3. Configure as variáveis de ambiente
No painel do Railway → **Variables**:

```
GEMINI_API_KEY=AIzaSy...          # Obtenha grátis em aistudio.google.com
SECRET_KEY=sua-chave-aleatoria    # Qualquer string longa aleatória
PORT=5000                          # Railway define automaticamente
```

### 4. Deploy automático ✅

O Railway detecta o `Procfile` e `requirements.txt` automaticamente.

---

## Rodando localmente

```bash
# Clone
git clone https://github.com/seu-usuario/geo-seo-web
cd geo-seo-web

# Instale dependências
pip install -r requirements.txt

# Configure variáveis
cp .env.example .env
# edite .env e adicione sua GEMINI_API_KEY

# Rode
python app.py
# Acesse: http://localhost:5000
```

---

## Obtendo a Gemini API Key (GRÁTIS)

1. Acesse [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave (começa com `AIzaSy...`)

**Limites gratuitos:** 15 req/min, 1.000.000 tokens/min — mais que suficiente.

---

## Estrutura do projeto

```
geo-seo-web/
├── app.py              # Flask app (rotas, background threads)
├── geo_analyzer.py     # Fetch de página + análise com IA
├── templates/
│   ├── base.html       # Layout base (nav, CSS)
│   ├── index.html      # Página inicial com formulário
│   ├── results.html    # Resultados da auditoria
│   └── history.html    # Histórico de auditorias
├── requirements.txt
├── Procfile            # Para Railway/Heroku
├── railway.toml        # Config Railway
└── .env.example        # Variáveis de exemplo
```

---

## Baseado em

[geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) — skill original para Claude Code,  
adaptado para rodar como web app independente com Gemini/Perplexity.
