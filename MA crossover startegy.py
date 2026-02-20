import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

class MovingAverageCrossover:

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
        ticker = yf.download(self.stock, self.start, self.end)
        self.data = pd.DataFrame(ticker)
        # fix multiindex columns from yfinance
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.droplevel(1)

    def construct_signals(self):
        self.data['short_ma'] = self.data['Close'].ewm(span=self.short_period).mean()
        self.data['long_ma'] = self.data['Close'].ewm(span=self.long_period).mean()
        self.data = self.data[['Close', 'short_ma', 'long_ma']]
        # print(self.data)

    def plot_signals(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.Close, label='Stock Price', c='k')
        plt.plot(self.data.short_ma, label='Short EWMA', c='b')
        plt.plot(self.data.long_ma, label='Long EWMA', c='g')
        plt.title('EW Moving Average (MA) Crossover Strategy')
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.legend()
        plt.show()

    def simulate(self):
        
        price_when_buy = 0

        for index, row in self.data.iterrows():
            # close the long pos.
            if row['short_ma'] < row['long_ma'] and self.is_long:
                self.equity.append(self.equity[-1] * row['Close'] / price_when_buy)
                self.is_long = False
                # print('sell')
            elif row['short_ma'] > row['long_ma'] and not self.is_long:
                # open the long pos.
                price_when_buy = row['Close']
                self.is_long = True
                # print('buy')
    
    def plot_equity(self):
        print('Profit (return) of the trading strategy %.2f%%' % (
            (float(self.equity[-1]) - float(self.equity[0])) /
            float(self.equity[0]) * 100))
        print('Actual capital: %.2f' % self.equity[-1])
        plt.figure(figsize=(12, 6))
        plt.title('Equity Curve')
        plt.plot(self.equity, label='Stock Price', c='g')
        plt.xlabel('Date')
        plt.ylabel('Actual Capital ($)')
        plt.show()
        
if __name__ == '__main__':

    start_date = datetime.datetime(2010,1,1)
    end_date = datetime.datetime(2020,1,1)

    strategy = MovingAverageCrossover(
        capital=100, 
        stock='IBM', 
        start=start_date, 
        end=end_date, 
        short_period=30, 
        long_period=50)
    
    strategy.download_data()
    strategy.construct_signals()
    # strategy.plot_signals()
    strategy.simulate()
    strategy.plot_equity()
    