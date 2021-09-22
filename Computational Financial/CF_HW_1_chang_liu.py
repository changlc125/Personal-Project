'''

@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Student Name  : first last

@Date          : March 2021

A Simplified Bond Class

'''

import math
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from bisection_method import bisection
from math import exp, log
import enum
import calendar

from datetime import date

class DayCount(enum.Enum):
    DAYCOUNT_30360 = "30/360"
    DAYCOUNT_ACTUAL_360 = "Actual/360"
    DAYCOUNT_ACTUAL_ACTUAL = "Actual/Actual"

class PaymentFrequency(enum.Enum):
    ANNUAL     = "Annual"
    SEMIANNUAL = "Semi-annual"
    QUARTERLY  = "Quarterly"
    MONTHLY    = "Monthly"
    CONTINUOUS = "Continuous"

    
class Bond(object):
    '''
    term is maturity term in years
    coupon is the coupon in percent
    maturity date will be issue_date + term
    '''
    def __init__(self, issue_date, term, day_count, payment_freq, coupon, principal = 100):
        self.issue_date = issue_date
        self.term = term
        self.day_count = day_count
        self.payment_freq = payment_freq
        self.coupon = coupon
        self.principal = principal
        # internal data structures
        self.payment_times_in_year = []
        self.payment_dates = []
        self.coupon_payment = []
        self._calc()

    def _add_months(self, dt, n_months):
        return(dt + relativedelta(months = n_months))

    def _calc(self):
        # calculate maturity date
        self.maturity_date = self._add_months(self.issue_date, 12 * self.term)

        # calculate all the payment dates
        dt = self.issue_date
        while dt < self.maturity_date:
            if self.payment_freq == PaymentFrequency.ANNUAL:
                next_dt = self._add_months(dt, 12)
            elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
                next_dt = self._add_months(dt, 6)
            elif self.payment_freq == PaymentFrequency.QUARTERLY:
                next_dt = self._add_months(dt, 4)
            elif self.payment_freq == PaymentFrequency.MONTHLY:
                next_dt = self._add_months(dt, 1)
            else:
                raise Exception("Unsupported Payment frequency")
                
            if next_dt <= self.maturity_date:
                self.payment_dates.append(next_dt)
                
            dt = next_dt

        # calculate the future cashflow vectors
        if self.payment_freq == PaymentFrequency.ANNUAL:
            coupon_cf = self.principal * self.coupon 
        elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
            coupon_cf = self.principal * self.coupon / 2
        elif self.payment_freq == PaymentFrequency.QUARTERLY:
            coupon_cf = self.principal * self.coupon / 4 
        elif self.payment_freq == PaymentFrequency.MONTHLY:
            coupon_cf = self.principal * self.coupon / 12 
        else:
            raise Exception("Unsupported Payment frequency")
            
        self.coupon_payment = [ coupon_cf for i in range(len(self.payment_dates))]
        
        # calculate payment_time in years
        if self.payment_freq == PaymentFrequency.ANNUAL:
            period = 1
        elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
            period = 1/2
        elif self.payment_freq == PaymentFrequency.QUARTERLY:
            period = 1/4
        elif self.payment_freq == PaymentFrequency.MONTHLY:
            period = 1/12
        else:
            raise Exception("Unsupported Payment frequency")

        self.payment_times_in_year = [ period * (i+1) for i in range(len(self.payment_dates))]

    def get_previous_payment_date(self, as_of_date):
        '''
        return the previous payment date before as_of_date if as_of_date is after the first pay date
        if it is before first pay date, return the issue date
        '''
        if as_of_date < self.issue_date:
            return(None)
        elif as_of_date < self.payment_dates[0]:
            return(self.issue_date)
        else:
            i = 1
            while i < len(self.payment_dates):
                dt = self.payment_dates[i]
                if as_of_date <= dt:
                    return(self.payment_dates[i-1])
                else:
                    i += 1
            return(None)
            


class BondCalculator(object):
    '''
    Bond Calculator. 
    '''

    def __init__(self, pricing_date):
        self.pricing_date = pricing_date

    def calc_one_period_discount_factor(self, bond, yld):
        '''
        Calculate the one period discount factor
        ''' 
        # TODO:
        if bond.payment_freq == PaymentFrequency.ANNUAL:
            yld=yld
        elif bond.payment_freq == PaymentFrequency.SEMIANNUAL:
            yld=yld / 2
        elif bond.payment_freq == PaymentFrequency.QUARTERLY:
            yld=yld/ 4 
        elif bond.payment_freq == PaymentFrequency.MONTHLY:
            yld=yld / 12 
        else:
            raise Exception("Unsupported Payment frequency")
        df = 1/(1+yld)

        return(df)


    def calc_clean_price(self, bond, yld):
        '''
        Calculate the price of the bond as of the pricing_date for a given yield
        as a percentage
        '''
        # TODO:
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        DF = [math.pow(one_period_factor, i+1) for i in range(len(bond.coupon_payment))]
        CF = [c for c in bond.coupon_payment]
        CF[-1] += bond.principal
        PVs = [ CF[i] * DF[i] for i in range(len(bond.coupon_payment))]
        px=sum(PVs)
        return(px)

    def calc_accrual_interest(self, bond, settle_date):
        '''
        calculate the accrual interest on given a settle_date
        by calculating the previous payment date first and use the date count
        from previous payment date to the settle_date
        '''
        index =0
        if bond.payment_freq == PaymentFrequency.ANNUAL:
            index = bond.term * 1
            period=12
        elif bond.payment_freq == PaymentFrequency.SEMIANNUAL:
            index = bond.term * 2
            period=6
        elif bond.payment_freq == PaymentFrequency.QUARTERLY:
            index = bond.term * 4
            period=3
        elif bond.payment_freq == PaymentFrequency.MONTHLY:
            index = bond.term * 12
            period=1
        else:
            raise Exception("Unsupported Payment frequency")
            
        pmt_date = None
        maturity_date = bond._add_months(bond.issue_date, 12 * bond.term)
        if settle_date < bond.issue_date or settle_date > maturity_date:
            raise Exception("Wrong settle_date")
        
        else:
            i = 0
            while i < len(bond.payment_dates):
                dt1 = bond.payment_dates[i]
                dt2 = bond.payment_dates[i+1]
                if settle_date >bond.issue_date and settle_date < dt1:
                    pmt_date = dt1 - relativedelta(months = period)
                    break
                elif settle_date >= dt1 and settle_date < dt2 :
                    pmt_date = bond.payment_dates[i]
                    break
                else:
                    i += 1           
         
        def get_actual360_daycount_frac(start, end):
            day_in_year = 360
            day_count = (end - start).days
            return(day_count / day_in_year)
        
        def get_30360_daycount_frac(start, end):
            day_in_year = 360
            day_count = 360*(end.year - start.year) + 30*(end.month - start.month - 1) + \
            max(0, 30 - start.day) + min(30, end.day)
            return(day_count / day_in_year )
        
        import calendar
        def get_actualactual_daycount_frac(start_date, end_date):
            day_count = (end_date - start_date).days
            year_days = 366 if calendar.isleap(int(str(end_date.year))) else 365
            return(day_count / year_days) 
            
#            pass
    
        if bond.day_count == DayCount.DAYCOUNT_30360:
            ratio = get_30360_daycount_frac(pmt_date, settle_date)
        elif bond.day_count == DayCount.DAYCOUNT_ACTUAL_360:
            ratio = get_actual360_daycount_frac(pmt_date, settle_date)
        elif bond.day_count == DayCount.DAYCOUNT_ACTUAL_ACTUAL:
            ratio = get_actualactual_daycount_frac(pmt_date, settle_date)
        else:
            raise Exception("Unsupported DayCount")
            
            
#         print(ratio)  
        result = bond.principal*bond.coupon * ratio
        return(result)

    def calc_macaulay_duration(self, bond, yld):
        '''
        time to cashflow weighted by PV
        '''
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        DF = [math.pow(one_period_factor, i+1) for i in range(len(bond.coupon_payment))]
        CF = [c for c in bond.coupon_payment]
        CF[-1] += bond.principal
        PVs = [ CF[i] * DF[i] for i in range(len(bond.coupon_payment))]
        
        # TODO:
        # wavg = ....
        wavg = [ CF[i] * bond.payment_times_in_year[i]* DF[i] for i in range(len(bond.coupon_payment))]
        return( sum(wavg) / sum(PVs))

    def calc_modified_duration(self, bond, yld):
        '''
        calculate modified duration
        '''
        D = self.calc_macaulay_duration(bond, yld)
        # TODO:
        #if bond.payment_freq == PaymentFrequency.ANNUAL:
        #    return(D/(1+yld))
        # elif bond.payment_freq == PaymentFrequency.SEMIANNUAL:
        # ...
        r = self.calc_one_period_discount_factor(bond, yld)
        result = D*r
        return(result)

    def calc_yield(self, bond, bond_price):
        '''
        Calculate the yield to maturity on given a bond price using bisection method
        '''
        
        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            # TODO: 
            one_period_factor = self.calc_one_period_discount_factor(bond, yld)
            DF = [math.pow(one_period_factor, i+1) for i in range(len(bond.coupon_payment))]
            CF = [c for c in bond.coupon_payment]
            CF[-1] += bond.principal
            PVs = [ CF[i] * DF[i] for i in range(len(bond.coupon_payment))]
            px=sum(PVs)
            return(px - bond_price)

        # call the bisection method
        # TODO:
        yld, n_iteractions = bisection(match_price,0,1,eps=1.0e-6)
        return(yld)

    def calc_convexity(self, bond, yld):
        '''
        Calculate the convexity
        '''
        #TODO
        
        bond_price = self.calc_clean_price(bond, yld)
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        DF = [math.pow(one_period_factor, i+1) for i in range(len(bond.coupon_payment))]
        CF = [c for c in bond.coupon_payment]
        CF[-1] += bond.principal
        v1= [ CF[i] *bond.payment_times_in_year[i]**2*exp(-yld*bond.payment_times_in_year[i]) for i in range(len(bond.coupon_payment))]
        v2=sum(v1)
        return(v2 / bond_price)


