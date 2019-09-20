#Load packages
import pandas as pd
import fasttext 
from TextHelper import tweet_cleaning_for_sentiment_analysis

#Function to make usable for fasttext
def add_fb_label(stringy):
	labe = '__label__'
	label_stringy = labe+stringy
	return label_stringy

#Load files
with open('text_emotion.csv', 'r') as f:
	tweet_emotes = pd.read_csv(f)

#Filter
emotes = tweet_emotes.loc[:,['sentiment', 'content']]

#Pre-process
emotes['content'] = emotes['content'].apply(tweet_cleaning_for_sentiment_analysis)
emotes = emotes.loc[emotes['content'].str.len() != 0, :]
emotes['sentiment'] = emotes['sentiment'].apply(add_fb_label)

#Combine into one column to make usable for fasttext
emotes['train'] = emotes['sentiment'] + ' ' + emotes['content']
train_df = emotes.loc[:,'train']

#Save dataframe to file for use later
train_df.to_csv('train.txt', index=False, header=False)