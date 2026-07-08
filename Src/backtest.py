import joblib
import pandas as pd
from pathlib import Path


Path("Reports").mkdir(exist_ok=True)

df = pd.read_csv("Reports/final_dataset.csv")

model = joblib.load("Models/best_model.pkl")
features = joblib.load("Models/features.pkl")

df["Prediction"] = model.predict(df[features])
df["Probability"] = model.predict_proba(df[features])[:, 1]

df["Market_Return"] = df["Close"].pct_change()
df["Strategy_Return"] = df["Prediction"].shift(1) * df["Market_Return"]

df["Equity_Curve"] = (1 + df["Strategy_Return"].fillna(0)).cumprod()
df["Buy_Hold_Curve"] = (1 + df["Market_Return"].fillna(0)).cumprod()

df["Peak"] = df["Equity_Curve"].cummax()
df["Drawdown"] = (df["Equity_Curve"] - df["Peak"]) / df["Peak"]

total_return = df["Equity_Curve"].iloc[-1] - 1
max_drawdown = df["Drawdown"].min()
win_rate = (df["Strategy_Return"] > 0).mean()

metrics = pd.DataFrame([{
    "Total Return": total_return,
    "Max Drawdown": max_drawdown,
    "Win Rate": win_rate,
}])

df.to_csv("Reports/backtest_results.csv", index=False)
metrics.to_csv("Reports/backtest_metrics.csv", index=False)

print(metrics)