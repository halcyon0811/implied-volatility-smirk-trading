# -*- coding: utf-8 -*-
"""
Created on Fri Jan 06 21:53:07 2017
###############################################
###                                    ######## 
###  Calculate Call Implied Volatility ########
###     and Put Implied Volatility     ########
###                                    ########   
###############################################
@author: Lida Xu
"""

# Load packages
import numpy as np
from scipy.stats import norm
import pandas as pd
import datetime
import math


######################################### || Define Some Functions || ####################################################################
def est_vega(S, K, r, sigma, T):
    """ Define a function to calculate the vega
        which is also the derivative of option with respect to sigma
    """    
    d = (np.log(S/K) + (r + 0.5 * sigma* sigma)* T) / (sigma * np.sqrt(T))
    vega = S * np.sqrt(T) * norm.pdf(d)
    
    return vega
    
def BS_call(S, K, r, sigma, T):
    """Define a function of Black_Scholes for call option(without dividend)
    """
    d1 = (np.log(S / K) + (r + 0.5 * np.power(sigma, 2))* T) / sigma / np.sqrt(T)
    d2 = d1 - sigma*np.sqrt(T)        
    C = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return C

def BS_put(S, K, r, sigma, T):
    """ Define a function of Black_Scholes for put option(without dividend)
    """
    d1 = (np.log(S / K) + (r + 0.5 * np.power(sigma, 2)) * T) / sigma / np.sqrt(T)
    d2 = d1 - sigma*np.sqrt(T)                
    P = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return P
    
def IV_call_newton_raphson(price_market, S, K, r, sigma, T):   
    """Define newton_raphson method to estimate the implied volatitly for call option  
    """
    n    = 0 # For run times
    # Check the difference between market price and BS price
    diff    = abs(price_market - BS_call(S, K, r, sigma, T)) 
    sigmas  = [] # initial sigmas list for saving the calculated volatility
    BS_diff = [] # initial a list for saving difference between market price and BS price 

    while ( abs(diff) > 0.001): # accuracy is round to third decimal place
        diff = price_market - BS_call(S, K, r, sigma, T) #difference between market price and BS price
        sigmas.append(sigma) # save volatility to 'sigmas' list
        BS_diff.append(abs(diff)) # save difference to 'BS_diff' list
        sigma = (diff)/est_vega(S, K, r, sigma, T) + sigma  #Newton_Raphson way to update the sigma
        n = n + 1
        if math.isnan(sigma):
            break
        if n > 10e3:  # if run times are greater than 1000, break, since it may not converge
            break
    if len(sigmas) > 0:
        # Get the relative correct IV
        # Search min difference, then get the corresponding sigma
        sigma = sigmas[BS_diff.index(min(BS_diff))] 
        
    return sigma

def IV_put_newton_raphson(price_market, S, K, r, sigma, T):
    """ Define newton_raphson method to estimate the implied volatitly for put option  
    """
    n = 0 # For rum times
    diff = abs(price_market - BS_put(S, K, r, sigma, T))
    # Check the difference between market price and BS price
    sigmas = []
    BS_diff = []
    while ( abs(diff) > 0.001):
        diff = price_market - BS_put(S, K, r, sigma, T)
        sigmas.append(sigma)
        BS_diff.append(abs(diff))
        sigma = (diff)/est_vega(S, K, r, sigma, T) + sigma
        n = n + 1
        if math.isnan(sigma):
            break
        if n > 10e3: # if run times are greater than 1000, break
            break
    if len(sigmas):
        # Get the relative correct IV
        # Search min difference, then get the corresponding sigma
        sigma = sigmas[BS_diff.index(min(BS_diff))]  
        
    return sigma


def count_day(startdate, enddate):
    """# Define a function to count the days to expiration
    """
    start = datetime.datetime(year=int(startdate[6:10]), month=int(startdate[0:2]), day=int(startdate[3:5]))
    end = datetime.datetime(year=int(enddate[6:10]), month=int(enddate[0:2]), day=int(enddate[3:5]))
    delta = end - start
    return delta.days

    
######################################### || Main Code Part || ####################################################################
def IVOL(raw_df, sp500list_df, r, check_prog = False):
    """
    """
    new_list = [] # this is to store list information of each option in the file   
    # Get the current day's s&p500 components
    sp500list = sp500list_df['Ticker'].tolist()        
    df = raw_df
    total  = len(df) # total options in the file
    K_call = []
    T_call = []
    Price_call = []
    K_put = []
    T_put = []
    Price_put = [] # initialize the list for next stock's option
    for i in range(total-1):
        # This loop for each option in the file
        try:
            now_symbol = df.loc[i]['UnderlyingSymbol'] # get the option's underlyingstock symbol
            # if underlying stock is in the sp500 list, then ok
            if now_symbol in sp500list: 
                volume = df.loc[i]['Volume'] # Get the daily trading volume of the option
                last = df.loc[i]['Last'] # Get the market last price of the option
                Type = df.loc[i]['Type'] # Get the option's type, call or put
                liq = count_day(df.loc[i]['DataDate'], df.loc[i]['Expiration']) # count how many days to expiration
                next_symbol = df.loc[i+1]['UnderlyingSymbol'] # get the next option's underlyingstock symbol
                app = (now_symbol != next_symbol) # check whether the next _symbol equals to now_symbol, app is True, if they are not equal, otherwise, app is false 
                
                # if symbols are same, option is liquid(have volumes and market last price) and days to expiration are between 30 days to 60 days
                # store suitable options' strike, days to expiration(in year unit) and market last option price into list
                # if symbols are different, which means options are for a different underlying stock. or next option reaches the end
                # then if the next option is the last, append the next option in the list
                # based on the list, calculate the defined skew.
                if app == False and volume != 0 and last != 0 and liq >= 10.0 and liq <= 60.0:
                    if Type == 'call':
                        K_call.append(float(df.loc[i]['Strike'])) # Get Option strike price
                        T_call.append( liq / 365.0)  # Get day to expiration
                        Price_call.append(last) # Market price for option
                    if Type == 'put':
                        K_put.append(float(df.loc[i]['Strike'])) # Get Option strike price
                        T_put.append(liq/ 365.0)  # Get day to expiration
                        Price_put.append(last) # Market price for option
                if app == True or (i+1 == total):
                    if i+1 == total: 
                        if Type == 'call':
                            K_call.append(float(df.loc[i+1]['Strike'])) # Get Option strike price
                            T_call.append( liq / 365.0)  # Get day to expiration
                            Price_call.append(last) # Market price for option
                        if Type == 'put':
                            K_put.append(float(df.loc[i+1]['Strike'])) # Get Option strike price
                            T_put.append(liq/ 365.0)  # Get day to expiration
                            Price_put.append(last) # Market price for option
                    s = df.loc[i]['UnderlyingPrice'] # Get the underlying stock price
                    ticker = df.loc[i]['UnderlyingSymbol'] # Get the underlying stock price
                    for types in ['call', 'put']:
                        # Defined ATMC is a call option when the ratio of strike price to the stock price is between 0.95 and 1.05
                        # In the code, ATMC is to find the minimum difference between strike and sport price 
                        if types =='call':
                            s_to_k_call = [abs(x-s) for x in K_call] # subtract strik by spot price, take absolute value 
                            min_indx = s_to_k_call.index(min(s_to_k_call)) # find where is the strike is close to the spot price
                            k = K_call[min_indx] # find the corresponding strike
                            t = T_call[min_indx] # find the corresponding time to expiration
                            price = Price_call[min_indx] # find the corresponding market last price
                            Call_IV = IV_call_newton_raphson(price, s, k, r, 0.3, t) # Calculate Implied volatility, initial volatility is 0.3
                            bs_price = BS_call(s, k, r, Call_IV, t) # based on the calulated Implied volatility to get the option price in BS formula
                            new_list.append([ticker, types, s, k, t, price, bs_price, Call_IV]) # store information into a list
                        # Defined OTMP is a put option when the ratio of strike price to the stock price
                        # is lower than 0.95(but higher than 0.80)  
                        # In the code, OTMP is to find the strike to spot ratio closest to 0.95, but not bigger than 0.95
                        # the method is to let 0.95 minus strike to spot ratio for each strike in K_put list,
                        # then find the minimum one when the difference is positive
                        if types == 'put':
                            s = df.loc[i]['UnderlyingPrice'] 
                            s_to_k_put = [(0.95-x/s) for x in K_put] #0.95 minus strike to spot ratio for each strike in K_put list
                            min_indx = s_to_k_put.index(min([putotm for putotm in s_to_k_put if putotm >0])) # find the index of the minimum one when the difference is positive
                            k = K_put[min_indx]
                            t = T_put[min_indx]
                            price = Price_put[min_indx]
                            Put_IV = IV_put_newton_raphson(price, s, k, r, 0.3, t) # Implied volatility
                            bs_price = BS_put(s, k, r, Put_IV, t)
                            new_list.append([ticker, types, s, k, t, price, bs_price, Put_IV]) # store information into a list
                            
                    K_call = []
                    T_call = []
                    Price_call = []
                    K_put = []
                    T_put = []
                    Price_put = [] # initialize the list for next stock's option 
                
                if check_prog == True:
                    # To check the progress
                    print("---------------------"+str(total-i)+" Left-------------------")    
        except :
            pass
            
    new_df = pd.DataFrame(new_list) # transfer the newlist into dataframe
    # Name the columns of the dataframe
    new_df.columns = ['UnderlyingSymbol','Type','UnderlyingPrice','Strike','ExpirDay','LastPrice','BSPrice','IVOL']    
    # new_df.to_csv(outpath + option_file)  # output the dataframe
    return new_df

def main():
    raw_df = pd.read_csv(sample_original_option_data.csv)
    sp500list = pd.read_CSv(sample_sp500list.csv)
    r = 0.0015
    df = IVOL(raw_df, sp500list_df, r)
    df.to_csv(sample_result.csv)


if ___name__ = '__main__':
    main()


     
    


