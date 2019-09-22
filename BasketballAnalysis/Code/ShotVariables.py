#This script is for Git use

#Options for player are 'all' or specific name
#e.g. player = 'TJ Warren'
#Options for distance are between distances, begin is 1, end is 87
#e.g. distance_begin = 1
#e.g. distance_end = 26


#Class for initializing variables
import pandas as pd

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Initiate class
class ShotVariables:
	def __init__(self, player, distance_begin, distance_end):
		self.player = player
		self.distance_begin = distance_begin
		self.distance_end = distance_end
		self.shot_table = pd.read_pickle('shot_table.pkl')


	#Filter the shot table
	def FilterTable(self):
		if self.player is not 'all':
			player_table = self.shot_table.loc[self.shot_table['PLAYER_NAME'] == self.player]
		filter_table = player_table.loc[(player_table['SHOTDISTANCE'] >= self.distance_begin) 
			& (player_table['SHOTDISTANCE'] <= self.distance_end)]
		filter_table.reset_index(inplace=True)
		self.shot_table = filter_table
		if self.shot_table.shape[0] == 0:
			print('Table was not filtered correctly, check data')

def GetVariables(player=None, distance_begin=None, distance_end=None):
	shot_variables = ShotVariables(
		player=player, 
		distance_begin=distance_begin, 
		distance_end=distance_end)
	shot_variables.FilterTable()
	return shot_variables


