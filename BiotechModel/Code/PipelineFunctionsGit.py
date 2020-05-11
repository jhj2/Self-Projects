import pandas as pd 
import numpy as np 
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt 
import random 
import warnings
import json
from urllib.request import urlopen
import time

'''
Inputs: headlines (dataframe), stocks (dictionary of dataframe), 
	days_before event (int), days_after event (int)
Outputs: event_log ()
'''
def GetHeadlineHistory(headline_data, stock_data, days_before, days_after):
	event_logs = []
	headline_length = headline_data.shape[0]
	headline_data['Stock_prices'] = np.nan
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

#191215
#Prepare results section. What is the data predicting?
#
#Option 1: compare prices to before and after announcements
#    - Should define what constitutes "good news" vs. "bad news" vs. "no effect"

#Random plots
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
		plt.plot(new_dates , event_log[j]['Open'])
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
Boolean 'success': True/False whether an arbitrary 5% return is reached on an opening price within 10 trading days
Highest price reached within 10 trading days: self explanatory
More to be added as needed 

Inputs: headline dataframe, stocks dictionary of dataframes. 
outputs: Dataframe of two numerical columns that should be appended to the headline dataframe. 
'''

def DefineEventResult(headline_data, stock_data, success):
	days_after = 9 # number of days away from headline event
	days_before = 0
	success_threshold = success
	event_logs = GetHeadlineHistory(headline_data, stock_data, days_before, days_after)
	print(len(event_logs))
	result_cols = []
	for i in range(len(event_logs)):
		stock_sample = event_logs[i].loc[:, 'Open']
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

'''
Add column of compatible stock dates .
This modifies the dataframe inplace.
'''
def ConvertHeadlineDates(headline_df):
	datey = headline_df.loc[:,'Date'].astype(str)
	new_date = datey.apply(lambda x: datetime.strptime('20' + x, '%Y%m%d').strftime('%Y-%m-%d'))
	headline_df['Stock_date'] = new_date

'''
Add column of compatible stock dates.
This modifies the dataframe inplace. 
'''
def ConvertStockDates(stocks_df):
	for stock_key in list(stocks_df.keys()):
		stock_dates = stocks_df[stock_key].loc[:,'Date'].astype(str)
		new_date = stock_dates.apply(lambda x: datetime.strptime(x,'%m/%d/%y').strftime('%Y-%m-%d'))
		stocks_df[stock_key]['Iso_date'] = new_date
	
#Current baseline is 2.14% return with 9 day limit & 7.5% thresh if invest on every single headline	
def GetMonetaryScore(headline_df, stocks_df, results_array, invest=5000, success=1.075, days_after=9):
	days_before = 0
	mon_returns = []
	new_logs = GetHeadlineHistory(headline_df,stocks_df,days_before,days_after)
	for i in range(len(new_logs)):
		stock_sample = new_logs[i].loc[:, 'Open']
		if len(stock_sample) != 0 and results_array[i] == 1:
			before_prices = stock_sample.iloc[days_before]
			after_prices = stock_sample.iloc[days_before+1:]
			normalized_difference = np.array(after_prices / before_prices)
			normal_len = len(normalized_difference)  
			for j in range(normal_len):
				day = normalized_difference[j]
				if day > success:
					mon_returns.append(invest*day)
					break
				elif j == (normal_len - 1):
					mon_returns.append(invest*day)
	raw_return = np.sum(mon_returns)
	tot_invest = len(mon_returns) * invest
	percent_return = ((raw_return / tot_invest) - 1) * 100
	numerical_return = raw_return - tot_invest
	print('Algorithm returned a {:.2f}% result of ${:.2f}'.format(percent_return, numerical_return))
	print('{0} was invested for a return of {1}, a {2}% increase'.format(tot_invest, raw_return, percent_return))

#Functions for converting clinical pipeline data into more general terms
def AddBroadDrug(drug_string):
	molecules = ['Molecules']
	biols = ['Biologics', 'Enzyme']
	genes = ['Gene', 'Cells', 'RNA']
	if drug_string in molecules:
		return 'Moldrugs'
	elif drug_string in biols:
		return 'Biodrugs'
	elif drug_string in genes:
		return 'Genedrugs'
	else:
		return 'Various'    

def AddBroadLocation(location_string):
	euro_locs = ['Switzerland', 'United Kingdom', 'Netherlands', 'Denmark', 'France', 'Belgium', 'Israel', 'Bermuda']
	west_locs = ['Seattle', 'Northern California', 'Southern California', 'Colorado']
	east_locs = ['Boston', 'Pennsylvania', 'New York', 'North Carolina', 'Kentucky', 'Maryland', 'Virginia', 'Connecticut']
	other_us_locs = ['Illinois', 'Austin', 'Texas', 'Florida']
	other_locs = ['China']
	if location_string in euro_locs:
		return 'Europe'
	elif location_string in west_locs:
		return 'Western US'
	elif location_string in east_locs:
		return 'Eastern US'
	else:
		return 'Other'

def AddBroadDisease(disease_string):
	approved = ['Cancer', 'Rare', 'Various']
	neuros = ['NeuroD', 'Nervous']
	if disease_string in approved:
		return disease_string
	elif disease_string in neuros:
		return 'Neuros'
	else:
		return 'Other'

#Add years active column
def CalcNewColumns(input_df):
	current_year = datetime.today().year
	years_active = current_year - input_df.loc[:,'Founded'] 
	input_df['Years Active'] = years_active

#Adds three general data columns for learning to submitted df and returns new df
#sub_select variable is for picking specific security symbol
def PrepareClinicalPipelineData(pipe_data, sub_select=''):
	from sklearn.preprocessing import OneHotEncoder
	CalcNewColumns(pipe_data)
	pipe_data['Broad Drug'] = pipe_data['Drug'].map(AddBroadDrug).apply(pd.Series)
	pipe_data['Broad Location'] = pipe_data['Location'].map(AddBroadLocation).apply(pd.Series)
	pipe_data['Broad Disease'] = pipe_data['Disease'].map(AddBroadDisease).apply(pd.Series)
	quant_cols = ['Security Symbol', 'Cap (Millions)', 'Years Active', 'Phase I', 'Phase II', 'Phase III', 'On Market']
	qual_cols = pipe_data.loc[:,['Broad Drug', 'Broad Location', 'Broad Disease']]
	pipe_quant = pipe_data.loc[:, quant_cols]
	enc = OneHotEncoder(sparse=False)
	qual_encode = enc.fit_transform(qual_cols)
	encode_df = pd.DataFrame(qual_encode)
	pipeline_df = pd.concat([pipe_quant.reset_index(drop=True), encode_df], axis=1)
	if len(sub_select) > 0:
		sub_selection = pipeline_df.loc[pipeline_df['Security Symbol'] == sub_select]
		if sub_selection.shape[0] != 1:
			warnings.warn('Expected one row, received zero or more than one.')
			print(sub_select)
		return sub_selection
	else:
		return pipeline_df


#Receive content of url, parse as json and return the object
#input: url(str); Output: dict
def GetJSONParsedData(url):
	response = urlopen(url)
	data = response.read().decode('utf-8')
	return json.loads(data)

def SaveURLCSV(url,filename):
	df = pd.read_csv(url)
	df.to_csv(filename)

#Omitted function for calling api

def CombineFinanceReports(symbol):
	file_suffix = symbol+'.csv'
	with open('QuarterlyFinance_'+file_suffix, 'r') as f:
		finance_df = pd.read_csv(f, index_col='Date')
		finance_df = finance_df.iloc[:,1:]
	with open('QuarterlyBalance_'+file_suffix, 'r') as f:
		balance_df = pd.read_csv(f, index_col='Date')
		balance_df = balance_df.iloc[:,1:]
	with open('QuarterlyCashFlow_'+file_suffix, 'r') as f:
		cash_df = pd.read_csv(f, index_col='Date')
		cash_df = cash_df.iloc[:,1:]
	#if list(finance_df.columns) == list(balance_df.columns) and list(finance_df.columns) == list(cash_df.columns):
	total_df = pd.concat([finance_df, balance_df, cash_df], axis=0)
	total_df.transpose().fillna(method='bfill',inplace=True)
	total_df.to_csv('QuarterReports_'+symbol+'.csv')
	#return None

def GetFinanceInformation(symbol, stock_date, finance_dic):
	company_reports = finance_dic[symbol]
	stock_datetime = date.fromisoformat(stock_date)
	column_dates = [date.fromisoformat(i) for i in list(company_reports.columns)]
	date_object = next(val for x, val in enumerate(column_dates) if val <= stock_datetime)
	finance_info =  company_reports.loc[:,date.isoformat(date_object)]
	return finance_info
