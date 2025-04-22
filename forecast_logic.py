import pandas as pd

def run_forecast(df, method, period):
    # Basic validation
    if df.empty or df.shape[1] < 2:
        raise ValueError("Data must have at least two columns: Date and Value")

    # Ensure Date column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])  # drop rows where date conversion failed
    df = df.sort_values('Date')

    if method == 'sma':
        df['Forecast'] = df['Value'].rolling(window=period).mean()
    
    elif method == 'wma':
        weights = range(1, period + 1)
        df['Forecast'] = df['Value'].rolling(window=period).apply(
            lambda x: sum(w * val for w, val in zip(weights, x)) / sum(weights),
            raw=True
        )
    
    else:
        raise ValueError(f"Unsupported method: {method}")

    # Drop rows with NaNs (e.g., due to initial rolling periods)
    df = df.dropna(subset=['Forecast'])

    # Return the last 10 forecasted results
    forecast_list = df[['Date', 'Forecast']].tail(10).to_dict(orient='records')
    return forecast_list
