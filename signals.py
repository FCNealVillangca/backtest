import pandas as pd
import pandas_ta as ta
from backtesting import Strategy, Backtest, lib


class MACDSignal():
    def __init__(self, df):
        self.df = df

    def cross_signal(self, col1, col2):
        signals = pd.Series(0, index=self.df.index)
        # Generate buy signals (1) when col1 crosses above col2
        signals[(col1 > col2) & (col1.shift(1) <= col2.shift(1))] = 1
        # Generate sell signals (-1) when col1 crosses below col2
        signals[(col1 < col2) & (col1.shift(1) >= col2.shift(1))] = -1
        
        return signals

    def make_signal(self, fast=12, slow=26, signal=9):
        # Calculate the number of rows to drop based on the longest period
        drop_rows = max(fast, slow, signal)
        # Calculate MACD indicators
        macd = ta.macd(self.df['Close'], fast=12, slow=26, signal=9)
        # Remove initial NaN values and reset index
        macd = macd.iloc[(drop_rows-1):]
        macd = macd.reset_index(drop=True)
        # Combine original dataframe with MACD indicators
        new = pd.concat([self.df, macd], axis=1)
        # Generate cross signals based on MACD and Signal line
        cross_signal = self.cross_signal(new['MACD_12_26_9'], new['MACDs_12_26_9'])
        # Add the cross signals to the dataframe
        result = new.assign(Signal=cross_signal)
        # Convert 'Time' column to datetime format
        result['Time'] = pd.to_datetime(result['Time'])
        # Remove any duplicate timestamps, keeping the first occurrence
        result = result.drop_duplicates(subset='Time', keep='first')
        # Set 'Time' as the index of the dataframe
        result.set_index('Time', inplace=True)
        # Ensure the index is sorted in chronological order
        result = result.sort_index()
        return result
