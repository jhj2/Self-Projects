'''Script for plotting box office results'''

#Import packages
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

#local functions
def clean_df(outcome_df):
	needed_col = ['Movie Title', 'Opening Gross', 'Predicted Tree', 'Predicted CV']
	rename_col = ['Movie Title', 'Opening Gross', 'Predicted Tree Gross', 'Predicted ElasticNet Gross']
	selected_df = outcome_df.loc[:,needed_col]
	selected_df.columns = rename_col
	return selected_df

def plot_outcomes(outcome_df):
	plt.clf();
	sns.set(style="whitegrid")
	outcome_df = outcome_df.melt('Movie Title', var_name='Grosses', value_name='vals')
	sns.catplot(x='vals', y='Movie Title', hue='Grosses', data=outcome_df,
				height=20, label='Real Gross', legend=True)
	ax = plt.gca()
	ax.xlabel='Predicted and Actual Gross'

#Load files
with open('Method1_outcomes.csv', 'r') as f:
    one_outcome = pd.read_csv(f)
    
with open('Method2_outcomes.csv', 'r') as g:
    two_outcome = pd.read_csv(g)

#Clean
one_outcome = clean_df(one_outcome)
two_outcome = clean_df(two_outcome)

#Plot
plot_outcomes(one_outcome)
plt.savefig('BoxOfficeModelComparison.png', dpi = 300)



