import { useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from "recharts";

const API = "http://localhost:8000";

type Form = {
  win_rate: number; draw_rate: number;
  goals_for: number; goals_against: number;
  shots_target: number; corners: number;
  matches_found: number;
};

type Prediction = {
  home_team: string; away_team: string;
  prediction: string; confidence: number; confidence_label: string;
  prob_home_win: number; prob_draw: number; prob_away_win: number;
  home_form: Form; away_form: Form;
};

const OUTCOME_LABELS: Record<string, string> = {
  HOME_WIN: "Home Win", DRAW: "Draw", AWAY_WIN: "Away Win"
};

const CONF_COLORS: Record<string, string> = {
  HIGH: "#22c55e", MEDIUM: "#f59e0b", LOW: "#ef4444"
};

const TEAMS = [
  "Arsenal","Aston Villa","Barcelona","Brentford","Brighton",
  "Burnley","Chelsea","Crystal Palace","Everton","Fulham",
  "Liverpool","Luton","Man City","Man United","Newcastle",
  "Nottm Forest","Real Madrid","Sheff Utd","Tottenham",
  "West Ham","Wolves","Ath Madrid","Atletico Madrid",
  "Sevilla","Valencia","Villarreal","Bayern Munich",
  "Borussia Dortmund","RB Leipzig","AC Milan","Inter",
  "Juventus","Napoli","Roma"
];

export default function App() {
  const [homeTeam,  setHomeTeam]  = useState("Barcelona");
  const [awayTeam,  setAwayTeam]  = useState("Real Madrid");
  const [oddsHome,  setOddsHome]  = useState("2.10");
  const [oddsDraw,  setOddsDraw]  = useState("3.50");
  const [oddsAway,  setOddsAway]  = useState("3.40");
  const [result,    setResult]    = useState<Prediction | null>(null);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState("");

  async function handlePredict() {
    setLoading(true); setError(""); setResult(null);
    try {
      const { data } = await axios.post<Prediction>(`${API}/predict`, {
        home_team: homeTeam, away_team: awayTeam,
        odds_home: parseFloat(oddsHome),
        odds_draw: parseFloat(oddsDraw),
        odds_away: parseFloat(oddsAway),
      });
      setResult(data);
    } catch (e: unknown) {
      if (axios.isAxiosError(e)) {
        setError(e.response?.data?.detail || "Prediction failed. Is the API running?");
      } else {
        setError("Prediction failed. Is the API running?");
      }
    } finally {
      setLoading(false);
    }
  }

  const chartData = result ? [
    { name: "Home Win", prob: +(result.prob_home_win * 100).toFixed(1), color: "#3b82f6" },
    { name: "Draw",     prob: +(result.prob_draw     * 100).toFixed(1), color: "#f59e0b" },
    { name: "Away Win", prob: +(result.prob_away_win * 100).toFixed(1), color: "#ef4444" },
  ] : [];

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", color:"#f1f5f9",
                  fontFamily:"'Segoe UI', sans-serif" }}>

      {/* Header */}
      <div style={{ background:"linear-gradient(135deg,#1e3a5f,#0f172a)",
                    padding:"32px 24px", textAlign:"center",
                    borderBottom:"1px solid #1e293b" }}>
        <div style={{ fontSize:48 }}>⚽</div>
        <h1 style={{ margin:"8px 0 4px", fontSize:28, fontWeight:700,
                     background:"linear-gradient(90deg,#60a5fa,#34d399)",
                     WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
          Football Match Predictor
        </h1>
        <p style={{ color:"#94a3b8", margin:0 }}>
          ML model trained on 6,469 matches · 53.2% accuracy
        </p>
      </div>

      <div style={{ maxWidth:800, margin:"0 auto", padding:"32px 24px" }}>

        {/* Input Card */}
        <div style={{ background:"#1e293b", borderRadius:16, padding:28,
                      border:"1px solid #334155", marginBottom:24 }}>
          <h2 style={{ margin:"0 0 20px", fontSize:18, color:"#e2e8f0" }}>
            Select Match
          </h2>

          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:20 }}>
            <div>
              <label style={{ display:"block", color:"#94a3b8", marginBottom:6, fontSize:14 }}>
                Home Team
              </label>
              <select value={homeTeam} onChange={e => setHomeTeam(e.target.value)}
                style={{ width:"100%", padding:"10px 12px", borderRadius:8,
                         background:"#0f172a", color:"#f1f5f9",
                         border:"1px solid #475569", fontSize:15 }}>
                {TEAMS.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label style={{ display:"block", color:"#94a3b8", marginBottom:6, fontSize:14 }}>
                Away Team
              </label>
              <select value={awayTeam} onChange={e => setAwayTeam(e.target.value)}
                style={{ width:"100%", padding:"10px 12px", borderRadius:8,
                         background:"#0f172a", color:"#f1f5f9",
                         border:"1px solid #475569", fontSize:15 }}>
                {TEAMS.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div style={{ marginBottom:8 }}>
            <label style={{ display:"block", color:"#94a3b8", marginBottom:8, fontSize:14 }}>
              Betting Odds (from bet365 / Google)
            </label>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
              {[
                { label:"Home Win", val:oddsHome, set:setOddsHome },
                { label:"Draw",     val:oddsDraw, set:setOddsDraw },
                { label:"Away Win", val:oddsAway, set:setOddsAway },
              ].map(({ label, val, set }) => (
                <div key={label}>
                  <div style={{ color:"#64748b", fontSize:12, marginBottom:4 }}>{label}</div>
                  <input type="number" step="0.05" min="1" value={val}
                    onChange={e => set(e.target.value)}
                    style={{ width:"100%", padding:"8px 10px", borderRadius:8,
                             background:"#0f172a", color:"#f1f5f9",
                             border:"1px solid #475569", fontSize:15,
                             boxSizing:"border-box" }} />
                </div>
              ))}
            </div>
          </div>

          <button onClick={handlePredict} disabled={loading}
            style={{ marginTop:20, width:"100%", padding:"14px",
                     borderRadius:10, border:"none", cursor:"pointer",
                     fontSize:16, fontWeight:600,
                     background: loading
                       ? "#334155"
                       : "linear-gradient(135deg,#3b82f6,#2563eb)",
                     color:"white", transition:"all 0.2s" }}>
            {loading ? "Predicting..." : "Predict Match"}
          </button>

          {error && (
            <div style={{ marginTop:12, padding:12, background:"#450a0a",
                          borderRadius:8, color:"#fca5a5", fontSize:14 }}>
              {error}
            </div>
          )}
        </div>

        {/* Result Card */}
        {result && (
          <div style={{ background:"#1e293b", borderRadius:16, padding:28,
                        border:"1px solid #334155" }}>

            {/* Prediction headline */}
            <div style={{ textAlign:"center", marginBottom:28 }}>
              <div style={{ fontSize:13, color:"#64748b", marginBottom:6 }}>
                {result.home_team} vs {result.away_team}
              </div>
              <div style={{ fontSize:32, fontWeight:700, color:"#f1f5f9", marginBottom:8 }}>
                {OUTCOME_LABELS[result.prediction]}
              </div>
              <span style={{
                padding:"4px 14px", borderRadius:20, fontSize:13, fontWeight:600,
                background: CONF_COLORS[result.confidence_label] + "22",
                color: CONF_COLORS[result.confidence_label],
                border: `1px solid ${CONF_COLORS[result.confidence_label]}44`
              }}>
                {result.confidence_label} confidence · {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>

            {/* Probability Bar Chart */}
            <div style={{ marginBottom:28 }}>
              <div style={{ color:"#94a3b8", fontSize:13, marginBottom:12 }}>
                Probability Breakdown
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={chartData} barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill:"#94a3b8", fontSize:13 }} />
                  <YAxis domain={[0,100]} tick={{ fill:"#94a3b8", fontSize:12 }}
                         tickFormatter={(v: number) => `${v}%`} />
                  <Tooltip
                    formatter={(value: unknown) => [`${value}%`, "Probability"]}
                    contentStyle={{ background:"#0f172a", border:"1px solid #334155",
                                    borderRadius:8, color:"#f1f5f9" }} />
                  <Bar dataKey="prob" radius={[6,6,0,0]}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Form Table */}
            <div>
              <div style={{ color:"#94a3b8", fontSize:13, marginBottom:12 }}>
                Recent Form (Last 5 Matches)
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
                {[
                  { team: result.home_team, form: result.home_form, icon: "Home" },
                  { team: result.away_team, form: result.away_form, icon: "Away" },
                ].map(({ team, form, icon }) => (
                  <div key={team} style={{ background:"#0f172a", borderRadius:10,
                                           padding:16, border:"1px solid #1e293b" }}>
                    <div style={{ fontWeight:600, marginBottom:10, fontSize:14 }}>
                      {icon}: {team}
                    </div>
                    {[
                      ["Win Rate",         `${(form.win_rate*100).toFixed(0)}%`],
                      ["Draw Rate",        `${(form.draw_rate*100).toFixed(0)}%`],
                      ["Goals For",        form.goals_for.toFixed(1)],
                      ["Goals Against",    form.goals_against.toFixed(1)],
                      ["Shots on Target",  form.shots_target.toFixed(1)],
                      ["Corners",          form.corners.toFixed(1)],
                    ].map(([label, value]) => (
                      <div key={label as string}
                           style={{ display:"flex", justifyContent:"space-between",
                                    marginBottom:4, fontSize:13 }}>
                        <span style={{ color:"#64748b" }}>{label}</span>
                        <span style={{ color:"#e2e8f0", fontWeight:500 }}>{value}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div style={{ textAlign:"center", marginTop:24, color:"#334155", fontSize:12 }}>
          Built by Endrit Ibraimi · Football Predictor v1.0
        </div>
      </div>
    </div>
  );
}
