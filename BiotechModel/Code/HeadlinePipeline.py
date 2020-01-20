#This is currently the main pipeline script
#This script will not work as it calls packages I have not uploaded, this is mainly for viewing purposes.

#Import libraries
import pandas as pd
import numpy as np
import scipy as sp
import LoadFiles
from datetime import datetime, date, timedelta
import StockFeaturePrepare as sfp
from PipelineFunctions import GetHeadlineHistory, DefineEventResult
import random
import matplotlib.pyplot as plt

#Setup crude prediction pipeline
from sklearn.preprocessing import normalize, robust_scale
from sklearn.model_selection import KFold, cross_val_score, cross_validate, cross_val_predict
from sklearn.linear_model import ElasticNetCV
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix

#Load files
headlines = LoadFiles.LoadHeadlines()
companies = LoadFiles.LoadCompanies()
stocks = LoadFiles.LoadStocks()

#Convert datetime of manual headlines to be compatible with stock data
datey = headlines.loc[:,'Date'].astype(str)
new_date = datey.apply(lambda x: datetime.strptime('20' + x, '%Y%m%d').strftime('%Y-%m-%d'))
headlines['Stock_date'] = new_date

#Addition to the theme of this addition
for stock_key in list(stocks.keys()):
	stock_dates = stocks[stock_key].loc[:,'Date'].astype(str)
	new_date = stock_dates.apply(lambda x: datetime.strptime(x,'%m/%d/%y').strftime('%Y-%m-%d'))
	stocks[stock_key]['Iso_date'] = new_date

#Create logs cont.
event_logs = GetHeadlineHistory(headlines,stocks,30,0)
headlines['Stock_prices'] = event_logs
headlines.dropna(inplace=True)

#Add informational features to the dataframe
stock_data_series = headlines['Stock_prices'].map(sfp.GetTimeComputes).apply(pd.Series)
stock_data_df = pd.DataFrame(stock_data_series)
stock_data_df.iloc[:,54] = robust_scale(stock_data_df.iloc[:,54]) #Beware the magic numbers here
headlines = pd.concat([headlines, stock_data_df.iloc[:,:55]], axis=1) #Same as above

#Add result columns
headlines.reset_index(inplace=True, drop=True)
result_columns = DefineEventResult(headlines, stocks)
headlines = pd.concat([headlines, result_columns], axis=1)

#Setup data specifically for sklearn pipeline
#Local variables that made sense in context of jupyter notebook
first_column = 'Success_Bool' #Column that is first after numeric data [Indexing purposes]
results_column = 'Success_Bool' #Which column to take as the results vector
dropna_thresh = headlines.shape[1] - 1 #one or two headlines get dropped for not having available stock prices
headlines.dropna(inplace=True, thresh=dropna_thresh)
training_data = headlines.loc[:,'Stock_prices':first_column]
training_data.drop(columns=['Stock_prices', first_column], inplace=True)
training_data['Phase'] = headlines.loc[:,'Phase']
training_data['TextSent'] = headlines.loc[:,'TextSent']
training_results = np.ravel(headlines.loc[:,results_column] * 1) # *1 is for encoding, may cause bugs if results_column changed

#Setup sklearn objects
kf = KFold(n_splits=5, shuffle=True, random_state=42)
regr = SVC(kernel='linear') #For the gist of it. Local script differs. 

#Testing follows and code following this changes from run to run and thus is not included.

