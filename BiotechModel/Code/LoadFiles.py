#Functions for loading files
import pandas as pd 
import os

def GetDataPath(data_file):
	'''Sub helper function for other load functions'''
	base_path = os.path.abspath('../Data')
	data_path = base_path + '/' + data_file
	return data_path

def LoadUniqueCompanies():
	'''Returns list'''
	file_path = GetDataPath('unique_companies.txt')
	with open(file_path, 'r') as f:
		companies = [line.rstrip() for line in f]
	return companies 

def LoadCompanies():
	'''Returns pandas dataframe'''
	file_path = GetDataPath('SODWeightings_20191025_NBI.csv')
	with open(file_path, 'r') as f:
		companies = pd.read_csv(f, sep='\t', header=4)
	return companies

def LoadCompaniesSimple(str_compatible=False):
	'''Loads pandas dataframe'''
	file_path = GetDataPath('SODWeightings_20191025_NBI_Edited.csv')
	with open(file_path, 'r') as f:
		companies = pd.read_csv(f, sep='\t', header=4)
	if str_compatible:
		companies['Company Name'] = companies['Company Name'].str.lower()
	return companies

def LoadHeadlines():
	'''Returns pandas dataframe'''
	file_path = GetDataPath('FilteredHeadlinesManual.csv')
	with open(file_path, 'r') as f:
		headlines = pd.read_csv(f, sep='\t')
	return headlines

def LoadStocks():
	'''Returns dictionary of pandas DataFrames'''
	stocks = {}
	companies = LoadUniqueCompanies()
	for symbol in companies:
		data_file = 'HistoricalPrices_' + symbol + '.csv'
		stock_data_path = GetDataPath(data_file)
		with open(stock_data_path, 'r') as f:
			stock_data = pd.read_csv(f, skipinitialspace=True)
		stocks[symbol] = stock_data
	return stocks

def LoadClinicPipeline(raw=False):
	'''Returns pandas dataframe'''
	file_path = GetDataPath('BiotechCompaniesInfo.csv')
	with open(file_path, 'r') as f:
		pipelines = pd.read_csv(f, sep='\t')
	if raw is False:
		nonrelevant_cats = ['Other', 'Unavailable', 'Devices', 'Diagnostics', 'Production', 'None']
		pipelines = pipelines.loc[~pipelines.loc[:,'Drug'].isin(nonrelevant_cats)] #tilde selects for opposite of isin()
	return pipelines

def LoadRecentHeadline(phase):
	file_suffix = 'RecentHeadlinePhase' + str(phase) + '.txt'
	file_path = GetDataPath(file_suffix)
	with open(file_path, 'r') as f:
		recent_headline = f.read()
	return recent_headline

def LoadFinanceReports():
	reports = {}
	companies = LoadUniqueCompanies()
	for symbol in companies:
		data_file = 'QuarterReports_' + symbol + '.csv'
		data_path = GetDataPath(data_file)
		with open(data_path, 'r') as f:
			report_data = pd.read_csv(f, index_col='Date')
		reports[symbol] = report_data
	return reports

def SavePrediction(stock_prediction_data):
	file_path = GetDataPath('PredictionData.csv')
	stock_prediction_data.to_csv(file_path, mode='a', header=False)
	return 

def SaveStockInfo(stock_df, file_suf):
	file_path = GetDataPath(file_suf)
	stock_df.to_csv(file_path, index=False)
	return 

def SaveRecentHeadline(headline, phase):
	file_suffix = 'RecentHeadlinePhase' + str(phase) + '.txt'
	file_path = GetDataPath(file_suffix)
	with open(file_path, 'w') as f:
		f.write(headline)
	return





