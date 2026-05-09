import subprocess
import pandas as pd
import plotly.express as px
from flask import Flask, render_template_string
import os

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Student Focus Monitor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: Arial, sans-serif; background: #0a0a1a; color: #eee; padding: 24px; }
    h1 { color: #a78bfa; text-align: center; font-size: 2rem; margin-bottom: 8px; }
    .subtitle { text-align: center; color: #888; font-size: 0.9rem; margin-bottom: 24px; }
    .kpi-row { display: flex; gap: 16px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }
    .kpi { background: #1a1a2e; border-radius: 16px; padding: 20px 32px; text-align: center; border: 1px solid #2a2a4a; min-width: 160px; }
    .kpi-val { font-size: 2rem; font-weight: bold; }
    .kpi-label { font-size: 0.8rem; color: #aaa; margin-top: 6px; }
    .focused { color: #34d399; }
    .distracted { color: #f87171; }
    .purple { color: #a78bfa; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0; }
    .chart { background: #1a1a2e; border-radius: 16px; padding: 16px; border: 1px solid #2a2a4a; }
    .chart-full { background: #1a1a2e; border-radius: 16px; padding: 16px; border: 1px solid #2a2a4a; margin: 16px 0; }
    .refresh-btn { display: block; margin: 20px auto; padding: 10px 28px; background: #a78bfa; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; text-decoration: none; text-align: center; width: fit-content; }
    @media(max-width: 768px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h1>Student Focus Monitor</h1>
  <p class="subtitle">Analysing {{ total }} readings across 2000 students · Powered by Apache Spark + Docker</p>

  <div class="kpi-row">
    <div class="kpi">
      <div class="kpi-val focused">{{ focused }}</div>
      <div class="kpi-label">Focused readings</div>
    </div>
    <div class="kpi">
      <div class="kpi-val distracted">{{ distracted }}</div>
      <div class="kpi-label">Distracted readings</div>
    </div>
    <div class="kpi">
      <div class="kpi-val purple">{{ pct }}%</div>
      <div class="kpi-label">Focus rate</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:#60a5fa">2000</div>
      <div class="kpi-label">Students monitored</div>
    </div>
  </div>

  <div class="grid">
    <div class="chart">{{ bar_chart | safe }}</div>
    <div class="chart">{{ session_chart | safe }}</div>
  </div>

  <div class="chart-full">{{ line_chart | safe }}</div>

  <div class="chart-full">{{ archetype_chart | safe }}</div>

  <a href="/refresh" class="refresh-btn">Re-run Spark Analysis</a>
</body>
</html>
"""

def run_spark():
    subprocess.run(["python3", "/app/analysis.py"], check=True)

def load_data():
    paths = [
        "/app/data/hourly_analysis.parquet",
        "/app/data/status_summary.parquet",
        "/app/data/session_analysis.parquet",
        "/app/data/archetype_analysis.parquet"
    ]
    if not os.path.exists(paths[0]):
        run_spark()
    return [pd.read_parquet(p) for p in paths]

@app.route("/")
def index():
    hourly, summary, session, archetype = load_data()

    focused = int(summary[summary["Status"] == "FOCUSED"]["Count"].values[0]) if "FOCUSED" in summary["Status"].values else 0
    distracted = int(summary[summary["Status"] == "DISTRACTED"]["Count"].values[0]) if "DISTRACTED" in summary["Status"].values else 0
    total = focused + distracted
    pct = round(focused / total * 100, 1) if total > 0 else 0

    config = {"displayModeBar": False}

    # Bar chart
    bar = px.bar(hourly, x="Hour", y="Count", color="Status", barmode="group",
        color_discrete_map={"FOCUSED": "#34d399", "DISTRACTED": "#f87171"},
        title="Focus vs Distraction by Hour", template="plotly_dark")
    bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40,b=20))

    # Session type chart
    session_order = ["Morning warmup", "Theory lecture", "Theory lecture cont.",
                     "Short break", "Problem solving", "Lunch break",
                     "Post lunch theory", "Lab/practical", "Quiz/exam", "Evening wind down"]
    ses = px.bar(session, x="Session_Type", y="Count", color="Status", barmode="group",
        color_discrete_map={"FOCUSED": "#34d399", "DISTRACTED": "#f87171"},
        title="Focus by Session Type", template="plotly_dark",
        category_orders={"Session_Type": session_order})
    ses.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-35, margin=dict(t=40,b=80))

    # Line chart
    line = px.line(hourly, x="Hour", y="Count", color="Status",
        color_discrete_map={"FOCUSED": "#34d399", "DISTRACTED": "#f87171"},
        title="Focus Trend over the Day", template="plotly_dark", markers=True)
    line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40,b=20))

    # Archetype chart
    arch = px.bar(archetype, x="Archetype", y="Count", color="Status", barmode="group",
        color_discrete_map={"FOCUSED": "#34d399", "DISTRACTED": "#f87171"},
        title="Focus vs Distraction by Student Archetype", template="plotly_dark")
    arch.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40,b=20))

    pjs = "cdn"
    return render_template_string(DASHBOARD_HTML,
        focused=f"{focused:,}", distracted=f"{distracted:,}",
        total=f"{total:,}", pct=pct,
        bar_chart=bar.to_html(full_html=False, include_plotlyjs=pjs, config=config),
        session_chart=ses.to_html(full_html=False, include_plotlyjs=False, config=config),
        line_chart=line.to_html(full_html=False, include_plotlyjs=False, config=config),
        archetype_chart=arch.to_html(full_html=False, include_plotlyjs=False, config=config))

@app.route("/refresh")
def refresh():
    run_spark()
    return "<script>window.location='/'</script>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)