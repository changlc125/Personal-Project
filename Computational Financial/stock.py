# CSCI 365/765 Pang HW0
# reference: https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4
# https://github.com/JECSand/yahoofinancials

# make sure you install yfinance and yahoofinancials first by
# pip install yfinance
# pip install yahoofinancials

import enum
import calendar
import math
import pandas as pd
import numpy as np

import datetime 
from scipy.stats import norm

from math import log, exp, sqrt

from yahoofinancials import YahooFinancials 

class Stock(object):
    '''
    mu is the expected return
    sigma is the volatility of the stock
    dividend_yield is the continous dividend yield paid by the stock
    '''
    def __init__(self, symbol, sigma = None, mu = None, dividend_yield = 0):
        self.symbol = symbol
        self.sigma = sigma
        self.mu = mu 
        self.dividend_yield = dividend_yield

        self.yfinancial = YahooFinancials(symbol)
        self.ohlcv_df = None

    def get_daily_hist_price(self, start_date, end_date):
        '''
        Get historical OHLC_V dataframe
        '''
        data = self.yfinancial.get_historical_price_data(start_date.strftime("%Y-%m-%d"), 
                                                         end_date.strftime("%Y-%m-%d"), 
                                                         'daily')

        self.ohlcv_df = pd.DataFrame(data[self.symbol]['prices']).set_index('formatted_date')

    def calc_returns(self):
        '''
        '''
        self.ohlcv_df['prev_close'] = self.ohlcv_df['close'].shift(1)
        self.ohlcv_df['returns'] = (self.ohlcv_df['close'] - self.ohlcv_df['prev_close'])/ \
                                        self.ohlcv_df['prev_close']
        
        
    def get_summary_data(self):
        data = self.yfinancial.get_summary_data()
        return(data[self.symbol])



def _test():
    symbol = 'AAPL'
    stock = Stock(symbol)
    start_date = datetime.date(2019, 1, 1)
    end_date = datetime.date.today()

    stock.get_daily_hist_price(start_date, end_date)

    print(stock.ohlcv_df.head())

    print(stock.get_summary_data())
    
    print("Market Cap ", stock.yfinancial.get_market_cap())
    print("Beta ", stock.yfinancial.get_beta())

    print("current price ", stock.yfinancial.get_current_price())

    print("current volume ", stock.yfinancial.get_current_volume())
    print("10 days avg daily volume ", stock.yfinancial.get_ten_day_avg_daily_volume())

if __name__ == "__main__":
    _test()
