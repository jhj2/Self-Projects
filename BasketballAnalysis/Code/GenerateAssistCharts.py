#Generates assist charts where rows are the assistee, columns are the assister

#Import all the packages
import pandas as pd
#Various self-made function imports
from LoadFunctions import LoadSeason
from ScoringFunctions import GenerateAssistMatrix

#Local Function
def assist_cutoff_filter(value_array, cutoff = 10):
	for row in value_array:
		for i in range(len(row)):
			if row[i] < cutoff:
				row[i] = 0
	return value_array


#global objects
season_chart = LoadSeason()

#League Wide matrix
assist_matrix = GenerateAssistMatrix(season_chart, names=True)

#Method for generating team assist matrices
unique_team_list = season_chart['PLAYER1_TEAM_ABBREVIATION'].unique().tolist()
unique_team_list = [x for x in unique_team_list if x == x]
team_assists = {}
for team in unique_team_list:
	sub_group = season_chart[season_chart.loc[:,'PLAYER1_TEAM_ABBREVIATION'] == team]
	sub_matrix = GenerateAssistMatrix(sub_group,names=True)
	team_assists[team] = sub_matrix

