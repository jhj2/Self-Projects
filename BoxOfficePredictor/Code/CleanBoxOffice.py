'''Script for cleaning comment data and preparing data for regression
Since this script was written piecemeal, later revisions will put most of these loops
	in functions to avoid variables crossing wires. 
'''

#Import packages
import pandas as pd
import fasttext 
from TextHelper import tweet_cleaning_for_sentiment_analysis
import os

#Load file
with open('BoxOfficeCommentInfo.csv', 'r') as f:
	box_info = pd.read_csv(f, sep='\t')

#Clean and append the box_info dataframe
box_info['Total Gross'] = box_info.loc[:,'Total Gross'].replace('[\$,]', '', regex=True).astype(int)
box_info['Opening Gross'] = box_info.loc[:,'Opening Gross'].replace('[\$,]', '', regex=True).astype(int)
box_info = pd.concat([box_info, pd.DataFrame(columns=['Label_1', 'Label_2', 'Label_3', 'Prop_1', 'Prop_2', 'Prop_3'])], sort=False)

#Get file paths for each comment section and make useable
mypath = './BoxOfficeComments'
(dummy, dummie, filenames) = next(os.walk(mypath))
comment_files = [mypath+'/'+x for x in filenames]

#Train the fasttext model
model = fasttext.train_supervised('train.txt')

#Primary Method
#Retrieve comments and clean
movie_comments = []
for comments_section in comment_files:
	with open(comments_section, 'r') as g:
		comments_section_string = g.read().replace('\n', '')
	movie_comments.append(comments_section_string)

movie_comments_filtered = [tweet_cleaning_for_sentiment_analysis(x) for x in movie_comments]

#Use fasttext model to predict sentiment
tag_length = len('_comments.txt')
output_columns = ['Label_1', 'Label_2', 'Label_3', 'Prop_1', 'Prop_2', 'Prop_3']
prediction_df = pd.DataFrame(columns=output_columns)
for j in range(len(filenames)):
	filtered_comments = movie_comments_filtered[j]
	movie_title = filenames[j][:-tag_length]
	model_output = model.predict(filtered_comments, k=3)
	output_list = list(model_output[0]) + list(model_output[1])
	box_info.loc[box_info['Movie Title'] == movie_title, output_columns] = output_list

#Second method
#Alternative way to measure 
comments_list_dic = {}
tag_length = len('_comments.txt')
path_length = len('./BoxOfficeComments/')
for comments_section in comment_files:
	with open(comments_section, 'r') as h:
		comments_list = h.read().splitlines()
	comments_list = [tweet_cleaning_for_sentiment_analysis(x) for x in comments_list]
	comments_list = [x for x in comments_list if len(x) > 0]
	movie_title = comments_section[path_length:-tag_length]
	comments_list_dic[movie_title] = comments_list   

#Create dataframes of sentiments for each line for each movie
sentiment_dfs = {}
for com_list in comments_list_dic.keys():
	lr_list = []
	clean_comments = comments_list_dic[com_list]
	for clean_line in clean_comments:
		line_result = model.predict(clean_line, k=3)
		line_result_as_list = list(line_result[0]) + list(line_result[1])
		lr_list.append(line_result_as_list)
	lr_sentiments = pd.DataFrame(lr_list)
	sentiment_dfs[com_list] = lr_sentiments  
    
#Add to dataframe the top 3 primary emotions predicted
box_info_alt = box_info.copy(deep=True)
output_columns = ['Label_1', 'Label_2', 'Label_3', 'Prop_1', 'Prop_2', 'Prop_3']
for movie_key in sentiment_dfs.keys():
	comment_emotes = sentiment_dfs[movie_key]
	if comment_emotes.shape[0] < 3:
		continue
	emote_counts = comment_emotes[0].value_counts(normalize=True)
	if len(emote_counts.index) < 3:
		continue
	output_emotes = emote_counts.index[0:3].tolist() + emote_counts[0:3].tolist()
	box_info_alt.loc[box_info_alt['Movie Title'] == movie_key, output_columns] = output_emotes

#Save different box_infos for regression
box_info.to_csv('BoxInfoMethod1.csv', sep='\t')
box_info_alt.to_csv('BoxInfoMethod2.csv', sep='\t')



