from pathlib import Path
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MODELS_DIR = Path("Models")
REPORTS_DIR = Path("Reports")

MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


FEATURES = [
    "Return",
    "SMA_20",
    "SMA_50",
    "Volatility",
    "Return_5D",
    "Return_20D"
]


def build_features(df):
    df = df.copy()

    df["Return"] = df.groupby("Ticker")["Close"].pct_change()
    df["SMA_20"] = df.groupby("Ticker")["Close"].transform(lambda x: x.rolling(20).mean())
    df["SMA_50"] = df.groupby("Ticker")["Close"].transform(lambda x: x.rolling(50).mean())
    df["Volatility"] = df.groupby("Ticker")["Return"].transform(lambda x: x.rolling(20).std())
    df["Return_5D"] = df.groupby("Ticker")["Close"].pct_change(5)
    df["Return_20D"] = df.groupby("Ticker")["Close"].pct_change(20)

    df["Future_Close"] = df.groupby("Ticker")["Close"].shift(-1)
    df["Target"] = (df["Future_Close"] > df["Close"]).astype(int)

    df = df.dropna()

    return df


def retrain_candidate_model():
    data_path = REPORTS_DIR / "all_market_data.csv"

    if not data_path.exists():
        raise FileNotFoundError("Run data_updater.py first.")

    df = pd.read_csv(data_path)
    df = build_features(df)

    X = df[FEATURES]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    metrics = {
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds, zero_division=0),
        "Recall": recall_score(y_test, preds, zero_division=0),
        "F1": f1_score(y_test, preds, zero_division=0),
        "ROC AUC": roc_auc_score(y_test, probs)
    }

    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(REPORTS_DIR / "candidate_model_metrics.csv", index=False)

    joblib.dump(model, MODELS_DIR / "candidate_model.pkl")
    joblib.dump(FEATURES, MODELS_DIR / "candidate_features.pkl")

    print("Candidate model trained.")
    print(metrics_df)


if __name__ == "__main__":
    retrain_candidate_model()