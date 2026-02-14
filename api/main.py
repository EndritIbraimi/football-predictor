
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# ── Load model & data once at startup ──────────────────
BASE = Path(__file__).parent.parent
model    = joblib.load(BASE / "models/best_model.pkl")
encoder  = joblib.load(BASE / "models/outcome_encoder.pkl")
features = joblib.load(BASE / "models/feature_names.pkl")

df = pd.read_csv(BASE / "data/combined_matches.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# ── App ─────────────────────────────────────────────────
app = FastAPI(
    title="Football Predictor API",
    description="Predicts match outcomes using ML trained on 6,469 matches",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ─────────────────────────────────────────────
class MatchRequest(BaseModel):
    home_team:  str
    away_team:  str
    odds_home:  float
    odds_draw:  float
    odds_away:  float

class TeamForm(BaseModel):
    win_rate:      float
    draw_rate:     float
    goals_for:     float
    goals_against: float
    shots_target:  float
    corners:       float
    matches_found: int

class PredictionResponse(BaseModel):
    home_team:       str
    away_team:       str
    prediction:      str
    confidence:      float
    confidence_label:str
    prob_home_win:   float
    prob_draw:       float
    prob_away_win:   float
    home_form:       TeamForm
    away_form:       TeamForm

# ── Helpers ─────────────────────────────────────────────
def get_team_form(team: str, n: int = 5) -> dict:
    past = df[
        (df["home_team"] == team) | (df["away_team"] == team)
    ].tail(n)

    if len(past) == 0:
        return {"w":0.45,"d":0.24,"gf":1.5,"ga":1.3,"sot":4.5,"corners":5.0,"n":0}

    w=d=gf=ga=sot=corners=0
    for _, r in past.iterrows():
        if r["home_team"] == team:
            gf+=r["home_goals"]; ga+=r["away_goals"]
            sot+=r.get("home_shots_target",4.5) or 4.5
            corners+=r.get("home_corners",5.0) or 5.0
            if r["outcome"]=="HOME_WIN": w+=1
            elif r["outcome"]=="DRAW":   d+=1
        else:
            gf+=r["away_goals"]; ga+=r["home_goals"]
            sot+=r.get("away_shots_target",4.5) or 4.5
            corners+=r.get("away_corners",5.0) or 5.0
            if r["outcome"]=="AWAY_WIN": w+=1
            elif r["outcome"]=="DRAW":   d+=1
    n2=len(past)
    return {"w":w/n2,"d":d/n2,"gf":gf/n2,"ga":ga/n2,"sot":sot/n2,"corners":corners/n2,"n":n2}

# ── Routes ──────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Football Predictor API", "status": "running", "accuracy": "53.2%"}

@app.get("/teams")
def get_teams():
    teams = sorted(set(df["home_team"].unique()) | set(df["away_team"].unique()))
    return {"teams": teams, "count": len(teams)}

@app.get("/team/{team_name}/form")
def get_form(team_name: str):
    form = get_team_form(team_name)
    if form["n"] == 0:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    return {
        "team": team_name,
        "last_5": {
            "win_rate":      round(form["w"], 3),
            "draw_rate":     round(form["d"], 3),
            "goals_for":     round(form["gf"], 2),
            "goals_against": round(form["ga"], 2),
            "shots_target":  round(form["sot"], 2),
            "corners":       round(form["corners"], 2),
        }
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(req: MatchRequest):
    h = get_team_form(req.home_team)
    a = get_team_form(req.away_team)

    imp_h = 1/req.odds_home
    imp_d = 1/req.odds_draw
    imp_a = 1/req.odds_away
    total = imp_h + imp_d + imp_a
    imp_h/=total; imp_d/=total; imp_a/=total

    X = pd.DataFrame([{
        "h_win_rate":h["w"],"h_draw_rate":h["d"],
        "h_goals_for":h["gf"],"h_goals_against":h["ga"],
        "h_shots_target":h["sot"],"h_corners":h["corners"],
        "a_win_rate":a["w"],"a_draw_rate":a["d"],
        "a_goals_for":a["gf"],"a_goals_against":a["ga"],
        "a_shots_target":a["sot"],"a_corners":a["corners"],
        "win_diff":h["w"]-a["w"],"goals_diff":h["gf"]-a["gf"],
        "sot_diff":h["sot"]-a["sot"],
        "imp_home":imp_h,"imp_draw":imp_d,"imp_away":imp_a,
    }])[features]

    probs      = model.predict_proba(X)[0]
    classes    = encoder.classes_
    prob_dict  = dict(zip(classes, probs))
    prediction = classes[np.argmax(probs)]
    confidence = float(max(probs))

    if confidence >= 0.60:   conf_label = "HIGH"
    elif confidence >= 0.50: conf_label = "MEDIUM"
    else:                    conf_label = "LOW"

    return PredictionResponse(
        home_team=req.home_team,
        away_team=req.away_team,
        prediction=prediction,
        confidence=round(confidence, 3),
        confidence_label=conf_label,
        prob_home_win=round(prob_dict.get("HOME_WIN",0), 3),
        prob_draw=round(prob_dict.get("DRAW",0), 3),
        prob_away_win=round(prob_dict.get("AWAY_WIN",0), 3),
        home_form=TeamForm(
            win_rate=round(h["w"],3), draw_rate=round(h["d"],3),
            goals_for=round(h["gf"],2), goals_against=round(h["ga"],2),
            shots_target=round(h["sot"],2), corners=round(h["corners"],2),
            matches_found=h["n"]
        ),
        away_form=TeamForm(
            win_rate=round(a["w"],3), draw_rate=round(a["d"],3),
            goals_for=round(a["gf"],2), goals_against=round(a["ga"],2),
            shots_target=round(a["sot"],2), corners=round(a["corners"],2),
            matches_found=a["n"]
        )
    )

@app.get("/stats")
def get_stats():
    return {
        "total_matches": len(df),
        "leagues": df["league"].value_counts().to_dict(),
        "date_range": {
            "from": str(df["date"].min().date()),
            "to":   str(df["date"].max().date())
        },
        "model_accuracy": "53.2%",
        "outcome_distribution": df["outcome"].value_counts().to_dict()
    }

# ── Data update endpoint ─────────────────────────────────
from api.update_data import update_dataset
import threading

@app.post("/admin/update-data")
def trigger_update():
    """Fetch latest match results and update the dataset"""
    def run():
        update_dataset()
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
    return {"message": "Data update started in background", "status": "running"}

@app.get("/admin/latest-matches")
def latest_matches(n: int = 10):
    """Show the most recent matches in the dataset"""
    recent = df.tail(n)[["date","home_team","away_team","home_goals","away_goals","outcome","league"]]
    return {"matches": recent.to_dict(orient="records"), "total_in_dataset": len(df)}
