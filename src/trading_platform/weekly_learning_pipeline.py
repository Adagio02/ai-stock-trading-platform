from trading_platform.data_updater import download_latest_data
from trading_platform.market_screener import main as run_screener
from trading_platform.model_retrainer import retrain_candidate_model
from trading_platform.model_evaluator import evaluate_candidate
from trading_platform.model_promoter import promote_if_approved


def main():
    print("Step 1: Downloading latest data...")
    download_latest_data()

    print("Step 2: Running market screener...")
    run_screener()

    print("Step 3: Retraining candidate model...")
    retrain_candidate_model()

    print("Step 4: Evaluating candidate model...")
    evaluate_candidate()

    print("Step 5: Promoting model if approved...")
    promote_if_approved()

    print("Weekly learning pipeline complete.")


if __name__ == "__main__":
    main()