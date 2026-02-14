
"""
Football Match Predictor
Usage: python3 predict.py
"""
import joblib
import numpy as np
import pandas as pd

model    = joblib.load('models/best_model.pkl')
encoder  = joblib.load('models/outcome_encoder.pkl')
features = joblib.load('models/feature_names.pkl')

df = pd.read_csv('data/combined_matches.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

def get_team_form(team, n=5):
    past = df[
        (df['home_team'] == team) | (df['away_team'] == team)
    ].tail(n)
    if len(past) == 0:
        print(f"  ⚠️  Warning: '{team}' not found in dataset - using defaults")
        return {'w':0.45,'d':0.24,'gf':1.5,'ga':1.3,'sot':4.5,'corners':5.0}
    w=d=gf=ga=sot=corners=0
    for _, r in past.iterrows():
        if r['home_team'] == team:
            gf+=r['home_goals']; ga+=r['away_goals']
            sot+=r.get('home_shots_target', 4.5) or 4.5
            corners+=r.get('home_corners', 5.0) or 5.0
            if r['outcome']=='HOME_WIN': w+=1
            elif r['outcome']=='DRAW': d+=1
        else:
            gf+=r['away_goals']; ga+=r['home_goals']
            sot+=r.get('away_shots_target', 4.5) or 4.5
            corners+=r.get('away_corners', 5.0) or 5.0
            if r['outcome']=='AWAY_WIN': w+=1
            elif r['outcome']=='DRAW': d+=1
    n2=len(past)
    return {'w':w/n2,'d':d/n2,'gf':gf/n2,'ga':ga/n2,'sot':sot/n2,'corners':corners/n2}

def predict_match(home_team, away_team, odds_home, odds_draw, odds_away):
    h = get_team_form(home_team)
    a = get_team_form(away_team)
    imp_h = 1/odds_home; imp_d = 1/odds_draw; imp_a = 1/odds_away
    total = imp_h + imp_d + imp_a
    imp_h/=total; imp_d/=total; imp_a/=total

    X = pd.DataFrame([{
        'h_win_rate':h['w'],'h_draw_rate':h['d'],
        'h_goals_for':h['gf'],'h_goals_against':h['ga'],
        'h_shots_target':h['sot'],'h_corners':h['corners'],
        'a_win_rate':a['w'],'a_draw_rate':a['d'],
        'a_goals_for':a['gf'],'a_goals_against':a['ga'],
        'a_shots_target':a['sot'],'a_corners':a['corners'],
        'win_diff':h['w']-a['w'],'goals_diff':h['gf']-a['gf'],
        'sot_diff':h['sot']-a['sot'],
        'imp_home':imp_h,'imp_draw':imp_d,'imp_away':imp_a,
    }])[features]

    probs  = model.predict_proba(X)[0]
    classes = encoder.classes_
    prob_dict = dict(zip(classes, probs))
    prediction = classes[np.argmax(probs)]
    confidence = max(probs)

    # Confidence label
    if confidence >= 0.60:   conf_label = "🔥 HIGH"
    elif confidence >= 0.50: conf_label = "✅ MEDIUM"
    else:                    conf_label = "⚠️  LOW"

    print(f"\n{'='*52}")
    print(f"  ⚽ {home_team} vs {away_team}")
    print(f"{'='*52}")
    print(f"  🏠 Home Win:  {prob_dict.get('HOME_WIN',0):>6.1%}  (odds: {odds_home})")
    print(f"  🤝 Draw:      {prob_dict.get('DRAW',0):>6.1%}  (odds: {odds_draw})")
    print(f"  ✈️  Away Win:  {prob_dict.get('AWAY_WIN',0):>6.1%}  (odds: {odds_away})")
    print(f"\n  🎯 Prediction:  {prediction}  [{conf_label} confidence: {confidence:.1%}]")
    print(f"\n  📊 Last 5 games:")
    print(f"     {home_team:<22} W:{h['w']:.0%}  GF:{h['gf']:.1f}  GA:{h['ga']:.1f}  SOT:{h['sot']:.1f}")
    print(f"     {away_team:<22} W:{a['w']:.0%}  GF:{a['gf']:.1f}  GA:{a['ga']:.1f}  SOT:{a['sot']:.1f}")
    return prob_dict, prediction

if __name__ == "__main__":
    print("\n🔮 FOOTBALL PREDICTIONS")
    print("=" * 52)
    print("Model accuracy: 53.2% | Trained on 6,469 matches")

    # ── UPDATE THESE EACH GAMEWEEK ──────────────────────
    predict_match("Arsenal",          "Manchester City", 2.50, 3.40, 2.80)
    predict_match("Barcelona",        "Real Madrid",     2.10, 3.50, 3.40)
    predict_match("Liverpool",        "Everton",         1.45, 4.50, 7.00)
    # ────────────────────────────────────────────────────
