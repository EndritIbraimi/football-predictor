
"""
Fetches latest match results from football-data.org API
and appends new matches to combined_matches.csv
Run this weekly to keep data fresh.
"""
import requests
import pandas as pd
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("FOOTBALL_API_KEY", "2351fe8c7cf04d0b87ba724d2d0d5ff6")
BASE_URL = "https://api.football-data.org/v4"
HEADERS  = {"X-Auth-Token": API_KEY}
DATA_PATH = Path(__file__).parent.parent / "data" / "combined_matches.csv"

LEAGUES = {
    "PL": "E0",   # Premier League
    "PD": "SP1",  # La Liga
    "CL": None,   # Champions League (API only)
}

def fetch_recent_matches(competition_code: str, season: int = 2024) -> list:
    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    params = {"season": season, "status": "FINISHED"}
    resp = requests.get(url, headers=HEADERS, params=params)

    if resp.status_code == 200:
        return resp.json().get("matches", [])
    elif resp.status_code == 403:
        print(f"  ⚠️  {competition_code} - not on free tier")
        return []
    else:
        print(f"  ❌ {competition_code} error {resp.status_code}")
        return []

def parse_match(match: dict, league_code: str) -> dict | None:
    try:
        hg = match["score"]["fullTime"]["home"]
        ag = match["score"]["fullTime"]["away"]
        if hg is None or ag is None:
            return None

        if hg > ag:   outcome = "HOME_WIN"
        elif hg < ag: outcome = "AWAY_WIN"
        else:         outcome = "DRAW"

        return {
            "league":      league_code,
            "date":        match["utcDate"][:10],
            "home_team":   match["homeTeam"]["name"],
            "away_team":   match["awayTeam"]["name"],
            "home_goals":  hg,
            "away_goals":  ag,
            "outcome":     outcome,
            # These won't be available from API (no shots/corners on free tier)
            # but we keep columns consistent with NaN
            "home_shots":         None,
            "away_shots":         None,
            "home_shots_target":  None,
            "away_shots_target":  None,
            "home_corners":       None,
            "away_corners":       None,
            "home_yellows":       None,
            "away_yellows":       None,
            # No odds from API - will use None (model uses form features still)
            "odds_home":   None,
            "odds_draw":   None,
            "odds_away":   None,
            "avg_odds_home": None,
            "avg_odds_draw": None,
            "avg_odds_away": None,
            "source":      "api_live",
        }
    except Exception as e:
        print(f"  ⚠️  Parse error: {e}")
        return None

def update_dataset():
    print(f"\n{'='*52}")
    print(f"  Football Predictor - Data Update")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*52}")

    # Load existing data
    if DATA_PATH.exists():
        existing = pd.read_csv(DATA_PATH)
        existing["date"] = pd.to_datetime(existing["date"])
        print(f"\n  Existing matches: {len(existing)}")
        latest_date = existing["date"].max()
        print(f"  Latest match in dataset: {latest_date.date()}")
    else:
        existing = pd.DataFrame()
        latest_date = pd.Timestamp("2020-01-01")
        print("  No existing dataset found - creating fresh")

    # Build a set of existing match keys to avoid duplicates
    if len(existing) > 0:
        existing_keys = set(
            existing["date"].astype(str) + "_" +
            existing["home_team"] + "_" +
            existing["away_team"]
        )
    else:
        existing_keys = set()

    # Fetch new matches from API
    new_matches = []
    league_map = {"PL": "E0", "PD": "SP1", "CL": "CL"}

    for code in ["PL", "PD", "CL"]:
        print(f"\n  Fetching {code}...")
        matches = fetch_recent_matches(code, season=2024)
        print(f"  Got {len(matches)} finished matches from API")

        for m in matches:
            parsed = parse_match(m, league_map.get(code, code))
            if parsed is None:
                continue

            # Check if this match is already in the dataset
            key = f"{parsed['date']}_{parsed['home_team']}_{parsed['away_team']}"
            if key not in existing_keys:
                new_matches.append(parsed)

        time.sleep(7)  # respect rate limit

    # Append new matches
    if new_matches:
        new_df = pd.DataFrame(new_matches)
        new_df["date"] = pd.to_datetime(new_df["date"])

        updated = pd.concat([existing, new_df], ignore_index=True)
        updated = updated.sort_values("date").reset_index(drop=True)
        updated.to_csv(DATA_PATH, index=False)

        print(f"\n  ✅ Added {len(new_matches)} new matches")
        print(f"  ✅ Total dataset: {len(updated)} matches")
        print(f"  ✅ Saved to {DATA_PATH}")
    else:
        print(f"\n  ✅ Dataset already up to date! No new matches found.")

    print(f"\n  Latest matches added:")
    if new_matches:
        for m in new_matches[-5:]:
            print(f"    {m['date']}  {m['home_team']} {m['home_goals']}-{m['away_goals']} {m['away_team']}")

if __name__ == "__main__":
    update_dataset()
