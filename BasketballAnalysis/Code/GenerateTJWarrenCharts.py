#Local imports
from GraphingFunctions import GraphShooterVolumes
from ShotVariables import GetVariables

#Options for player are 'all' or specific name
player = 'TJ Warren'
#Options for distance are between distances, begin is 1, end is 87
distance_begin = 1
distance_end = 30
#Title for the chart
title='TJWarrenDistances'

shot_variables = GetVariables(player=player, distance_begin=distance_begin, distance_end=distance_end)
GraphShooterVolumes(shot_variables.shot_table, title=title)

