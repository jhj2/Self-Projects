import seaborn as sns
import matplotlib.pyplot as plt

#Master function
def GenerateFigure(shooting_df, shot_variable):
	if shot_variable.chart == 'bar':
		graph_shooters(shooting_df, title=shot_variable.title)

#Individual Functions
#Bar graph function
def GraphShooters(shooting_df, title='Placeholder title', ylabel='Shooting Percentage'):
	plt.clf()
	sns.set(style="whitegrid")
	ax = sns.barplot(x='SHOTDISTANCE', y='PERCENTAGE', data=shooting_df, ci=None)
	fig = plt.gcf()
	fig.set_size_inches(20, 10)
	ax.set(xlabel = 'Distance from basket (ft)', ylabel=ylabel, title=title)
	ax.set_ylim(bottom=0, top=1)
	for row, index in shooting_df.iterrows():
		if index['PERCENTAGE'] < .175:
			ax.text(row-1, index['PERCENTAGE']+.01, index.PLAYER_NAME, color='black', ha="center", va ='bottom', rotation='vertical')
		else:
			ax.text(row-1, index['PERCENTAGE']-.01, index.PLAYER_NAME, color='black', ha="center", va ='top', rotation='vertical')
	filename=title+'.png'
	plt.savefig(filename)

def GraphShooterVolumes(shooting_df, title='Placeholder'):
	plt.clf()
	sns.set(style="whitegrid")
	ax = sns.barplot(x='SHOTDISTANCE', y='PERCENTAGE', data=shooting_df, ci=None)
	fig = plt.gcf()
	fig.set_size_inches(20, 10)
	ax.set(xlabel = 'Distance from basket (ft)', ylabel='Shooting Percentage', title=title)
	ax.set_ylim(bottom=0, top=1)
	for row, index in shooting_df.iterrows():
		if index['PERCENTAGE'] < .175:
			ax.text(row, index['PERCENTAGE']+.01, 'Shots taken: '+str(index.TOTALSHOTS), color='black', ha="center", va ='bottom', rotation='vertical')
		else:
			ax.text(row, index['PERCENTAGE']-.01, 'Shots taken: '+str(index.TOTALSHOTS), color='black', ha="center", va ='top', rotation='vertical')
	filename=title+'.png'
	plt.savefig(filename)
