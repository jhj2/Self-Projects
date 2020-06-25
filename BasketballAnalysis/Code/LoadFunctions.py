#This version of the script is for Git upload. Note: base baths removed

#Load packages
import pandas as pd
import os
import pickle 

#Functions
def GetDataPath(data_file):
	'''Sub helper function for other load functions'''
	base_path = os.path.abspath('../Data')
	data_path = base_path + '/' + data_file
	return data_path

def GetImagePath(data_file):
	'''Sub helper function for other load functions'''
	base_path = os.path.abspath('../Images')
	data_path = base_path + '/' + data_file
	return data_path

#Get relevenat stats
def BStatsReduce(stats_matrix):
	#Assumption that input is a pandas matrix
	nec_columns = ['EVENTMSGACTIONTYPE', 'EVENTMSGTYPE', 'EVENTNUM', 'GAME_ID', 'HOMEDESCRIPTION', 'PCTIMESTRING', 'PERIOD', 
				'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ABBREVIATION', 'PLAYER1_TEAM_ID', 
				'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ABBREVIATION', 'PLAYER2_TEAM_ID', 
				'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ABBREVIATION', 'PLAYER3_TEAM_ID', 
				'SCORE', 'SCOREMARGIN', 'VISITORDESCRIPTION', 'WCTIMESTRING']
	stats_matrix = stats_matrix.loc[:,nec_columns]
	return stats_matrix

#Load a specified game
def LoadGame(game=1, reduced=True):
	#Path for game files, will need to change if multiple seasons implemented
	base_path = '######'
	#For the 2016-17 season there are 1230 recorded games, and the number should be from 1-1230 *NO ZERO*
	game_num = format(game, '04d')
	game_file_tag = '002160'+game_num+'.csv' 
	game_file = base_path + game_file_tag
	with open(game_file) as f:
		game_chart = pd.read_csv(f)
	game_chart.drop(game_chart.columns[0], axis=1, inplace=True)
	if reduced is True:
		game_chart = BStatsReduce(game_chart)
	return game_chart

#Load a season
def LoadSeason(season='2016-17', reduced=True):
	season_pickle = season+'.pickle'
	try:
		pickle_path = GetDataPath(season_pickle)
		with open(pickle_path, 'rb') as f:
			season_chart = pickle.load(f)
	except FileNotFoundError: 
		base_path = '#####'
		season_path = base_path + season
		season_list = []
		#Appending game DataFrames without pre-allocating space because unknown parameters
		for file_name in os.listdir(season_path):
			full_file_name = season_path+'/'+file_name
			with open(full_file_name) as f:
				game_chart = pd.read_csv(f)
			season_list.append(game_chart)
		season_chart = pd.concat(season_list, axis=0)
		season_chart.drop(season_chart.columns[0], axis=1, inplace=True)
		with open(season_pickle, 'wb') as f:
			pickle.dump(season_data, f)
	if reduced is True:
		season_chart = BStatsReduce(season_chart)
	return season_chart

#Load 2019-20 season which is dramatically different than the 2016-17
def LoadSeason19():
	file_path = GetDataPath('NBA-PBP-2019-2020.csv')
	with open(file_path, 'r') as f:
		season_chart = pd.read_csv(f)
	return season_chart

def LoadPlayers19():
	file_path = GetDataPath('2019-20PlayerStats.csv')
	with open(file_path, 'r') as f:
		season_chart = pd.read_csv(f, sep='\t')
	return season_chart
