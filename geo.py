'''The following program gets the location ids from the Twitter API (geo_search) https://dev.twitter.com/rest/reference/get/geo/search
This operation will reach your rate limit but it is necessary to do in order to get tweets from certain states'''

import os
from configparser import ConfigParser
import tweepy
from textblob import TextBlob

cfg = ConfigParser()

cfg.read(os.path.join("necessary_files", 'twitter.ini'))
twitter_consumer_key = cfg.get('twitter_keys', 'consumer_key')
twitter_consumer_secret = cfg.get('twitter_keys', 'consumer_secret')
twitter_access_token = cfg.get('twitter_keys', 'access_token')
twitter_access_secret = cfg.get('twitter_keys', 'access_secret')

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_secret)

api = tweepy.API(auth)

state_list = ("Alabama", "Alaska", "Arizona", "Arkansas", "California","Colorado","Connecticut","Delaware",
"Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
"Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
"New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia",
"Washington","West Virginia","Wisconsin","Wyoming")

geo_file = open("geo.txt", 'a')

try:
	for state in state_list[0:2]:
		places = api.geo_search(query=state, granularity='admin')
		print(f"{state}\t{places[0].id}\n")
		geo_file.write(f"{state}\t{places[0].id}\n")
		
	geo_file.close()
	print("Success id codes have been written to a file called geo.txt")
except tweepy.error.RateLimitError:
	print("rate limit exceeded")
	geo_file.close()
except e:
	print("error:", e)
	geo_file.close()
	
	
#print(places)