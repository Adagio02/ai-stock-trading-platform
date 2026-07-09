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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Live Prices",
    "Signals",
    "Backtest",
    "Model Metrics",
    "Risk Controls",
    "Portfolio Research"
])

with tab1:
    st.header("Live Price Viewer")

    tickers = st.multiselect(
        "Choose Stocks",
        ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "SPY", "QQQ"],
        default=["AAPL", "MSFT"]
    )

    period = st.selectbox(
        "Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )

    for ticker in tickers:
        df = yf.download(
            ticker,
            period=period,
            auto_adjust=True
        )

        if df.empty:
            st.warning(f"No data available for {ticker}")
            continue

        df = df.reset_index()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()

        st.subheader(f"{ticker} Price Chart")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Close"
        ))

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["SMA_20"],
            mode="lines",
            name="20-Day Moving Average"
        ))

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["SMA_50"],
            mode="lines",
            name="50-Day Moving Average"
        ))

        fig.update_layout(
            title=f"{ticker} Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        latest_close = float(df["Close"].iloc[-1])
        st.metric(f"{ticker} Latest Close", f"${latest_close:,.2f}")

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
        st.error("Model files are missing. Run training locally, or add model training to the deployed app.")

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

with tab6:
    st.header("Portfolio Research Dashboard")

    if (BASE_DIR / "Reports" / "market_signals.csv").exists():
        st.subheader("Market Screener")
        signals = pd.read_csv(BASE_DIR / "Reports" / "market_signals.csv")
        st.dataframe(signals, use_container_width=True)

    if (BASE_DIR / "Reports" / "optimized_portfolio.csv").exists():
        st.subheader("Optimized Portfolio")
        portfolio = pd.read_csv(BASE_DIR / "Reports" / "optimized_portfolio.csv")
        st.dataframe(portfolio, use_container_width=True)
        st.bar_chart(portfolio.set_index("Ticker")["Weight"])

    if (BASE_DIR / "Reports" / "walk_forward_results.csv").exists():
        st.subheader("Walk-Forward Equity Curve")
        wf = pd.read_csv(BASE_DIR / "Reports" / "walk_forward_results.csv")
        st.line_chart(wf.set_index("Date")["Equity_Curve"])

    if (BASE_DIR / "Reports" / "performance_metrics.csv").exists():
        st.subheader("Performance Metrics")
        metrics = pd.read_csv(BASE_DIR / "Reports" / "performance_metrics.csv")
        st.dataframe(metrics)

    if (BASE_DIR / "Reports" / "shap_summary.png").exists():
        st.subheader("SHAP Feature Importance")
        st.image(str(BASE_DIR / "Reports" / "shap_summary.png"))