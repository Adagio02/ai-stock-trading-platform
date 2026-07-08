import joblib
import pandas as pd
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from xgboost import XGBClassifier

from trading_platform.data import download_data
from trading_platform.trading_platform.features import add_features


Path("Models").mkdir(exist_ok=True)
Path("Reports").mkdir(exist_ok=True)

ticker = "AAPL"

df = download_data(ticker, period="5y")
df = add_features(df)

features = [
    "Return",
    "SMA_10",
    "SMA_50",
    "Volatility",
    "RSI",
    "MACD",
    "Signal",
]

X = df[features]
y = df["Target"]

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    ),
    "XGBoost": XGBClassifier(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    ),
}

results = []
trained_models = {}

for name, model in models.items():
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", model),
    ])

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1]

    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1": f1_score(y_test, y_pred),
        "ROC AUC": roc_auc_score(y_test, y_proba),
    })

    trained_models[name] = pipe

results_df = pd.DataFrame(results).sort_values("ROC AUC", ascending=False)
results_df.to_csv("Reports/model_comparison.csv", index=False)

best_model_name = results_df.iloc[0]["Model"]
best_model = trained_models[best_model_name]

joblib.dump(best_model, "Models/best_model.pkl")
joblib.dump(best_model_name, "Models/best_model_name.pkl")
joblib.dump(features, "Models/features.pkl")

df.to_csv("Reports/final_dataset.csv", index=False)

print(results_df)
print(f"Best model: {best_model_name}")