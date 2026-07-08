import pandas as pd
from trading_platform.features import add_features

def test_add_features_creates_target():
    df = pd.DataFrame({
        "Close": [100, 101, 102, 103, 104, 105] * 20,
        "High": [101, 102, 103, 104, 105, 106] * 20,
        "Low": [99, 100, 101, 102, 103, 104] * 20,
        "Open": [100, 101, 102, 103, 104, 105] * 20,
        "Volume": [1000000] * 120
    })

    result = add_features(df)

    assert "Target" in result.columns
    assert "RSI" in result.columns