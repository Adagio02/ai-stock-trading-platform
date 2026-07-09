import pandas as pd
import yfinance as yf
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

Path("Reports").mkdir(exist_ok=True)

ticker = "AAPL"

df = yf.download(ticker, period="5y", auto_adjust=True, progress=False).reset_index()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] for col in df.columns]

df["Return"] = df["Close"].pct_change()
df["SMA_20"] = df["Close"].rolling(20).mean()
df["SMA_50"] = df["Close"].rolling(50).mean()
df["Volatility"] = df["Return"].rolling(20).std()
df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
df = df.dropna()

features = ["Return", "SMA_20", "SMA_50", "Volatility"]

window = 500
step = 30

rows = []

for start in range(0, len(df) - window - step, step):
    train = df.iloc[start:start + window]
    test = df.iloc[start + window:start + window + step]

    X_train = train[features]
    y_train = train["Target"]

    X_test = test[features]
    y_test = test["Target"]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(n_estimators=200, random_state=42))
    ])

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    test = test.copy()
    test["Prediction"] = preds
    test["Strategy_Return"] = test["Prediction"].shift(1) * test["Return"]

    rows.append(test)

results = pd.concat(rows)
results["Equity_Curve"] = (1 + results["Strategy_Return"].fillna(0)).cumprod()
results["Peak"] = results["Equity_Curve"].cummax()
results["Drawdown"] = (results["Equity_Curve"] - results["Peak"]) / results["Peak"]

results.to_csv("Reports/walk_forward_results.csv", index=False)

print("Walk-forward complete.")