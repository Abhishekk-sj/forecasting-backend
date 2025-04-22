# Inside forecast_logic.py

import pandas as pd

def aggregate_data(df, frequency):
    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Aggregate data by frequency (weekly, monthly, etc.)
    if frequency == 'weekly':
        df.set_index('Date', inplace=True)
        df = df.resample('W').sum().reset_index()
    elif frequency == 'monthly':
        df.set_index('Date', inplace=True)
        df = df.resample('M').sum().reset_index()
    elif frequency == 'quarterly':
        df.set_index('Date', inplace=True)
        df = df.resample('Q').sum().reset_index()
    elif frequency == 'yearly':
        df.set_index('Date', inplace=True)
        df = df.resample('Y').sum().reset_index()
    else:
        # Default is daily if no frequency is selected
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    return df
# Inside forecast_logic.py

def run_forecast(df, method, period, frequency):
    # Aggregate data based on frequency
    df = aggregate_data(df, frequency)
    
    # Ensure that we have the required columns
    if df.empty or df.shape[1] < 2:
        raise ValueError("Data must have at least two columns")

    df.columns = ['Date', 'Value']
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # Apply SMA or WMA as chosen
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
