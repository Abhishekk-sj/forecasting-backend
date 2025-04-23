import pandas as pd
from pandas.tseries.offsets import MonthEnd, QuarterEnd

def run_forecast(df, method, period, freq):
    if df.empty or df.shape[1] < 2:
        raise ValueError("Data must have at least two columns: Date and Value")

    # Convert to datetime and strip time
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'])

    # Aggregate based on frequency
    if freq == 'daily':
        df = df.groupby('Date')['Value'].sum().reset_index()
    elif freq == 'weekly':
        df['Date'] = df['Date'] - pd.to_timedelta(df['Date'].dt.weekday, unit='d')
        df = df.groupby('Date')['Value'].sum().reset_index()
    elif freq == 'monthly':
        df['Date'] = df['Date'] + MonthEnd(0)
        df = df.groupby('Date')['Value'].sum().reset_index()
    elif freq == 'quarterly':
        df['Date'] = df['Date'] + QuarterEnd(0)
        df = df.groupby('Date')['Value'].sum().reset_index()
    elif freq == 'yearly':
        df['Date'] = df['Date'].dt.to_period('Y').dt.to_timestamp()
        df = df.groupby('Date')['Value'].sum().reset_index()
    else:
        raise ValueError("Invalid frequency selected.")

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

    # Generate future forecast
    last_date = df['Date'].max()
    freq_offset = {'daily': 'D', 'weekly': 'W-MON', 'monthly': 'M', 'quarterly': 'Q', 'yearly': 'A'}[freq]
    future_dates = pd.date_range(last_date, periods=period + 1, freq=freq_offset)[1:]

    # Use last rolling average as forecast
    last_forecast = df['Forecast'].iloc[-1]
    future_df = pd.DataFrame({'Date': future_dates, 'Forecast': [last_forecast] * period})

    combined = pd.concat([df[['Date', 'Forecast']], future_df])
    forecast_list = combined.tail(period).to_dict(orient='records')
    return forecast_list
