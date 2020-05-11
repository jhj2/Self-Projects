#Last updated 200227
#imports
import LoadFiles as lf 
import StockFeaturePrepare as sfp
import PipelineFunctions as pf 
import re 
from datetime import date, timedelta
import pandas as pd 
import feedparser
import joblib
import pync
import time


'''
Crude estimation of clinical trial headline sentiment
current problems: 
	1. Distinguishing between positive news and gene-positives (e.g. HER2 positive)
	2. Distinguising between trial news and investors responding to trial news
	3. Announcements that avoid broad terms and use disease specific metrics
'''
def HeadlineSentiment(headline_string):
	#Some positive words are just the root to cover all variations of the word
	positive_words = [' positive', 'publi', 'complet', 'mechanistic', 'filing',
					 'improvement', 'superior', 'achieve', 'promis', 'milestone', 'meets',
					 '100%', 'succe', 'hit', 'pass', 'good', 'improvement', 'durability']
	negative_words = ['did not', 'does not', 'halt', 'flop', 'flunk', 'discontinue',
					 'fail', ' nix', 'sink', 'drop', 'death', 'stop', 'lack']
	negative_exceptions = ['failure society']
	positive_exceptions = ['abstract', 'but']
	headline_string = ' ' + headline_string.lower()
	negative_check = {x for x in negative_words if x in headline_string}
	negative_exception_check = {x for x in negative_exceptions if x in headline_string}
	positive_check = {x for x in positive_words if x in headline_string}
	positive_exception_check = {x for x in positive_exceptions if x in headline_string}
	if negative_check and not negative_exception_check:
		return -1
	elif positive_check and not positive_exception_check:
		return 1
	else:
		return 0

'''
Headline_string = string variable of a headline
usable_companies = dataframe with columns of 'Company Name' and 'Security Symbol'
'''
def BreakdownHeadline(headline_string):
    usable_companies = lf.LoadCompaniesSimple(str_compatible=True)
    company_names = usable_companies['Company Name']
    headline_string = headline_string.lower()
    matches = {x for x in company_names if x in headline_string}
    short_names = ['ra', 'ani']
    match_name = {x for x in matches if x in short_names}
    if len(match_name) > 0:
        for off_word in match_name:
            if re.search(rf'({off_word}\S|\S{off_word})', headline_string):
                matches.remove(off_word)
    match_security = [usable_companies.loc[company_names == x, 'Security Symbol'].item() for x in matches]
    if len(match_security) == 0:
        print('No companies found')
    return match_security

'''
Need to test if url works on current days with incomplete information
Preferablly just single input
'''
def GetStockInfo(security_symbols):
	#Omitted for api reasons
	return None
'''
Display model recommendation
'''
def MacNotification(headline, security, recommendation):
	if recommendation == 1:
		str_rec = 'Buy '
	elif recommendation == 0:
		str_rec = 'Pass on '
	title = str_rec + security
	pync.notify(headline, title=title)

'''
Get model prediction
'''
def GetPrediction(headline, phase):
	#Breakdown headline
	security_symbol = BreakdownHeadline(headline)
	predicted_sent = HeadlineSentiment(headline)
	today_date = date.today().strftime('%Y%m%d')
	for symbol in security_symbol:
		stock_info = GetStockInfo(security_symbol)
		#Setup headline entry
		headline_entry = {
			'Security': symbol,
			'Headline': headline,
			'Date': today_date
		}
		headline_series = pd.DataFrame(headline_entry,index=[0])
		base_shape = headline_series.shape[1]
		#Get features
		stock_series = sfp.GetTimeComputes(stock_info)
		headline_series = pd.concat([headline_series, pd.DataFrame(stock_series).transpose()], axis=1)
		#Combine headline info and clinic data
		clinic_data = lf.LoadClinicPipeline()
		clinics = pf.PrepareClinicalPipelineData(clinic_data, sub_select=symbol)
		clinics.reset_index(inplace=True, drop=True)
		clinics.drop('Security Symbol', axis=1, inplace=True)
		headline_series = pd.concat([headline_series, clinics], axis=1)
		#Prepare for model
		headline_series['Phase'] = phase
		headline_series['TextSent'] = predicted_sent
		test_series = headline_series.iloc[:,base_shape:]
		#Predict
		predict_model = joblib.load('BiotechModel.joblib')
		recommendation = predict_model.predict(test_series)
		headline_series['Prediction'] = recommendation
		lf.SavePrediction(headline_series)
		MacNotification(headline, symbol, recommendation)

'''
Check RSS feed
'''
def CheckRSS(phase_url, phase):
	recent_headline = lf.LoadRecentHeadline(phase)
	phase_headlines = feedparser.parse(phase_url)
	entry_len = len(phase_headlines.entries)
	for entry in range(entry_len):
		entry_headline = phase_headlines.entries[entry]['title']
		if entry_headline == recent_headline:
			print('Processed {} headlines'.format(entry))
			print('Done checking phase ' + str(phase) + ' headlines')
			return
		else:
			if entry == 0:
				lf.SaveRecentHeadline(entry_headline, phase)
			GetPrediction(entry_headline, phase)

'''
Get data from RSS feed
'''
def GetNewHeadlines():
	#Omitted for api reasons
	return None

		