'''Get Trailer Comments'''
#Import packages
import praw
import pandas as pd

#Make ids from dataframe submittable to info()
def add_tag(id_string):
	new_thing = 't3_' + id_string
	return new_thing

#Get Box office info
with open('2018BoxOffice.csv', 'r') as f:
	box_info = pd.read_csv(f, sep='\t')

#Set up box_info dataframe for adding of info from praw
box_info = pd.concat([box_info, pd.DataFrame(columns=[ 'title', 'ups', 'downs', 
													'upvote_ratio', 'num_comments', 
													'score'])], sort=True)
box_info['Reddit_id'] = box_info['Reddit_id'].apply(add_tag)

#Setup praw object. Reddit info obscured out
reddit = praw.Reddit(client_id = '#####',
					client_secret = '#####',
					password='######',
					user_agent='######',
					username='######')

reddit.read_only = True

#Send in url IDs and retrieve each submission post and extract relevant information
submissions = reddit.info(box_info['Reddit_id'].to_list())
j=0
for submission in submissions:
	filename = box_info['Movie Title'][j]+'_comments.txt'
	comment_file = open(filename, 'w')
	box_info['ups'][j] = submission.ups
	box_info['downs'][j] = submission.downs
	box_info['upvote_ratio'][j] = submission.upvote_ratio
	box_info['num_comments'][j] = submission.num_comments
	box_info['score'][j] = submission.score 
	box_info['title'][j] = submission.title 
	j += 1 
	for comment in submission.comments.list():
		if isinstance(comment, MoreComments):
			continue
		else:
			comment_file.write(comment.body)
			comment_file.write('\n')   
	comment_file.close()

box_info.to_csv('BoxOfficeCommentInfo.csv', sep='\t', index=False)

#Relevant for picking the limit on comments: http://yongyeol.com/papers/choi-reddit-2015.pdf

