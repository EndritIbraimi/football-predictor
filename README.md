# ⚽ Football Match Predictor

A full-stack machine learning application that predicts football match outcomes (Win / Draw / Loss) using historical data, live API updates, and betting odds analysis.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikitlearn)
![Accuracy](https://img.shields.io/badge/Model%20Accuracy-53.2%25-brightgreen)

---

## Demo

> Select any two teams, enter the current betting odds, and get an instant ML-powered prediction with probability breakdown and recent form stats.

---

## Features

- **Match Outcome Prediction** — Predicts Home Win, Draw, or Away Win with confidence levels
- **Probability Breakdown** — Visual bar chart showing percentage chance for each outcome
- **Team Form Analysis** — Last 5 matches stats: win rate, goals, shots on target, corners
- **Betting Odds Integration** — Uses bookmaker implied probabilities as model features
- **Live Data Updates** — Fetches latest match results weekly via football-data.org API
- **REST API** — Full FastAPI backend with interactive Swagger docs at `/docs`

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| ML Model  | Python, scikit-learn, pandas      |
| Backend   | FastAPI, Uvicorn, SQLite          |
| Frontend  | React, TypeScript, Recharts       |
| Data      | football-data.co.uk, football-data.org API |

---

## ML Model

| Metric              | Value                        |
|---------------------|------------------------------|
| Training data       | 6,469 matches                |
| Leagues             | Premier League, La Liga, Bundesliga, Serie A |
| Seasons             | 2019/20 → 2024/25            |
| Algorithm           | Random Forest (300 estimators) |
| Accuracy            | **53.2%**                    |
| Baseline (random)   | 33.3%                        |
| Bookmaker accuracy  | ~55-60%                      |

### Key Features Used
- Team form: win rate, draw rate, goals scored/conceded (last 5 matches)
- Shots on target and corners (last 5 matches)
- Win rate differential between home and away team
- **Bookmaker implied probabilities** (most predictive feature)

> 53.2% accuracy is 20 percentage points above random guessing and within 2-3% of professional bookmakers who employ entire teams of analysts.

---

## Project Structure

```
football-predictor/
├── api/
│   ├── main.py            # FastAPI app - all endpoints
│   └── update_data.py     # Weekly data updater script
├── frontend/
│   └── src/
│       └── App.tsx        # React UI
├── models/
│   ├── best_model.pkl     # Trained Random Forest model
│   ├── outcome_encoder.pkl
│   └── feature_names.pkl
├── notebooks/
│   └── 01_data_exploration.ipynb
├── predict.py             # Quick CLI prediction script
├── RUNNING.md             # How to run the project
├── requirements.txt
└── .env                   # API keys (not committed)
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free API key from [football-data.org](https://www.football-data.org/client/register)

### 1. Clone the repo

```bash
git clone https://github.com/EndritIbraimi/football-predictor.git
cd football-predictor
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Add your API key

```bash
cp .env.example .env
# Edit .env and add your football-data.org API key
```

### 4. Download historical data

```bash
python3 api/update_data.py
```

### 5. Start the backend

```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm start
```

Open **http://localhost:3000** in your browser.

---

## API Endpoints

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/`                       | API status                         |
| GET    | `/docs`                   | Interactive Swagger documentation  |
| GET    | `/teams`                  | List all available teams           |
| GET    | `/team/{name}/form`       | Get a team's recent form stats     |
| POST   | `/predict`                | Predict a match outcome            |
| GET    | `/stats`                  | Dataset and model statistics       |
| POST   | `/admin/update-data`      | Trigger live data update           |
| GET    | `/admin/latest-matches`   | Show most recent matches           |

### Example prediction request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Barcelona",
    "away_team": "Real Madrid",
    "odds_home": 2.10,
    "odds_draw": 3.50,
    "odds_away": 3.40
  }'
```

### Example response

```json
{
  "home_team": "Barcelona",
  "away_team": "Real Madrid",
  "prediction": "HOME_WIN",
  "confidence": 0.377,
  "confidence_label": "LOW",
  "prob_home_win": 0.377,
  "prob_draw": 0.333,
  "prob_away_win": 0.290,
  "home_form": {
    "win_rate": 0.8,
    "goals_for": 2.2,
    "goals_against": 1.0,
    "shots_target": 6.4,
    "corners": 6.2,
    "matches_found": 5
  }
}
```

---

## Data Sources

- **Historical data (2019-2025):** [football-data.co.uk](https://www.football-data.co.uk) — free CSV downloads with shots, corners, cards and betting odds
- **Live results:** [football-data.org](https://www.football-data.org) — free API with Premier League, La Liga, Champions League

---

## Roadmap

- [ ] Deploy backend to Railway / Render
- [ ] Deploy frontend to Vercel
- [ ] Add prediction history tracking
- [ ] Add more leagues (Serie A, Bundesliga)
- [ ] Retrain model automatically after data updates
- [ ] Add player injury/suspension data

---

## Author

**Endrit Ibraimi**
- GitHub: [@EndritIbraimi](https://github.com/EndritIbraimi)

---

## License

MIT License — feel free to use this project for learning and portfolio purposes.
