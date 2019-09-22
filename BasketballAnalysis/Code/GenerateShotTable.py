#Script generated by creating a leaner version of ShotDistanceCharts jupyter
#External imports
import pandas as pd 

#Local imports
from LoadFunctions import LoadSeason, LoadGame
from ScoringFunctions import GetShots, GetShotDistance, ID2Name

#Initiations
season_chart = LoadSeason()
shots_filtered = GetShots(season_chart, which_shot='all')
shot_distance = GetShotDistance(shots_filtered)
id_dic = ID2Name(season_chart)

#Create table of player, distance, result
minimal = shots_filtered.loc[:,['PLAYER1_ID', 'EVENTMSGTYPE']]
minimal['SHOTDISTANCE'] = shot_distance
minimal.dropna(inplace=True)

#Create list of unique distances
distances = list(minimal['SHOTDISTANCE'])
distances.sort()

#Create aggregate table of shots 
shot_table = minimal.groupby(['PLAYER1_ID', 'SHOTDISTANCE']).EVENTMSGTYPE.value_counts().unstack(fill_value=0)
shot_table.columns=['MADE', 'MISSED']
shot_table['TOTALSHOTS'] = shot_table.sum(axis=1)
shot_table['PERCENTAGE'] = shot_table['MADE'] / shot_table['TOTALSHOTS']
shot_table.reset_index(inplace=True)
shot_table['PLAYER_NAME'] = shot_table['PLAYER1_ID'].map(id_dic)



shot_table.to_pickle('shot_table.pkl')