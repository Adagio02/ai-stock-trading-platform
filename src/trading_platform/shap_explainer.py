import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

Path("Reports").mkdir(exist_ok=True)

model = joblib.load("Models/best_model.pkl")
features = joblib.load("Models/features.pkl")
df = pd.read_csv("Reports/final_dataset.csv")

X = df[features].tail(200)

final_model = model.named_steps["model"]
scaler = model.named_steps["scaler"]

X_scaled = scaler.transform(X)

explainer = shap.Explainer(final_model)
shap_values = explainer(X_scaled)

shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
plt.savefig("Reports/shap_summary.png")
plt.close()

print("SHAP summary saved.")