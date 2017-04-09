# -*- coding: utf-8 -*-
"""
Created on Sat Jan 07 21:46:38 2017
###########################################
###                                  ###### 
###        calculate Skew            ######
###     SKEW = VOL_OTMP-VOL_ATMC     ######
###                                  ######   
###########################################
@author: Lida Xu
"""

# import packages
import pandas as pd
import datetime
import calendar

def daily_skew(ivol_file):
    
    rawdate = ivol_file.split('.')[0].split('_')[2] #date of the file
    year = int(rawdate[0:4])  # year of the file
    month = int(rawdate[4:6]) # month of the file
    day = int(rawdate[6:8])   # day of the file         
    weekday = calendar.day_name[datetime.date(year, month, day).weekday()] # get the weekday of the file

    # read each file into dataframe
    df = pd.read_csv(ivol_file, index_col = 0)
    skew_list = []
    # calculate the skew
    for i in range(len(df)-1):
        now_symbol = df.loc[i]['UnderlyingSymbol']
        next_symbol = df.loc[i+1]['UnderlyingSymbol']
        if now_symbol == next_symbol :
            now_type = df.loc[i]['Type']
            next_type = df.loc[i+1]['Type']
            stock_price = df.loc[i]['UnderlyingPrice']
            if now_type == 'call' and next_type =='put':
                skew = df.loc[i+1]['IVOL'] - df.loc[i]['IVOL'] # skew = VOL_OTMP - OVL_ATMC
            if now_type == 'put' and next_type =='call':
                skew = df.loc[i]['IVOL'] - df.loc[i+1]['IVOL'] # skew = VOL_OTMP - OVL_ATMC
            # append symbol, stock_price and skew into list  
            skew_list.append([now_symbol, stock_price, skew])

    # transfer list into dataframe and output
    new_df = pd.DataFrame(skew_list)
    new_df.columns = ['Symbol', 'UnderlyingPrice', 'SKEW']
    # export file name, example: 20160801Tuesday.csv
    option_name = rawdate + weekday +'.csv'
    # new_df.to_csv(outpath + option_name)
    return (new_df, option_name)

def main():
    df, df_name = daily_skew('bb_options_20160813.csv') # this files is with calculated implied volatility, not the onriginal optio file
    df.to_csv(df_name)

if __name__ == '__main__':
    main()
 
