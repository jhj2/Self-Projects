#Script for generating similarity profiles
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib import rc

import LoadFunctions as lf

#Load database
season_df = lf.LoadPlayers19()
#Global Parameters
player = 'Torrey Craig'
player_sim_col = player + ' SimCol'
comparisons = ['FG', 'FGA', '3P', '3PA', '2P', '2PA', 'FT', 'FTA',
			   'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
#Plotting variables
background_color = '#FEC524'
font_color = '#8B2131'
bar_color = '#0E2240'
table_scale = 1.5
games_filter = 44 #Default 44 per bball reference
per36_comp = ['PTSper36','2Pper36', '3Pper36', 'TRBper36','ASTper36', 'STLper36', 'BLKper36']
pic_file = 'torrey-craig.png'
figure_file = player + ' SimilarityTest'+'.png'

#Functions
def SimilarityScore(player_df, categories, player='Dejounte Murray', metric='euclidean', minutes=True):
	player_row = player_df.loc[player_df['Player'] == player, :]
	if player_row.shape[0] == 0:
		print('Player not found')
		return None
	player_index = player_row.index.values.astype(int)[0]
	counting_df = player_df.loc[:,categories]
	if minutes==True:
		counting_df = counting_df.div(player_df.loc[:, 'MP'].values, axis=0) * 36
	scaler = MinMaxScaler()
	nc_df = scaler.fit_transform(counting_df)
	nc_df = np.nan_to_num(nc_df)
	player_stats = nc_df[player_index, :].reshape(1,nc_df.shape[1])
	distances = sp.spatial.distance.cdist(player_stats, nc_df, metric)
	distance_df = pd.Series(distances.ravel()).round(decimals=3)
	return distance_df

def NormalizePer36(player_df, categories):
	count_df = player_df.loc[:, categories]
	count_df = count_df.div(player_df.loc[:,'MP'].values, axis=0) *36
	min_scaler = MinMaxScaler()
	ncna = min_scaler.fit_transform(count_df)
	ncna = np.nan_to_num(ncna)
	comp_per36 = [x+'per36' for x in categories]
	ncdf = pd.DataFrame(ncna, columns=comp_per36)
	normalized_df = pd.concat([player_df, ncdf], axis=1)
	return normalized_df

#Set up player similarity scores
season_df[player_sim_col] = SimilarityScore(season_df, comparisons,player=player)
per36_normal = NormalizePer36(season_df, comparisons)

#Prep
#Global prep
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#Image get for plot 1
image_path = lf.GetImagePath(pic_file)
with open(image_path, 'rb') as f:
	image = plt.imread(f)
	
#Similar players for plot 2
similar_players = per36_normal.sort_values(player_sim_col).loc[:,['Player', player_sim_col]].iloc[1:6,:]
cell_text = []
cell_color = []
for row in range(len(similar_players)):
	subrow = similar_players.iloc[row]
	cell_text.append(subrow)
	cell_color.append([background_color] * len(subrow) )
col_color = [bar_color] * len(subrow)
#Prep for plot 3
game_filtered = per36_normal.loc[per36_normal['G'] > games_filter, :]
highlight = game_filtered.rank(pct=True).loc[game_filtered['Player'] == player, per36_comp]

#Set up figure
fig, (ax1, ax2, ax3) = plt.subplots(nrows=3,ncols=1)
fig.set_size_inches(4,10)
#Subplot 1 picture
ax1.imshow(image)
ax1.axis('off')
#Subplot 2 table
axtable = ax2.table(cellText=cell_text, cellColours=cell_color, colColours=col_color,
					colLabels=['Similar Player', 'Similarity Score'], loc='center', cellLoc='center')
ax2.axis('off')
table_props = axtable.properties()
table_cells = table_props['child_artists']
axtable.scale(table_scale, table_scale)
for cell in table_cells: 
	cell.get_text().set_fontsize(32)
	if 'Similar' in cell.get_text()._text:
		cell.get_text().set_color('white') #background_color also option
	else:
		cell.get_text().set_color(font_color)

#Subplot 3 stat profile
stats = ['Points', '2P Made', '3P Made', 'Rebounds', 'Assists', 'Steals', 'Blocks']
pos = np.arange(len(per36_comp))
ax3.bar(pos, highlight.values[0], color=bar_color)
ax3.set_xticklabels(stats, color=font_color)
ax3.set_xticks(pos)
plt.xticks(rotation=45, ha='right')
ax3.tick_params(axis='y', colors=font_color)
ax3.set_xlabel('Counting Stat Categories', color=font_color)
ax3.set_ylabel('Percentile for Per36 Stat', color=font_color)
ax3.set_facecolor(background_color)
ax3.spines['left'].set_color(font_color)
ax3.spines['bottom'].set_color(font_color)
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)

#Figure miscellaneous
fig.suptitle(('Similarity Profile:\n'+player), fontsize=22, color=font_color, ha='center')
fig.set_facecolor(background_color)
fig.savefig(figure_file, facecolor=background_color, bbox_inches='tight', dpi=250)

		