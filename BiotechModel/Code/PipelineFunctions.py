
'''
Pipeline functions that didn't fit neatly into a single category
'''
import pandas as pd 
import numpy as np 
import random
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt

'''
Inputs: headlines (dataframe), stocks (dictionary of dataframe), 
	days_before event (int), days_after event (int)
Outputs: event_log ()
'''
def GetHeadlineHistory(headline_data, stock_data, days_before, days_after):
	event_logs = []
	headline_length = headline_data.shape[0]
	headline_data['Stock_prices'] = pd.Series(pd.DataFrame())
	for row_num in range(headline_length):
		stock_date = headline_data['Stock_date'].iloc[row_num]
		security = headline_data['Security'].iloc[row_num]
		headline = headline_data['Headline'].iloc[row_num]
		stock_info = stock_data[security]
		date_idx_array = np.where(stock_info['Iso_date'] == stock_date)
		if len(date_idx_array[0]) == 0:
			i = 1
			while len(date_idx_array[0]) == 0:
				stock_date_fromiso = date.fromisoformat(stock_date)
				stock_date_fromiso += timedelta(days=1)
				stock_date = stock_date_fromiso.isoformat()
				date_idx_array = np.where(stock_info['Iso_date'] == stock_date)
				i += 1
				if i > 10:
					#print('exceeded range')
					event_logs.append(np.nan)
					break
		if len(date_idx_array[0]) != 0:
			date_idx = int(date_idx_array[0])
			records = stock_info.iloc[date_idx-days_after:date_idx+days_before,:]
			event_logs.append(records)
	return event_logs

'''
Function for plotting out the stock price data. Writes out plots to file as a png.
'''
def PlotRandomStockJumps(headline_data, stock_data, random=True):
	from textwrap import wrap
	sample_headlines = pd.DataFrame()
	sample_len = headline_data.shape[0]
	if random == True:
		for i in range(sample_len):
			sample_num = random.randint(0,headline_data.shape[0]-1)
			sample = headline_data.iloc[sample_num, :]
			sample_headlines = sample_headlines.append(sample)
	else:
		for i in range(sample_len):
			sample = headline_data.iloc[i, :]
			sample_headlines = sample_headlines.append(sample)
	event_log = GetHeadlineHistory(sample_headlines, stock_data, 15, 15)
	for j in range(sample_len):
		plt.clf()
		fig = plt.figure()
		ax = fig.add_subplot(111)
		try:
			new_dates = list(event_log[j]['Iso_date'].apply(datetime.fromisoformat))
		except TypeError:
			continue
		plt.plot(new_dates , event_log[j][' Open'])
		head_title = sample_headlines['Headline'].iloc[j]
		#idx_avg = np.mean(event_log[j].index) + 0.5
		if len(new_dates) > 0:
			idx_avg = new_dates[len(new_dates)//2]
			plt.axvline(x = idx_avg, color='r')
		plt.xticks(rotation=45)
		title = ax.set_title("\n".join(wrap(head_title, 60)))
		plt.xlabel('Date')
		plt.ylabel('Opening Price ($)')
		# these are matplotlib.patch.Patch properties
		#props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		# place a text box in upper left in axes coords
		#ax.text(.51, 0.95, 'Headline Announced', transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
		plt.tight_layout()
		filename = 'stock_' + str(j) + '.png'
		plt.savefig(filename)
		plt.close(fig)



'''
200107 Update: Completely remade Event Result function to better reflect real world scenario
New Description:
This function creates multiple columns of the difference between the opening price of the stock the day (or first 
day of an open stock market after) that the news broke and various conditions reached afterward.
The columns described are as follows:
Boolean 'success': True/False whether an arbitrary return is reached on an opening price within 10 trading days
Highest price reached within 10 trading days: self explanatory
More to be added as needed 

Inputs: headline dataframe, stocks dictionary of dataframes. 
outputs: Dataframe of two numerical columns that should be appended to the headline dataframe. 
'''


def DefineEventResult(headline_data, stock_data):
	days_after = 9 # number of days away from headline event
	days_before = 0
	success_threshold = 1.075
	event_logs = GetHeadlineHistory(headline_data, stock_data, days_before, days_after)
	print(len(event_logs))
	result_cols = []
	for i in range(len(event_logs)):
		stock_sample = event_logs[i].loc[:, ' Open']
		if len(stock_sample) != 0:
			before_prices = stock_sample.iloc[days_before]
			after_prices = stock_sample.iloc[days_before+1:]
			normalized_difference = after_prices / before_prices
			success_bool = (sum(normalized_difference > success_threshold) > 0)
			highest_return = np.max(normalized_difference)
		else:
			normalized_difference = 0
			success_bool = False
			highest_return = 0
		result_cols.append([success_bool, highest_return])
	result_df = pd.DataFrame(result_cols)
	result_df.columns = ['Success_Bool', 'Highest_Return']
	result_df.reset_index(inplace=True, drop=True)
	return result_df
