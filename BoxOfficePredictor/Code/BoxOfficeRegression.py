'''Script for creating a regression model'''

#Import packages
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNetCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import KFold, cross_val_predict

#Local functions
#Collect columns currently relevant for regression
def GetRegressionDF(input_df):
	reg_columns = ['Opening Gross', 'Opening Theaters', 'num_comments', 'score', 'upvote_ratio']
	reg_df = input_df.loc[:,reg_columns]
	return reg_df

#Split dataframe into input and output labels for training
#sklearn has this capability
def BoxInfoXYSplit(input_df):
	input_labels = [x for x in input_df.columns if x != 'Opening Gross']
	x_df = box_df.loc[:,input_labels]
	y_df = box_df.loc[:, 'Opening Gross']
	return x_df, y_df

#One-Hot like encoder except instead of binary representations of categories, there are ratios
def SentimentEncoding(sent_df):
	sent_one = list(sent_df.loc[:,'Label_1'].unique())
	sent_two = list(sent_df.loc[:,'Label_2'].unique())
	sent_three = list(sent_df.loc[:,'Label_3'].unique())
	unique_sents = list(set().union(sent_one, sent_two, sent_three))
	zero_prep = np.zeros(shape=(sent_df.shape[0], len(unique_sents)))
	sent_levels = pd.DataFrame(zero_prep, columns=unique_sents)
	for j in range(sent_df.shape[0]):
		sent_levels.loc[j,sent_df.loc[j,'Label_1']] = sent_df.loc[j,'Prop_1']
		sent_levels.loc[j,sent_df.loc[j,'Label_2']] = sent_df.loc[j,'Prop_2']
		sent_levels.loc[j,sent_df.loc[j,'Label_3']] = sent_df.loc[j,'Prop_3']
	return sent_levels

#Load data
#Method 1 is top 3 emotions predicted for whole section 
#Method 2 is top 3 emotions for line by line analysis 
with open('BoxInfoMethod1.csv', 'r') as f:
	box_info_one = pd.read_csv(f, sep='\t')
with open('BoxInfoMethod2.csv', 'r') as g:
	box_info_two = pd.read_csv(g, sep='\t')

box_infos = [box_info_one, box_info_two]
box_dfs = [GetRegressionDF(x) for x in box_infos]

#Train regression model
kf = KFold(n_splits=5, shuffle=True, random_state=42)
one_out_len = box_infos[0].shape[0]
one_out = KFold(n_splits=one_out_len, shuffle=True, random_state=42)
outcome_dfs = []
for box_df in box_infos:
	reg_df = GetRegressionDF(box_df)
	pre_x_df, y_df = BoxInfoXYSplit(reg_df)
	label_encodes = SentimentEncoding(box_df)
	x_df = pd.concat([pre_x_df, label_encodes],axis=1)
	tree_model = DecisionTreeRegressor(max_depth=3)
	elastic_model_cv = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, .99, 1], cv=7)
	movie_title = box_df.loc[:,'Movie Title']
	actual_opening = box_df.loc[:,'Opening Gross']
	predicted_tree_opening = cross_val_predict(tree_model,x_df ,y_df, cv=one_out, n_jobs=-1)
	predicted_elastic_opening = cross_val_predict(elastic_model_cv,x_df ,y_df, cv=one_out, n_jobs=-1)
	outcome_df = pd.concat([movie_title, actual_opening, 
							pd.Series(predicted_tree_opening), 
							pd.Series(predicted_elastic_opening)], axis=1)
	outcome_df.columns = ['Movie Title', 'Opening Gross', 'Predicted Tree', 'Predicted CV']
	outcome_dfs.append(outcome_df)

#Save to file
outcome_dfs[0].to_csv('Method1_outcomes.csv')
outcome_dfs[1].to_csv('Method2_outcomes.csv')








