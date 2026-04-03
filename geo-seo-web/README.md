# GEO-SEO Auditor 🤖 — Generative Engine Optimization

Ferramenta de auditoria **GEO/AIO** (Generative Engine Optimization / AI Overviews) que roda na web, usando **Gemini** (grátis) ou **Perplexity** como motor de IA.  
Deploy em 1 clique no **Railway**.

---

## O que é GEO/AIO?

**GEO (Generative Engine Optimization)** é a otimização de sites para serem descobertos, citados e recomendados por sistemas de IA como ChatGPT, Perplexity, Gemini e Google AI Overviews. Este auditor fornece análise **prescritiva** (não apenas informativa) com ações diretas para dominar essas novas buscas.

---

## Análise Prescritiva

Este auditor segue a **Diretriz Mestra de Auditoria SEO de Próxima Geração** e fornece:

### 1. **Veredito do Especialista** 🎯
Resumo executivo direto sobre o estado atual do site e seu potencial de crescimento em buscas de IA.

### 2. **Matriz de Prioridade** 📊
Tabela estruturada com:
- **Prioridade** (Crítica, Alta, Média, Baixa)
- **Ação Recomendada** (específica e prescritiva)
- **Impacto** (0-10)
- **Esforço** (Baixo, Médio, Alto)
- **Objetivo Técnico** (ex: "Ser citado no Perplexity")

### 3. **Quick Wins (< 15 min)** ⚡
3 ações que podem ser implementadas em menos de 15 minutos com impacto imediato.

### 4. **Guia de Implementação GEO/AIO** 🔧
- **JSON-LD pronto para copiar** (FAQPage, HowTo, Organization)
- **Conteúdo para /llms.txt** (arquivo que guia crawlers de IA)
- **Conteúdo no formato "Answer Engine"** (pergunta + resposta factual)

### 5. **Gap de Maturidade** 📈
Benchmark contra padrão **NP Digital** — identifique lacunas em relação aos líderes do mercado.

### 6. **Plano de 30 Dias** 📅
Roadmap semanal estruturado para dominar AI Overviews.

---

## Pilares de Análise GEO

| Categoria | Peso | O que mede |
|---|---|---|
| **AI Citability** | 25% | Definições concisas, FAQ, estatísticas, passagens diretas |
| **Brand Authority** | 20% | Presença em Reddit/YouTube/Wikipedia, sinais de entidade forte |
| **Content E-E-A-T** | 20% | Experiência, Expertise, Autoridade, Confiabilidade |
| **Technical GEO** | 15% | robots.txt, llms.txt, sitemap, acesso de crawlers de IA |
| **Schema Markup** | 10% | JSON-LD, tipos de schema, completude estruturada |
| **Platform Optim.** | 10% | Google AIO, ChatGPT Browse, Perplexity Citations |

---

## Tom de Voz Prescritivo

O auditor **não sugere**, ele **determina** as ações necessárias:

✅ **Use:** "Implemente", "Substitua", "Remova", "Otimize para..."  
❌ **Evite:** "Pode ser interessante", "Talvez", "Considere"

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
├── geo_analyzer.py     # Fetch de página + análise prescritiva com IA
├── templates/
│   ├── base.html       # Layout base (nav, CSS, design system)
│   ├── index.html      # Página inicial com formulário
│   ├── results.html    # Resultados com veredito, matriz, guia GEO
│   └── history.html    # Histórico de auditorias
├── requirements.txt
├── Procfile            # Para Railway/Heroku
├── railway.toml        # Config Railway
└── .env.example        # Variáveis de exemplo
```

---

## Análise Detalhada por Categoria

### 🤖 AI Citability (25%)
- Existem definições concisas (máx. 30 palavras) no formato "[Termo] é..."?
- Há blocos FAQ estruturados?
- Contém estatísticas e dados proprietários?
- Existem tabelas comparativas?

### 🏷️ Brand Authority (20%)
- Sinais de presença em Reddit, YouTube, Wikipedia?
- Entidade forte e consistente (NAP)?
- Menções de marca em fontes de alta autoridade?

### ✍️ Content E-E-A-T (20%)
- Bios de autores com credenciais?
- Citações e links para fontes externas?
- Conteúdo atualizado regularmente?
- Profundidade e originalidade?

### ⚙️ Technical GEO (15%)
- Crawlers de IA bloqueados em robots.txt?
- Arquivo llms.txt presente?
- Sitemap.xml acessível?
- Canonical tag definida?

### 🗂️ Schema Markup (10%)
- JSON-LD presente?
- Tipos de schema (Organization, Article, FAQ, Product)?
- Completude dos dados estruturados?

### 📡 Platform Optim. (10%)
- Otimizado para Google AI Overview?
- Perguntas de cauda longa respondidas?
- Passagens citáveis e diretas?

---

## Baseado em

[geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) — skill original para Claude Code,  
adaptado para rodar como web app independente com Gemini/Perplexity e melhorias GEO/AIO.

---

## Licença

MIT — Use livremente!
