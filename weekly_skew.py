# -*- coding: utf-8 -*-
"""
Created on Sun Jan 08 01:03:44 2017
#################################################
###                                        ###### 
###       Clalculate weely average skews   ######
###          Tuesday to Tuesday            ######
###                                        ######   
#################################################
@author: Lida Xu
"""

from os import listdir
from os.path import isfile, join
import re
import pandas as pd


def weekly_skew(inpath, outpath, Weekday = 'Tuesday'):
    outpath = outpath + ''+ Weekday + '_to_' + Weekday + '/'
    option_files = [f for f in listdir(inpath) if isfile(join(inpath, f))] # read files in the folder
    df_list = []  # initialize a list to store dataframes (Tuesday to Tuesday)
    name_list = []  # initialize a list to store the years in the Tuesday to Tuesday

    app = False
    for indx in range(len(option_files)):
        # keep reading files in the folder, and append the information into df_list and name_list
        rawdate = re.split('(\d+)', option_files[indx])[1] # the date of the file
        weekday = re.split('(\d+)', option_files[indx])[2].split('.')[0] # the weekday of the file
        df_list.append(pd.read_csv(inpath + option_files[indx], index_col = 0)) # append df into list
        name_list.append(rawdate) 
        
        # weekday is same as Weekday
        # Then app is True
        if weekday == Weekday:
            app = True
        # If app is True, then calculate the average SKEWs
        if app == True:
            temple = df_list[0] # initialize a temple, later for dataframe merging
            for i in range(1,len(df_list)):
                # merge dataframes in the df_list based on 'Symbol' column
                temple = pd.merge(temple, df_list[i], on = 'Symbol') 
            
            # After the first Tuesday, when meet the next Tuesday, then merge temple with the previous Tuesday 
            if indx >= 4:
                # the Previous Tueday index = current index -  length of the df_list 
                temple = pd.merge(temple, pd.read_csv(inpath + option_files[indx-len(df_list)], index_col = 0), on = 'Symbol')
                # update the name_list
                name_list.append(re.split('(\d+)', option_files[indx-len(df_list)])[1])
               
            # calculate the averag_skew    
            average_skew = []
            col_lens = len(temple.columns)
            for i in range(len(temple)):
                sum_skew = 0.0
                for j in range(2, col_lens, 2):
                    sum_skew = sum_skew + temple.loc[i][j]
                average_skew.append(sum_skew/len(range(2, col_lens, 2)))
            
            # Create an average_skew column in the dataframe
            temple['average_skew'] = average_skew
            # sort the dataframe based on the average_skew column, from smallest to biggest
            temple = temple.sort('average_skew', ascending = 1)
            temple.index = range(len(temple))  # reindex the temple dataframe
            
            # After the first Tuesday, name should from the previous Tuesday date to current Tuesday date
            # otherwise, the name is just the startdate to the first Tuesday
            if indx >= 4:
                name = name_list[-1] + '_' + name_list[-2] + '_' + Weekday + '_to_' + Weekday
            else:
                name = name_list[0] + '_' + name_list[-1] + '_' + Weekday + '_to_' + Weekday

            # export dataframe 
            temple.to_csv(outpath + name +'.csv')
            # initialize df_list, name_list and app
            df_list = []
            name_list = []
            app = False


