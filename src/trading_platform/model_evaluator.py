from pathlib import Path
import pandas as pd

REPORTS_DIR = Path("Reports")


def evaluate_candidate():
    current_path = REPORTS_DIR / "model_comparison.csv"
    candidate_path = REPORTS_DIR / "candidate_model_metrics.csv"

    if not current_path.exists():
        raise FileNotFoundError("Missing Reports/model_comparison.csv")

    if not candidate_path.exists():
        raise FileNotFoundError("Missing Reports/candidate_model_metrics.csv")

    current = pd.read_csv(current_path)
    candidate = pd.read_csv(candidate_path)

    current_best_auc = current["ROC AUC"].max()
    candidate_auc = candidate["ROC AUC"].iloc[0]

    print(f"Current best ROC AUC: {current_best_auc:.4f}")
    print(f"Candidate ROC AUC: {candidate_auc:.4f}")

    improvement = candidate_auc - current_best_auc

    decision = "REJECT"

    if improvement > 0.01:
        decision = "PROMOTE"

    result = pd.DataFrame([{
        "Current ROC AUC": current_best_auc,
        "Candidate ROC AUC": candidate_auc,
        "Improvement": improvement,
        "Decision": decision
    }])

    result.to_csv(REPORTS_DIR / "model_evaluation_decision.csv", index=False)

    print(result)


if __name__ == "__main__":
    evaluate_candidate()