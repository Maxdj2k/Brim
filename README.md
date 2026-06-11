# Brim Search

Decentralized web search engine with real-time veracity protocol and social layer.

## Versions

### 1. Brim Browser (Recommended) ⭐
**Full browser with login, embedded viewing, and community discussion.**

```bash
cd /Users/theredferret03/brim
python3 brim_browser.py
```

**Features:**
- 🔐 User accounts (login/signup)
- 🌐 Browse websites with veracity panel visible
- 🔍 Search with DuckDuckGo
- 📊 Real-time credibility scoring (0-100)
- 💬 Comment and discuss on any website
- 🔒 All data stored locally
- 🎨 Dark theme interface

**Layout:**
- Left: Search results
- Center: Browse websites (opens in system browser with panel synced)
- Right: Veracity analysis + community comments

### 2. Simple Desktop
Basic version without login:

```bash
python3 brim_desktop.py
```

### 3. Browser Client (HTML/JS)
Standalone browser version:

```bash
open client/index.html
```

### 4. Lua + Windsurf
```bash
lua brim_search.lua
```

## Features

- **Authentication** — Create accounts, secure login
- **Web Search** — DuckDuckGo API with fallback
- **Veracity Protocol** — Real-time credibility analysis
- **Social Layer** — Comment on any website, see community ratings
- **Embedded Browsing** — Browse with panel visible (synced to external browser)
- **Signal Breakdown** — Authority, Security, Citations, Transparency
- **Local Storage** — No backend, no cloud, fully private

## Quick Start

```bash
cd /Users/theredferret03/brim
python3 brim_browser.py
```

1. Create account or sign in
2. Search for any topic
3. Click a result to open website
4. View veracity score in right panel
5. Post comments and see community ratings

## File Structure

```
brim/
├── brim_browser.py      # ⭐ Main browser app (USE THIS)
├── brim_desktop.py      # Simple version without auth
├── client/              # Browser-only version
│   ├── index.html
│   ├── brim.js
│   └── brim.css
├── brim_search.lua      # Lua version
├── archive/             # Old Django backend
└── README.md
```

## Data Storage

All user data stored locally in `~/.brim/`:
- `users.json` — Account credentials (hashed passwords)
- `comments.json` — Community reviews and discussions

## Legacy

Original Django backend preserved in `archive/django-backend/`.
