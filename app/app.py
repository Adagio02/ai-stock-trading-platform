from pathlib import Path
import streamlit as st
import pandas as pd
import yfinance as yf
import joblib
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="AI Stock Trading Platform", layout="wide")

st.title("AI Stock Trading Platform")
st.caption("Research and paper-trading dashboard. Not financial advice.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Live Prices",
    "Signals",
    "Backtest",
    "Model Metrics",
    "Risk Controls"
])

with tab1:
    st.header("Live Price Viewer")

    ticker = st.text_input("Ticker", "AAPL")

    live = yf.download(ticker, period="6mo", auto_adjust=True)

    if not live.empty:
        live = live.reset_index()

        if isinstance(live.columns, pd.MultiIndex):
            live.columns = [col[0] for col in live.columns]

        fig = px.line(
            live,
            x="Date",
            y="Close",
            title=f"{ticker} Closing Price"
        )

        st.plotly_chart(fig, use_container_width=True)

        latest_close = float(live["Close"].iloc[-1])
        st.metric("Latest Close", f"${latest_close:,.2f}")
    else:
        st.error("No live data found for this ticker.")

with tab2:
    st.header("Buy/Sell Signal")

    model_path = BASE_DIR / "Models" / "best_model.pkl"
    features_path = BASE_DIR / "Models" / "features.pkl"
    dataset_path = BASE_DIR / "Reports" / "final_dataset.csv"

    if model_path.exists() and dataset_path.exists():
        model = joblib.load(model_path)
        features = joblib.load(features_path)
        df = pd.read_csv(dataset_path)

        latest = df.iloc[[-1]]
        probability = model.predict_proba(latest[features])[:, 1][0]
        prediction = model.predict(latest[features])[0]

        st.metric("Probability of next-day increase", f"{probability:.1%}")

        if prediction == 1:
            st.success("Model signal: BUY / LONG")
        else:
            st.warning("Model signal: HOLD / NO TRADE")

        st.dataframe(latest[features])
    else:
        st.error("Train the model first: python Src/train_models.py")

with tab3:
    st.header("Backtest Results")

    backtest_path = BASE_DIR / "Reports" / "backtest_results.csv"
    metrics_path = BASE_DIR / "Reports" / "backtest_metrics.csv"

    if backtest_path.exists():
        bt = pd.read_csv(backtest_path)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bt["Date"], y=bt["Equity_Curve"], name="Strategy"))
        fig.add_trace(go.Scatter(x=bt["Date"], y=bt["Buy_Hold_Curve"], name="Buy & Hold"))
        fig.update_layout(title="Equity Curve")

        st.plotly_chart(fig, use_container_width=True)

        dd_fig = px.line(bt, x="Date", y="Drawdown", title="Strategy Drawdown")
        st.plotly_chart(dd_fig, use_container_width=True)

    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path)
        st.dataframe(metrics)

with tab4:
    st.header("Model Comparison")

    comparison_path = BASE_DIR / "Reports" / "model_comparison.csv"

    if comparison_path.exists():
        comparison = pd.read_csv(comparison_path)
        st.dataframe(comparison)

        fig = px.bar(
            comparison,
            x="Model",
            y="ROC AUC",
            title="Model ROC AUC Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No model comparison found.")

with tab5:
    st.header("Risk Management")

    account_equity = st.number_input("Account Equity", value=10000.0)
    risk_per_trade = st.slider("Risk per Trade", 0.001, 0.05, 0.01)
    max_leverage = st.slider("Max Leverage", 1.0, 2.0, 1.0)
    entry_price = st.number_input("Entry Price", value=100.0)
    stop_loss = st.number_input("Stop Loss Price", value=95.0)

    per_share_risk = abs(entry_price - stop_loss)
    risk_amount = account_equity * risk_per_trade

    if per_share_risk > 0:
        shares_by_risk = risk_amount / per_share_risk
        shares_by_leverage = (account_equity * max_leverage) / entry_price
        shares = int(min(shares_by_risk, shares_by_leverage))
    else:
        shares = 0

    st.metric("Suggested Position Size", f"{shares} shares")
    st.metric("Dollar Risk", f"${risk_amount:,.2f}")
    st.warning("This is for risk education and paper trading. Margin increases losses as well as gains.")