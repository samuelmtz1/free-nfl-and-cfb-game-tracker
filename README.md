# 🏈 100% Free Football Dashboard (NFL & CFB)

A desktop dashboard built with **Python**, **CustomTkinter**, and **SQLite** that delivers today's NFL and College Football games and scores without exceeding free API tiers.

---

## 🔒 API Key Handling

This repository is pre-configured with industry-standard security practices so your private keys are **never pushed to GitHub**:

1. **Environment Isolation**: Real keys live in `.env`, which is strictly ignored by `.gitignore`.
2. **Safe Template**: `.env.example` provides public placeholders with no real credentials.
3. **Local Database Caching**: API responses are cached in a local `sports_cache.sqlite` file (also gitignored).

---

## 🚀 Quickstart

### 1. Activate Virtual Environment
```bash
# On macOS / Linux:
source .venv/bin/activate
```

### 2. Run the Dashboard
```bash
python main.py
```
*(The app will launch immediately with demo data even if you don't have API keys yet!)*

---

## 🔑 Adding Real API Keys (100% Free)

When you're ready to connect live data:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Get your free keys:
   * **NFL (BallDontLie)**: [app.balldontlie.io](https://app.balldontlie.io) *(5 req/min free limit)*
   * **College Football (CFBD)**: [collegefootballdata.com/key](https://collegefootballdata.com/key) *(1,000 req/month free limit)*
3. Paste them into `.env`:
   ```env
   BALLDONTLIE_API_KEY=your_actual_key_here
   CFBD_API_KEY=your_actual_key_here
   ```

---

## 🎨 Customizing the UI (`theme.json`)

You can fully customize the look and feel of the app by editing `theme.json`:

```json
{
  "theme_name": "Modern Stadium Dark",
  "mode": "dark",
  "colors": {
    "background": "#0f172a",
    "surface": "#1e293b",
    "primary": "#3b82f6",
    "accent_nfl": "#38bdf8",
    "accent_cfb": "#f97316"
  }
}
```

---

## 🧪 Running Tests

To verify that the cache, parsers, and rate limits are working correctly:
```bash
python test_dashboard.py
```
