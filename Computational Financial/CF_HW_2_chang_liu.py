'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Student Name  : first last

@Date          : April 2021

A Simple Option Pricer Class

'''
import enum
import calendar
import math
import pandas as pd
import numpy as np

from datetime import date
from scipy.stats import norm

from math import log, exp, sqrt

class Stock(object):
    '''
    mu is the expected return
    sigma is the volatility of the stock
    dividend_yield is the continous dividend yield paid by the stock
    '''
    def __init__(self, symbol, spot_price, sigma, mu, dividend_yield = 0):
        self.symbol = symbol
        self.spot_price = spot_price
        self.sigma = sigma
        self.mu = mu 
        self.dividend_yield = dividend_yield

class Option(object):
    '''
    time_to_expiry is the number of days till expiry_date expressed in unit of years
    underlying is the underlying stock object
    '''

    class Type(enum.Enum):
        CALL = "Call"
        PUT  = "Put"

    class Style(enum.Enum):
        EUROPEAN = "European"
        AMERICAN = "American"

    def __init__(self, option_type, option_style,  underlying, time_to_expiry, strike):
        self.option_type = option_type
        self.option_style = option_style
        self.underlying = underlying
        self.time_to_expiry = time_to_expiry
        self.strike = strike

class EuropeanCallOption(Option):
    def __init__(self, underlying, time_to_expiry, strike):
        Option.__init__(self, Option.Type.CALL, Option.Style.EUROPEAN,
                        underlying, time_to_expiry, strike)

class EuropeanPutOption(Option):
    def __init__(self, underlying, time_to_expiry, strike):
        Option.__init__(self, Option.Type.PUT, Option.Style.EUROPEAN,
                        underlying, time_to_expiry, strike)

class AmericanCallOption(Option):
    def __init__(self, underlying, time_to_expiry, strike):
        Option.__init__(self, Option.Type.CALL, Option.Style.AMERICAN,
                        underlying, time_to_expiry, strike)

class AmericanPutOption(Option):
    def __init__(self, underlying, time_to_expiry, strike):
        Option.__init__(self, Option.Type.PUT, Option.Style.AMERICAN,
                        underlying, time_to_expiry, strike)


class OptionPricer(object):
    '''
    Option Pricer for calculating option price using either Binomial or Black-Scholes Model
    '''

    def __init__(self, pricing_date, risk_free_rate):
        self.pricing_date = pricing_date
        self.risk_free_rate = risk_free_rate
      
        
    def _binomial_european_call(self, S_0, K, T, r, sigma, q, N):
        '''
        Calculate the price of an European call using Binomial Tree
        S_0 - stock price today
        K - strike price of the option
        T - time to expiry in unit of years
        r - risk-free interest rate
        sigma - the volatility of the stock
        q - the continous dividend yield of the stock
        N - number of periods in the tree
        '''
        dt = T/N
        u =  exp(sigma * sqrt(dt))
        d = 1/u
#         d=0.9
        prob = (exp((r-q) * dt) - d)/(u - d)
        C = {}
        for m in range(0, N+1):
            S_T = S_0 * (u ** (2*m - N))
            C[(N, m)] = max(S_T - K, 0)
        for k in range(N-1, -1, -1):
            for m in range(0, k+1):
                C[(k, m)] = exp(-r * dt)*(prob*C[(k+1, m+1)]+(1-prob)*C[(k+1, m)]) 

        return C[(0,0)]        

    def _binomial_european_put(self, S_0, K, T, r, sigma, q, N):
        '''
        Calculate the price of an European put using Binomial Tree
        S_0 - stock price today
        K - strike price of the option
        T - time to expiry in unit of years
        r - risk-free interest rate
        sigma - the volatility of the stock
        q - the continous dividend yield of the stock
        N - number of steps in the model
        '''
        dt = T/N
        u =  exp(sigma * sqrt(dt))
        d = 1/u
#         d = 0.9
        prob = (exp((r - q) * dt) - d)/(u - d)
        P = {}

        for m in range(0, N+1):
            S_T = S_0 * (u ** (2*m - N))
            P[(N, m)] = max(K-S_T, 0)
#         P[(N, 0)] = 19
#         P[(N, 1)] = 1
#         P[(N, 2)] = 0
        for k in range(N-1, -1, -1):
            for m in range(0, k+1):
                P[(k, m)] = exp(-r * dt)*(prob*P[(k+1, m+1)]+(1-prob)*P[(k+1, m)])
                    
        return P[(0,0)]        

    def _binomial_american_call(self, S_0, K, T, r, sigma, q, N):
        '''
        Calculate the price of an American call using Binomial Tree
        S_0 - stock price today
        K - strike price of the option
        T - time until expiry of the option
        r - risk-free interest rate
        sigma - the volatility of the stock
        q - the continous dividend yield of the stock
        N - number of steps in the model
        '''
        dt = T/N
        u =  exp(sigma * sqrt(dt))
        d = 1/u
        prob = (exp( (r-q) * dt) - d)/(u - d)
        
        C = {}
        for m in range(0, N+1):
            S_T = S_0 * (u ** (2*m - N))
            C[(N, m)] = max(S_T - K, 0)
#             print(C[(N, m)])      
        for k in range(N-1, -1, -1):
            for m in range(0,k+1):
                # TODO: fill in the blank here
                # hint the stock price at the (k, m) node is 
                # S_t = S_0 * (u ** m * d ** (k-m) = u ** ( 2m - k) as d = 1/u
                # end TODO
                S_t = S_0 * (u ** m * d ** (k-m) )
                C[(k, m)] = (prob*C[(k+1, m+1)]+(1-prob)*C[(k+1, m)]) *exp(-r * dt)
                early_exercise = S_t - K     
                if early_exercise > C[(k, m)]:
                      C[(k, m)] =  early_exercise 
#                 print(C[(k, m)]) 
                
        return C[(0,0)]        

    def _binomial_american_put(self, S_0, K, T, r, sigma, q, N):
        '''
        Calculate the price of an American put using Binomial Tree
        S_0 - stock price today
        K - strike price of the option
        T - time to expiry in unit of years
        r - risk-free interest rate
        sigma - the volatility of the stock
        N - number of steps in the model
        '''
        dt = T/N
        u =  exp(sigma * sqrt(dt))
        d = 1/u
        prob = (exp((r-q) * dt) - d)/(u - d) 
        
        P = {}

        for m in range(0, N+1):
            S_T = S_0 * (u ** (2*m - N))
            P[(N, m)] = max(K-S_T, 0)
#             print(P[(N, m)])                 
        for k in range(N-1, -1, -1):
            for m in range(0, k+1):
                P[(k, m)] = (prob*P[(k+1, m+1)]+(1-prob)*P[(k+1, m)])*exp(-r * dt)
                S_t = S_0 * (u ** m * d ** (k-m) ) 
                early_exercise = K-S_t
                if early_exercise > P[(k, m)]:
                      P[(k, m)] =  early_exercise  
#                 print(P[(k, m)] )
           

                    
        return P[(0,0)]        
        

    def calc_binomial_model_price(self, option, num_of_period):
        '''
        Calculate the price of the option using num_of_period Binomial Model 
        '''
        if option.option_type == Option.Type.CALL and option.option_style == Option.Style.EUROPEAN:
            px = self._binomial_european_call(option.underlying.spot_price, option.strike, option.time_to_expiry, self.risk_free_rate, 
                                              option.underlying.sigma, option.underlying.dividend_yield, num_of_period)
        elif option.option_type == Option.Type.PUT and option.option_style == Option.Style.EUROPEAN:
            px = self._binomial_european_put(option.underlying.spot_price, option.strike, option.time_to_expiry, self.risk_free_rate, 
                                             option.underlying.sigma, option.underlying.dividend_yield, num_of_period)
        elif option.option_type == Option.Type.CALL and option.option_style == Option.Style.AMERICAN:
            px = self._binomial_american_call(option.underlying.spot_price, option.strike, option.time_to_expiry, self.risk_free_rate, 
                                              option.underlying.sigma, option.underlying.dividend_yield, num_of_period)
        elif option.option_type == Option.Type.PUT and option.option_style == Option.Style.AMERICAN:
            px = self._binomial_american_put(option.underlying.spot_price, option.strike, option.time_to_expiry, self.risk_free_rate, 
                                             option.underlying.sigma, option.underlying.dividend_yield, num_of_period)

        return(px)


    def calc_parity_price(self, option, option_price):
        '''
        return the put price from Put-Call Parity if input option is a call
        else return the call price from Put-Call Parity if input option is a put
        '''
        result = None
        if option.option_type == Option.Type.CALL:
            call_side = option_price + option.strike *exp(-self.risk_free_rate * option.time_to_expiry)
            result = call_side-option.underlying.spot_price*exp(-option.underlying.dividend_yield * option.time_to_expiry)
          
        else:
            put_side = option_price +option.underlying.spot_price*exp(-option.underlying.dividend_yield * option.time_to_expiry)
            result = put_side-option.strike *exp(-self.risk_free_rate * option.time_to_expiry)
            
        return(result)

    def calc_black_scholes_price(self, option):
        '''
        Calculate the price of the call or put option using Black-Scholes model
        '''
        px = None
        if option.option_style == Option.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        else:
                S0 = option.underlying.spot_price
                T = option.time_to_expiry
                q = option.underlying.dividend_yield
                K = option.strike
                symb = option.underlying.symbol
                sigma = option.underlying.sigma
                mu = option.underlying.mu
                r = self.risk_free_rate
                d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
                d2 = d1 - sigma*sqrt(T)
                if option.option_type == Option.Type.CALL:
                    px = S0*exp(-q*T)*norm.cdf(d1)-K*exp(-r*T)*norm.cdf(d2)
                else:
#                     option.option_type == Option.Type.PUT
                      px = K*exp(-r*T)*norm.cdf(-d2)-S0*exp(-q*T)*norm.cdf(-d1)      
        return(px)


    def calc_delta(self, option):
        result = None
        S0 = option.underlying.spot_price
        T = option.time_to_expiry
        q = option.underlying.dividend_yield
        K = option.strike
        symb = option.underlying.symbol
        sigma = option.underlying.sigma
        mu = option.underlying.mu
        r = self.risk_free_rate
        d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
        if option.option_type == Option.Type.CALL:
            result = exp(-q**T)*norm.cdf(d1)
        else:
#           option.option_type == Option.Type.PUT
            result = exp(-q**T)*(norm.cdf(d1)-1)
        return(result)

    def calc_gamma(self, option):
        result = None
        S0 = option.underlying.spot_price
        T = option.time_to_expiry
        q = option.underlying.dividend_yield
        K = option.strike
        symb = option.underlying.symbol
        sigma = option.underlying.sigma
        mu = option.underlying.mu
        r = self.risk_free_rate
        d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
        result = (norm.pdf(d1) *exp(-q*T))/(S0*sigma * sqrt(T))
        return(result)

    def calc_theta(self, option):
        result = None
        S0 = option.underlying.spot_price
        T = option.time_to_expiry
        q = option.underlying.dividend_yield
        K = option.strike
        symb = option.underlying.symbol
        sigma = option.underlying.sigma
        mu = option.underlying.mu
        r = self.risk_free_rate
        d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        if option.option_type == Option.Type.CALL:
            result = ((-S0 *norm.pdf(d1) *sigma*exp(-q*T))/(2*sqrt(T)))+q*S0*norm.cdf(d1)*exp(-q*T)-r*K*exp(-r*T)*norm.cdf(d2)
        else:
#           option.option_type == Option.Type.PUT
            result = ((-S0 *norm.pdf(d1) *sigma*exp(-q*T))/(2*sqrt(T)))-q*S0*norm.cdf(-d1)*exp(-q*T)+r*K*exp(-r*T)*norm.cdf(-d2)
        return(result)

    def calc_vega(self, option):
        result = None
        S0 = option.underlying.spot_price
        T = option.time_to_expiry
        q = option.underlying.dividend_yield
        K = option.strike
        symb = option.underlying.symbol
        sigma = option.underlying.sigma
        mu = option.underlying.mu
        r = self.risk_free_rate
        d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
        result = S0*sqrt(T)*norm.pdf(d1)*exp(-q*T)
        return(result)

    def calc_rho(self, option):
        result = None
        S0 = option.underlying.spot_price
        T = option.time_to_expiry
        q = option.underlying.dividend_yield
        K = option.strike
        symb = option.underlying.symbol
        sigma = option.underlying.sigma
        mu = option.underlying.mu
        r = self.risk_free_rate
        d1 = (log(S0/K)+(r-q+pow(sigma,2)/2)*T)/(sigma * sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        if option.option_type == Option.Type.CALL:
            result = K*T*exp(-r*T)*norm.cdf(d2)
        else:
#           option.option_type == Option.Type.PUT
            result = -K*T*exp(-r*T)*norm.cdf(-d2)
        return(result)





