import pandas as pd

def run_forecast(df, method, period):
    if df.empty or df.shape[1] < 2:
        raise ValueError("Data must have at least two columns")

    df.columns = ['Date', 'Value']
    df['Date'] = pd.to_datetime(df['Date'])
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
        raise ValueError("Unsupported method")

    df = df.dropna()
    forecast_list = df[['Date', 'Forecast']].tail(10).to_dict(orient='records')
    return forecast_list