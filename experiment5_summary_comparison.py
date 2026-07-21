"""
experiment5_summary_comparison.py
Loads results from all 4 experiments and generates a combined comparison dashboard (PNG + HTML).
Run AFTER all 4 experiments have been executed.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import json, os, warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("  EXPERIMENT SUMMARY — Cross-Experiment Comparison")
print("=" * 60)

# ==============================
# LOAD RESULTS FROM EACH EXPERIMENT
# ==============================
missing = []
for f in ["experiment1_results.csv", "experiment2_zone_breakdown.csv",
          "experiment3_results.csv", "experiment4_results.csv"]:
    if not os.path.exists(f):
        missing.append(f)

if missing:
    print(f"\n⚠️  Missing result files: {missing}")
    print("   Please run all experiments first before running this script.")
    exit(1)

exp1 = pd.read_csv("experiment1_results.csv", index_col=0)
exp2_zone = pd.read_csv("experiment2_zone_breakdown.csv", index_col=0)
exp3 = pd.read_csv("experiment3_results.csv", index_col=0)
exp4 = pd.read_csv("experiment4_results.csv", index_col=0)

# Try to load hourly CSVs too
exp2_hourly = pd.read_csv("experiment2_hourly.csv") if os.path.exists("experiment2_hourly.csv") else None

print("✅ All result files loaded")

# ==============================
# DERIVED METRICS
# ==============================
# Exp2 cost summary
total_normal    = exp2_zone['normal'].sum()
total_optimized = exp2_zone['optimized'].sum()
tou_saving_pct  = ((total_normal - total_optimized) / total_normal) * 100

# Exp4 saving
exp4['Saving_%'] = exp4['Saving_%'].astype(float)
rec_saving_pct  = exp4['Saving_%'].mean()
total_saving_rm  = exp4['Saving_RM'].sum()

# Best model from exp1
best_model_row = exp1.loc[exp1['R²'].idxmax()]
best_model_name = best_model_row.name
best_r2  = best_model_row['R²']
best_mae = best_model_row['MAE']

# Best profile from exp3
best_profile_row = exp3.loc[exp3['R²'].idxmax()]
best_profile = best_profile_row.name
worst_profile_row = exp3.loc[exp3['Est. Daily Cost (RM)'].idxmax()]
worst_cost_profile = worst_profile_row.name

print(f"\n📌 Key Findings:")
print(f"   Best model       : {best_model_name}  (R²={best_r2}, MAE={best_mae})")
print(f"   ToU Saving       : {tou_saving_pct:.1f}%")
print(f"   Best profile     : {best_profile}")
print(f"   Rec. Saving      : {rec_saving_pct:.1f}% avg | RM {total_saving_rm:.4f} total")

# ==============================
# MATPLOTLIB SUMMARY FIGURE
# ==============================
fig = plt.figure(figsize=(20, 14), facecolor='#0f1117')
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)

ACCENT   = '#00d4aa'
ACCENT2  = '#ff6b6b'
ACCENT3  = '#ffd93d'
TEXT_COL = '#e8eaf6'
CARD_COL = '#1a1d2e'

def style_ax(ax, title):
    ax.set_facecolor(CARD_COL)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.set_title(title, color=ACCENT, fontsize=9, fontweight='bold', pad=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2d3e')

# ── Title ──────────────────────────────────────────────
ax_title = fig.add_subplot(gs[0, :])
ax_title.set_facecolor('#0f1117')
ax_title.axis('off')
ax_title.text(0.5, 0.75, "⚡ Electricity Consumption — Experiment Summary",
              ha='center', va='center', fontsize=18, fontweight='bold', color=TEXT_COL,
              transform=ax_title.transAxes)
ax_title.text(0.5, 0.25,
              f"Best Model: {best_model_name} (R²={best_r2})  |  "
              f"ToU Saving: {tou_saving_pct:.1f}%  |  "
              f"Recommendation Saving: {rec_saving_pct:.1f}%  |  "
              f"Best Profile: {best_profile}",
              ha='center', va='center', fontsize=10, color=ACCENT,
              transform=ax_title.transAxes)

# ── EXP 1: Model Comparison ────────────────────────────
ax1a = fig.add_subplot(gs[1, 0])
style_ax(ax1a, "EXP 1 — Model R² Score")
colors_r2 = [ACCENT if m == best_model_name else '#3d5a80' for m in exp1.index]
bars = ax1a.barh(exp1.index, exp1['R²'], color=colors_r2, edgecolor='none', height=0.5)
ax1a.set_xlim(0, 1.1)
ax1a.axvline(0.8, color=ACCENT2, linestyle='--', linewidth=1, alpha=0.7)
for bar, val in zip(bars, exp1['R²']):
    ax1a.text(val + 0.01, bar.get_y() + bar.get_height()/2,
              f'{val:.3f}', va='center', color=TEXT_COL, fontsize=8)
ax1a.set_xlabel("R²", color=TEXT_COL)

ax1b = fig.add_subplot(gs[1, 1])
style_ax(ax1b, "EXP 1 — MAE & RMSE")
x = np.arange(len(exp1))
w = 0.35
ax1b.bar(x - w/2, exp1['MAE'],  width=w, color=ACCENT,  alpha=0.85, label='MAE',  edgecolor='none')
ax1b.bar(x + w/2, exp1['RMSE'], width=w, color=ACCENT2, alpha=0.85, label='RMSE', edgecolor='none')
ax1b.set_xticks(x)
ax1b.set_xticklabels([m.replace(' ', '\n') for m in exp1.index], fontsize=7, color=TEXT_COL)
ax1b.set_ylabel("kW", color=TEXT_COL)
ax1b.legend(fontsize=7, labelcolor=TEXT_COL, facecolor=CARD_COL, edgecolor='none')

# ── EXP 2: ToU Cost Comparison ────────────────────────
ax2 = fig.add_subplot(gs[1, 2])
style_ax(ax2, "EXP 2 — Cost by ToU Zone")
zones = exp2_zone.index.tolist()
x = np.arange(len(zones))
w = 0.35
ax2.bar(x - w/2, exp2_zone['normal'],    width=w, color=ACCENT2, alpha=0.85, label='Normal', edgecolor='none')
ax2.bar(x + w/2, exp2_zone['optimized'], width=w, color=ACCENT,  alpha=0.85, label='Optimized', edgecolor='none')
ax2.set_xticks(x)
ax2.set_xticklabels(zones, fontsize=8, color=TEXT_COL)
ax2.set_ylabel("Cost (RM)", color=TEXT_COL)
ax2.legend(fontsize=7, labelcolor=TEXT_COL, facecolor=CARD_COL, edgecolor='none')

ax2b = fig.add_subplot(gs[1, 3])
style_ax(ax2b, f"EXP 2 — Total Saving ({tou_saving_pct:.1f}%)")
wedge_data   = [total_optimized, total_normal - total_optimized]
wedge_labels = ['Optimized', f'Saving\n{tou_saving_pct:.1f}%']
wedge_cols   = [ACCENT, ACCENT3]
ax2b.pie(wedge_data, labels=wedge_labels, colors=wedge_cols,
         autopct='%1.1f%%', startangle=90,
         textprops={'color': TEXT_COL, 'fontsize': 8})

# ── EXP 3: User Profiles ──────────────────────────────
ax3a = fig.add_subplot(gs[2, 0])
style_ax(ax3a, "EXP 3 — Daily Cost by Profile")
prof_colors = [ACCENT if p == best_profile else '#3d5a80' for p in exp3.index]
bars = ax3a.barh(exp3.index, exp3['Est. Daily Cost (RM)'],
                 color=prof_colors, edgecolor='none', height=0.5)
ax3a.set_xlabel("RM / day", color=TEXT_COL)
ax3a.tick_params(axis='y', labelsize=7)

ax3b = fig.add_subplot(gs[2, 1])
style_ax(ax3b, "EXP 3 — Model R² by Profile")
r2_colors = [ACCENT if v == exp3['R²'].max() else '#3d5a80' for v in exp3['R²']]
ax3b.barh(exp3.index, exp3['R²'], color=r2_colors, edgecolor='none', height=0.5)
ax3b.axvline(0.8, color=ACCENT2, linestyle='--', linewidth=1, alpha=0.7)
ax3b.set_xlabel("R²", color=TEXT_COL)
ax3b.tick_params(axis='y', labelsize=7)

# ── EXP 4: Recommendation ────────────────────────────
ax4a = fig.add_subplot(gs[2, 2])
style_ax(ax4a, "EXP 4 — Cost Saving by Recommendation")
rec_colors = {'Shift to Off-Peak': ACCENT2, 'Reduce or Delay': ACCENT3, 'No Change': ACCENT}
bar_cols = [rec_colors.get(r, ACCENT) for r in exp4.index]
ax4a.bar(range(len(exp4)), exp4['Saving_RM'], color=bar_cols, edgecolor='none', alpha=0.9)
ax4a.set_xticks(range(len(exp4)))
ax4a.set_xticklabels([r.replace(' ', '\n') for r in exp4.index], fontsize=7, color=TEXT_COL)
ax4a.set_ylabel("Saving (RM)", color=TEXT_COL)

ax4b = fig.add_subplot(gs[2, 3])
style_ax(ax4b, "EXP 4 — Saving % by Recommendation")
ax4b.bar(range(len(exp4)), exp4['Saving_%'], color=bar_cols, edgecolor='none', alpha=0.9)
ax4b.set_xticks(range(len(exp4)))
ax4b.set_xticklabels([r.replace(' ', '\n') for r in exp4.index], fontsize=7, color=TEXT_COL)
ax4b.set_ylabel("Saving %", color=TEXT_COL)
ax4b.axhline(exp4['Saving_%'].mean(), color=ACCENT3, linestyle='--', linewidth=1,
             label=f"Avg {exp4['Saving_%'].mean():.1f}%")
ax4b.legend(fontsize=7, labelcolor=TEXT_COL, facecolor=CARD_COL, edgecolor='none')

plt.savefig("summary_comparison.png", dpi=150, bbox_inches='tight', facecolor='#0f1117')
print("\n✅ Summary chart saved: summary_comparison.png")

# ==============================
# HTML DASHBOARD
# ==============================
exp1_json  = exp1.reset_index().to_dict(orient='records')
exp3_json  = exp3.reset_index().to_dict(orient='records')
exp4_json  = exp4.reset_index().to_dict(orient='records')
exp2z_json = exp2_zone.reset_index().to_dict(orient='records')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Experiment Comparison Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0b0d17; --card: #12151f; --border: #1e2235;
    --accent: #00d4aa; --accent2: #ff6b6b; --accent3: #ffd93d;
    --text: #e8eaf6; --muted: #7b82a0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'DM Mono', monospace; min-height: 100vh; }}
  header {{ padding: 2.5rem 3rem 1.5rem; border-bottom: 1px solid var(--border); }}
  header h1 {{ font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: var(--accent); }}
  header p  {{ color: var(--muted); font-size: 0.8rem; margin-top: 0.4rem; }}

  .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; padding: 1.5rem 3rem; }}
  .kpi {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem 1.5rem; }}
  .kpi .label {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }}
  .kpi .value {{ font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; margin-top: 0.3rem; }}
  .kpi .sub   {{ font-size: 0.72rem; color: var(--muted); margin-top: 0.2rem; }}

  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; padding: 0 3rem 3rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; }}
  .card h3 {{ font-family: 'Syne', sans-serif; font-size: 0.9rem; font-weight: 700; color: var(--accent); margin-bottom: 1rem; letter-spacing: 0.04em; }}
  .card canvas {{ max-height: 260px; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 0.75rem; margin-top: 0.5rem; }}
  th {{ color: var(--muted); text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid var(--border); font-weight: 500; }}
  td {{ padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border); color: var(--text); }}
  tr:last-child td {{ border-bottom: none; }}
  .best {{ color: var(--accent); font-weight: 700; }}

  @media (max-width: 900px) {{
    .kpi-row {{ grid-template-columns: 1fr 1fr; }}
    .grid     {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <h1>⚡ Electricity Experiment Dashboard</h1>
  <p>Cross-experiment comparison — Prediction · ToU Cost · User Profiles · Recommendations</p>
</header>

<div class="kpi-row">
  <div class="kpi">
    <div class="label">Best Model R²</div>
    <div class="value" style="color:var(--accent)">{best_r2}</div>
    <div class="sub">{best_model_name}</div>
  </div>
  <div class="kpi">
    <div class="label">ToU Saving</div>
    <div class="value" style="color:var(--accent3)">{tou_saving_pct:.1f}%</div>
    <div class="sub">Off-peak optimisation</div>
  </div>
  <div class="kpi">
    <div class="label">Best User Profile</div>
    <div class="value" style="color:var(--accent2);font-size:1.1rem;padding-top:0.5rem">{best_profile}</div>
    <div class="sub">Highest model accuracy</div>
  </div>
  <div class="kpi">
    <div class="label">Rec. Avg Saving</div>
    <div class="value" style="color:var(--accent3)">{rec_saving_pct:.1f}%</div>
    <div class="sub">RM {total_saving_rm:.4f} total</div>
  </div>
</div>

<div class="grid">

  <!-- EXP 1: Model R² -->
  <div class="card">
    <h3>EXP 1 — Model Prediction Performance</h3>
    <canvas id="chart1"></canvas>
    <table style="margin-top:1rem">
      <tr><th>Model</th><th>MAE</th><th>RMSE</th><th>R²</th><th>MAPE%</th></tr>
      {"".join(f"<tr><td class='{'best' if r['Model']==best_model_name else ''}'>{r['Model']}</td><td>{r['MAE']}</td><td>{r['RMSE']}</td><td class='{'best' if r['Model']==best_model_name else ''}'>{r['R²']}</td><td>{r['MAPE%']}</td></tr>" for r in exp1_json)}
    </table>
  </div>

  <!-- EXP 2: ToU Cost -->
  <div class="card">
    <h3>EXP 2 — ToU Cost Comparison</h3>
    <canvas id="chart2"></canvas>
    <table style="margin-top:1rem">
      <tr><th>Zone</th><th>Normal (RM)</th><th>Optimized (RM)</th><th>Saving (RM)</th><th>Saving%</th></tr>
      {"".join(f"<tr><td>{r['Unnamed: 0']}</td><td>{r['normal']}</td><td>{r['optimized']}</td><td class='best'>{r['saving']}</td><td>{r['saving%']}%</td></tr>" for r in exp2z_json)}
    </table>
  </div>

  <!-- EXP 3: User Profiles -->
  <div class="card">
    <h3>EXP 3 — User Profile Comparison</h3>
    <canvas id="chart3"></canvas>
    <table style="margin-top:1rem">
      <tr><th>Profile</th><th>Avg Power (kW)</th><th>Daily Cost (RM)</th><th>R²</th><th>MAPE%</th></tr>
      {"".join(f"<tr><td class='{'best' if r['Profile']==best_profile else ''}'>{r['Profile']}</td><td>{r['Avg Power (kW)']}</td><td>{r['Est. Daily Cost (RM)']}</td><td>{r['R²']}</td><td>{r['MAPE%']}</td></tr>" for r in exp3_json)}
    </table>
  </div>

  <!-- EXP 4: Recommendations -->
  <div class="card">
    <h3>EXP 4 — Recommendation Effectiveness</h3>
    <canvas id="chart4"></canvas>
    <table style="margin-top:1rem">
      <tr><th>Recommendation</th><th>Before (RM)</th><th>After (RM)</th><th>Saving (RM)</th><th>Saving%</th></tr>
      {"".join(f"<tr><td>{r['recommendation']}</td><td>{r['Cost_Before_RM']}</td><td>{r['Cost_After_RM']}</td><td class='best'>{r['Saving_RM']}</td><td>{r['Saving_%']}%</td></tr>" for r in exp4_json)}
    </table>
  </div>

</div>

<script>
const ACCENT  = '#00d4aa';
const ACCENT2 = '#ff6b6b';
const ACCENT3 = '#ffd93d';
const MUTED   = '#3d4566';
const TEXT    = '#e8eaf6';
const gridColor = '#1e2235';

Chart.defaults.color = TEXT;
Chart.defaults.borderColor = gridColor;
Chart.defaults.font.family = "'DM Mono', monospace";

const exp1 = {json.dumps(exp1_json)};
const exp2z = {json.dumps(exp2z_json)};
const exp3 = {json.dumps(exp3_json)};
const exp4 = {json.dumps(exp4_json)};

// Chart 1 — Model R²
new Chart(document.getElementById('chart1'), {{
  type: 'bar',
  data: {{
    labels: exp1.map(d => d.Model),
    datasets: [
      {{ label: 'R²', data: exp1.map(d => d['R²']), backgroundColor: [ACCENT, MUTED, MUTED], borderRadius: 6 }},
      {{ label: 'MAE', data: exp1.map(d => d.MAE), backgroundColor: [ACCENT2, ACCENT2, ACCENT2], borderRadius: 6 }}
    ]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: TEXT }} }} }},
    scales: {{ x: {{ grid: {{ color: gridColor }} }}, y: {{ grid: {{ color: gridColor }} }} }} }}
}});

// Chart 2 — ToU Cost
new Chart(document.getElementById('chart2'), {{
  type: 'bar',
  data: {{
    labels: exp2z.map(d => d['Unnamed: 0']),
    datasets: [
      {{ label: 'Normal', data: exp2z.map(d => d.normal), backgroundColor: ACCENT2, borderRadius: 6 }},
      {{ label: 'Optimized', data: exp2z.map(d => d.optimized), backgroundColor: ACCENT, borderRadius: 6 }}
    ]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: TEXT }} }} }},
    scales: {{ x: {{ grid: {{ color: gridColor }} }}, y: {{ grid: {{ color: gridColor }}, title: {{ display: true, text: 'RM', color: TEXT }} }} }} }}
}});

// Chart 3 — Profile Daily Cost
new Chart(document.getElementById('chart3'), {{
  type: 'bar',
  data: {{
    labels: exp3.map(d => d.Profile),
    datasets: [
      {{ label: 'Daily Cost (RM)', data: exp3.map(d => d['Est. Daily Cost (RM)']), backgroundColor: [ACCENT, MUTED, MUTED, MUTED, MUTED, MUTED], borderRadius: 6 }},
      {{ label: 'R²', data: exp3.map(d => d['R²']), backgroundColor: ACCENT3, borderRadius: 6, yAxisID: 'y2' }}
    ]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: TEXT }} }} }},
    scales: {{
      x: {{ grid: {{ color: gridColor }} }},
      y: {{ grid: {{ color: gridColor }}, title: {{ display: true, text: 'RM', color: TEXT }} }},
      y2: {{ position: 'right', grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: 'R²', color: TEXT }}, min: 0, max: 1 }}
    }} }}
}});

// Chart 4 — Recommendation Saving
new Chart(document.getElementById('chart4'), {{
  type: 'bar',
  data: {{
    labels: exp4.map(d => d.recommendation),
    datasets: [
      {{ label: 'Saving (RM)', data: exp4.map(d => d.Saving_RM), backgroundColor: [ACCENT2, ACCENT3, ACCENT], borderRadius: 6 }},
      {{ label: 'Saving %', data: exp4.map(d => d['Saving_%']), backgroundColor: [ACCENT2+'88', ACCENT3+'88', ACCENT+'88'], borderRadius: 6, yAxisID: 'y2' }}
    ]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: TEXT }} }} }},
    scales: {{
      x: {{ grid: {{ color: gridColor }} }},
      y: {{ grid: {{ color: gridColor }}, title: {{ display: true, text: 'RM', color: TEXT }} }},
      y2: {{ position: 'right', grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: '%', color: TEXT }} }}
    }} }}
}});
</script>
</body>
</html>"""

with open("summary_dashboard.html", "w") as f:
    f.write(html)

print("✅ HTML dashboard saved: summary_dashboard.html")
print("   → Open summary_dashboard.html in your browser to view the interactive dashboard")
print("\n🎉 Summary comparison DONE!")
