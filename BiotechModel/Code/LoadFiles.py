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
			stock_data = pd.read_csv(f)
		stocks[symbol] = stock_data
	return stocks



