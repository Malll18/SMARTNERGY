"""
run_all_experiments.py
Run all 4 experiments in sequence.
"""

import subprocess
import sys

experiments = [
    ("Experiment 1 — Prediction Performance",   "experiment1_prediction_performance.py"),
    ("Experiment 2 — ToU Cost Comparison",       "experiment2_tou_cost.py"),
    ("Experiment 3 — Different User Profiles",   "experiment3_user_profiles.py"),
    ("Experiment 4 — Recommendation Effectiveness", "experiment4_recommendation.py"),
]

print("=" * 60)
print("   Running ALL Experiments")
print("=" * 60)

for title, script in experiments:
    print(f"\n{'='*60}")
    print(f"  ▶  {title}")
    print(f"{'='*60}\n")
    result = subprocess.run([sys.executable, script], check=False)
    if result.returncode != 0:
        print(f"\n❌ {title} failed with exit code {result.returncode}")
    else:
        print(f"\n✅ {title} completed successfully")

print("\n" + "=" * 60)
print("  🎉  ALL EXPERIMENTS DONE!")
print("=" * 60)
print("\nOutput files generated:")
print("  experiment1_prediction.png | experiment1_results.csv")
print("  experiment2_tou_cost.png   | experiment2_hourly.csv | experiment2_zone_breakdown.csv")
print("  experiment3_user_profiles.png | experiment3_results.csv")
print("  experiment4_recommendation.png | experiment4_results.csv | experiment4_detail.csv")
