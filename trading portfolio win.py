# -*- coding: utf-8 -*-
"""
Created on Sun Jan 08 16:35:59 2017

@author: Lida Xu
"""
from yahoo_finance import Share
from os import listdir
from os.path import isfile, join
import pandas as pd
import datetime

def yahoo_price(df, position, position_index, startdate, enddate, records):
    stock_list = []
    skew_list = []
    for j in position_index:
        stock_list.append(df.loc[j]['Symbol'])
        skew_list.append(df.loc[j]['average_skew'])
    
    for i  in range(len(stock_list)):
        try:
            pre = float(Share(stock_list[i]).get_historical(startdate, startdate)[0]['Adj_Close'])
            after = float(Share(stock_list[i]).get_historical(enddate, enddate)[0]['Adj_Close'])
            records.append([stock_list[i], skew_list[i], startdate, enddate, position, pre, after])
        
        except Exception as message:
            print(stock_list[i], message)
            
    return records

def  portfolio_construct(option_files, inpath, check_prog = False):         
	Days = []  # For SPX benchmark
	records = []
	for indx in range(len(option_files)):
		end_raw = option_files[indx].split('_')[1]
		end_date =  datetime.datetime.strptime(end_raw, '%Y%m%d') + datetime.timedelta(days = 8) # forcast next week
		enddate = end_date.strftime('%Y-%m-%d')
		endday = end_date.strftime('%Y%m%d')
		start_date =  end_date - datetime.timedelta(days = 7)
		startdate = start_date.strftime('%Y-%m-%d')
		startday = start_date.strftime('%Y%m%d')
		Days.append(startday + '_' + endday)
		df = pd.read_csv(inpath + option_files[indx])
		
		long_index = range(int(len(df)/5.0))  #long the previous 1/5 stocks which has the small skew
		short_index = range(int(4.0*len(df)/5.0), len(df))
		
		records = yahoo_price(df, 'long', long_index, startdate, enddate, records)
		records = yahoo_price(df, 'short', short_index, startdate, enddate, records)
		
		if check_prog == True:
			print('-------------------------'+str(len(option_files)-indx)+' Left-------------------------------------')
			
	record_df = pd.DataFrame(records)
	record_df.columns = ['Ticker','Skew','startdate','enddate','position','pre','after']
	
	return record_df


def portfolio_summary(record_df):
	combo_pre = []
	pres =  record_df.loc[0, 'pre']
	afters = record_df.loc[0, 'after']
	for trade_indx in range(1, len(record_df)):
		
#		now_date = record_df.loc[trade_indx, 'startdate']
#		pre_date = record_df.loc[trade_indx-1, 'startdate']
		pre_end = record_df.loc[trade_indx-1, 'enddate']
		pos = record_df.loc[trade_indx, 'position']
		pre_pos  = record_df.loc[trade_indx-1, 'position']
		pr = record_df.loc[trade_indx, 'pre']
		af = record_df.loc[trade_indx, 'after']
		if pos == pre_pos:
			pres  = pres + pr
			afters = afters + af
		if pos != pre_pos:
			combo_pre.append([pre_end, pre_pos, pres, afters])
			pres =  record_df.loc[trade_indx, 'pre']
			afters =  record_df.loc[trade_indx, 'after']

	combo = pd.DataFrame(combo_pre)
	combo.columns = ['date','position','trades','results']
	
	return combo
	
def trade_sim(imoney, ihold, trades, results, position):

    irecords =[]
    
    for i in range(len(trades)):
        ishare = int(imoney * ihold / abs(trades[i]))
        imoney_ = imoney
        if position[i] == 'long':
            pos = 1.0
        if position[i] == 'short':
            continue
            
        imoney = imoney + ishare * (results[i] - trades[i]) * pos               
        ireturn = imoney / imoney_ - 1.0
        irecords.append([imoney_, imoney, trades[i], results[i], ishare, ireturn])
    
    df = pd.DataFrame(irecords)
    df.columns = ['Money Before Trade', 'Money After Trade','Premium','Payoff','Shares', 'Rerturn']
    return df

def main():
    Weekday = 'Tuesday'
    inpath = 'C:\\Users\\xulid\\Desktop\\IVOL Result\\Skew_'+ Weekday +'_to_'+Weekday+ '/'
    option_files = [f for f in listdir(inpath) if isfile(join(inpath, f))] # read files in the folder
    record_df = portfolio_construct(option_files, inpath)
    combo = portfolio_summary(record_df)
    # initial account 1 million, invest 90% of the account value each time.
    trades = combo['trades'].tolist()
    results = combo['results'].tolist()
    position = combo['position'].tolist()
    trade_result = trade_sim(10e6, 0.9, trades, results, position)

	
if __name__ == '__main__':
	main()
            
