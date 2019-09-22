#Git Version of script
#Import all the packages
import numpy as np
import pandas as pd
import random
#Various sklearn imports
from LoadFunctions import LoadSeason, LoadGame

#~~~~~~~~~~~~~~~~~~~~~~~~~
#HELPER FUNCTIONS
def MadeShotString(description):
	shot_string = description.loc[['HOMEDESCRIPTION', 'VISITORDESCRIPTION']].dropna().values[0]
	return shot_string

#Return a dictionary of player names attached to each ID
#I thought this would be a bit more involved but it turns out there was a one line solution
def ID2Name(season_description):
	ID_dic = season_description.set_index('PLAYER1_ID').to_dict()['PLAYER1_NAME']
	ID_dic_2 = season_description.set_index('PLAYER2_ID').to_dict()['PLAYER2_NAME']
	ID_dic.update(ID_dic_2)
	return ID_dic

#~~~~~~~~~~~~~~~~~~~~~~~~
#CALLED FUNCTIONS
def ShotValue(description):
	#if type(description) is not 1:
	#    #Feed in only one row at a time, otherwise raise this error
	#    raise Exception('Need one row at a time, there were {} rows'.format(description.shape[0])) 
	shot_type = description.loc['EVENTMSGTYPE']
	'''shot string will take both descriptions, assume that there's only one description by dropping
	na values, and then taking the one and only string. Plays with more than one player involved will
	not have the correct string caught but no made shots contain more than one description'''
	try:
		shot_string = MadeShotString(description)
	except IndexError:
		shot_string = ''
	shot_value = 0
	if shot_type == 1:
		if '3PT' in shot_string:
			shot_value = 3
		else:
			shot_value = 2
	elif shot_type == 3:
		#dependent on MISS being in capital letters
		if 'MISS' not in shot_string:
			shot_value = 1  
	return shot_value

#If a made shot as an assistor, get the ID of the assistor
def GetAssistorID(description):
	if description.loc['EVENTMSGTYPE'] != 1:
		#Need to figure out overall flow and what sort of null answer to return
		return None
	else:
		shot_string = MadeShotString(description)
		#Assumption that holds on quick eye check that assistors are player 2
		if 'AST' in shot_string:
			assistor_id = description['PLAYER2_ID']
			return assistor_id
		#No assists on play
		return None

#Get player ID for the person that made the shot
def GetShotMakerID(description):
	if description.loc['EVENTMSGTYPE'] != 1:
		#Need to figure out overall flow and what sort of null answer to return
		return None
	else: 
		shot_string = MadeShotString(description)
		#Assumption that holds on quick eye check that shot makers are player 1
		maker_id = description['PLAYER1_ID']
		return maker_id

#The names option renames IDs to player names
def GenerateAssistMatrix(season_description, names=True, self=False):
	#I put ID
	made_shots = season_description[season_description.loc[:,'EVENTMSGTYPE'] == 1]
	ID_dic = ID2Name(made_shots)
	#Would be faster to make dic out of made_shots, but there are players with 0 made shots and >0 assists
	assist_counts = made_shots.groupby(['PLAYER1_ID', 'PLAYER2_ID']).size()
	assist_matrix = pd.DataFrame(index=ID_dic, columns=ID_dic)
	for indexers, ass_count in assist_counts.items():
		#When doing chained indexing, column call is first, then row call
		assist_matrix[indexers[1]][indexers[0]] = ass_count
	#Drop any rows and columns that are nothing but NaN
	assist_matrix = assist_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
	#Converting non-assisted shots to "self-assisted" shots no the matrix to make it square
	self_assist = assist_matrix.loc[:,0].values.tolist()
	assist_matrix.drop(labels=0,axis=1,inplace=True)
	if self == True:
		np.fill_diagonal(assist_matrix.values, self_assist)
	else:
		np.fill_diagonal(assist_matrix.values, 0)
	#Replace ID's with player names
	if names is True:
		assist_matrix.rename(columns=ID_dic, inplace=True)
		assist_matrix.rename(index=ID_dic, inplace=True)
	#Replace NaN with zeroes
	assist_matrix.fillna(0, inplace=True)
	return assist_matrix

#Group players by team
def GenerateRosters(season_description):
	team_sorted = season_description.groupby(['PLAYER1_TEAM_ID'])

#Filter the season_description matrix for shots, filters out non-shot events
#Parameter to choose whether to return all, missed, or made shots
#Takes in season_description matrix and returns all rows fitting the which_shot selection
def GetShots(season_description, which_shot='all'):
    event_msg_filter = season_description.loc[:,'EVENTMSGTYPE']
    made_shots = event_msg_filter == 1
    missed_shots = event_msg_filter == 2
    if which_shot is 'all':
        new_des = season_description[made_shots | missed_shots ]
    elif which_shot is 'made':
        new_des = season_description[made_shots]
    elif which_shot is 'missed':
        new_des = season_description[missed_shots]
    else:
        print('Incorrect parameter for which_shot, options are "all", "made", "missed"')
        return None
    return new_des

#Use regex to extract the shot distance for each made/missed shot
#Takes in season_description matrix and returns a nx1 array of numeric shot distances
def GetShotDistance(season_description):
    descriptions = season_description.loc[:,['HOMEDESCRIPTION', 'VISITORDESCRIPTION']]
    dis_reg = descriptions.apply(lambda x: x.str.extract(r'\s(\d{1,2})[^"]', expand=False), axis=1)
    clean_dis = dis_reg.fillna(value='')
    #Assumption that only one shot distance listed per row
    clean_dis_sum = clean_dis.sum(axis=1)
    distance_array = pd.to_numeric(clean_dis_sum)
    distance_array.replace('', np.nan, inplace=True)
    return distance_array
    
	