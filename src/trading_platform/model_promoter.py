from pathlib import Path
import shutil
import pandas as pd

MODELS_DIR = Path("Models")
REPORTS_DIR = Path("Reports")


def promote_if_approved():
    decision_path = REPORTS_DIR / "model_evaluation_decision.csv"

    if not decision_path.exists():
        raise FileNotFoundError("Run model_evaluator.py first.")

    decision = pd.read_csv(decision_path)

    if decision["Decision"].iloc[0] != "PROMOTE":
        print("Candidate rejected. Keeping current model.")
        return

    shutil.copy(MODELS_DIR / "candidate_model.pkl", MODELS_DIR / "best_model.pkl")
    shutil.copy(MODELS_DIR / "candidate_features.pkl", MODELS_DIR / "features.pkl")

    print("Candidate promoted to production model.")


if __name__ == "__main__":
    promote_if_approved()