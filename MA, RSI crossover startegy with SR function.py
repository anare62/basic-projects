import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd

class MovingAverageRSIStrategy:

    def __init__(self, capital, stock, start, end, short_period, long_period):
        self.data = None
        self.is_long = False
        self.short_period = short_period
        self.long_period = long_period
        self.capital = capital
        self.equity = [capital]
        self.stock = stock
        self.start = start
        self.end = end

    def download_data(self):
        self.data = yf.download(self.stock, self.start, self.end)
        # fix multiindex columns from yfinance
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.droplevel(1)
        self.data = self.data[['Close']]
        return pd.DataFrame(self.data)
    
    def construct_signals(self):
        # EWMA
        self.data['short_ma'] = self.data['Close'].ewm(span=self.short_period).mean()
        self.data['long_ma'] = self.data['Close'].ewm(span=self.long_period).mean()
        # RSI
        self.data['move'] = self.data['Close'] - self.data['Close'].shift(1)
        self.data['up'] = np.where(self.data['move'] > 0, self.data['move'], 0)
        self.data['down'] = np.where(self.data['move'] < 0, -self.data['move'], 0)
        self.data['average_gain'] = self.data['up'].rolling(14).mean()
        self.data['average_loss'] = self.data['down'].rolling(14).mean()
        relative_strength = self.data['average_gain'] / self.data['average_loss']
        self.data['rsi'] = 100.0 - (100.0 / (1.0 + relative_strength))
        self.data = self.data.dropna()
        print(self.data)

    def plot_signals(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data['Close'], label='Stock Price')
        plt.plot(self.data['short_ma'], label='Short MA', c='b')
        plt.plot(self.data['long_ma'], label='Long MA', c='g')
        plt.title('Moving Average (MA) crossover strategy with RSI')
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.show()

    def simulate(self):
        
        price_when_buy = 0

        for index, row in self.data.iterrows():
            # close the long pos.
            if row['short_ma'] < row['long_ma'] and self.is_long:
                self.equity.append(self.equity[-1] * row['Close'] / price_when_buy)
                self.is_long = False
                # print('sell')
            elif row['short_ma'] > row['long_ma'] and not self.is_long and row['rsi'] < 20:
                # open the long pos.
                price_when_buy = row['Close']
                self.is_long = True
                # print('buy')
        if self.is_long:
            final_price = self.data['Close'].iloc[-1]
            self.equity.append(self.equity[-1] * final_price / price_when_buy)

    def plot_equity(self):

        plt.figure(figsize=(12, 6))
        plt.title('Equity Curve')
        plt.plot(self.equity, label='Stock Price', c='g')
        plt.xlabel('Date')
        plt.ylabel('Actual Capital ($)')
        plt.show()

    def show_stats(self, rfr=0.0):
        print('Profit (return) of the trading strategy %.2f%%' % (
            (float(self.equity[-1]) - float(self.equity[0])) /
            float(self.equity[0]) * 100))
        print('Actual capital: %.2f' % self.equity[-1])        
        returns = (self.data['Close'] - self.data['Close'].shift(1)) / self.data['Close'].shift(1)
        ratio = (returns.mean() - rfr) / returns.std() * np.sqrt(252)
        print('Sharpe ratio: %.2f' % ratio)

if __name__ == '__main__':

    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)

    model = MovingAverageRSIStrategy(100, 'IBM', start_date, end_date, 40, 150)
    model.download_data()
    model.construct_signals()
    model.plot_signals()
    model.simulate()
    model.plot_equity()
    model.show_stats()
    