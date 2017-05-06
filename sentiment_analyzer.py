import os
from configparser import ConfigParser
import tweepy
from textblob import TextBlob

class Tweet:
	def __init__(self, text, mood = -1.0):
		self.text = text
		self.mood = mood
	
	def get_sentiment(self):
		self.mood = TextBlob(self.text).polarity

class TwitterQuery:
	max_tweets = 10

	def __init__(self, api, str_query, region_id, region_str):
		self.api = api
		self.str_query = str_query
		self.region_id = region_id
		self.region_str = region_str
		self.tweet_list = []
		
		self.positive_tweets = []
		self.neutral_tweets = []
		self.negative_tweets = []
		
		self.get_tweets()
	
	def get_tweets(self):
		dirty_tweets = self.api.search(q = f"place:{self.region_id} {self.str_query}", count = TwitterQuery.max_tweets)
		
		clean_text = self.clean_tweets(dirty_tweets)
		
		for tweet in clean_text:
			self.tweet_list.append(Tweet(tweet))
		
		#print(tweet.text + " | " + tweet.place.name if tweet.place else "Undefined place")
		
		for tweet_obj in self.tweet_list:
			tweet_obj.get_sentiment()
		
		for tweet_obj in self.tweet_list:
			if tweet_obj.mood > 0:
				self.positive_tweets.append(tweet_obj)
			elif tweet_obj.mood < 0:
				self.negative_tweets.append(tweet_obj)
			else:
				self.neutral_tweets.append(tweet_obj)
	
	def get_perc_negative_tweets(self):
		return (len(self.negative_tweets) / len(self.tweet_list)) * 100
	
	def get_perc_neutral_tweets(self):
		return (len(self.neutral_tweets) / len(self.tweet_list)) * 100
	
	def get_perc_positive_tweets(self):
		return (len(self.positive_tweets) / len(self.tweet_list)) * 100
	
	def get_num_tweets(self):
		return len(self.tweet_list)
	
	def get_positive_tweets(self):
		str = ''
		
		for tweet in self.positive_tweets:
			str = str + (tweet.text)
			
		return str
	
	def get_neutral_tweets(self):
		str = ''
		
		for tweet in self.neutral_tweets:
			str = str + (tweet.text)
		
		return str
	
	def get_negative_tweets(self):
		str = ''
		
		for tweet in self.negative_tweets:
			str = str + (tweet.text)
			
		return str
	
	def clean_tweets(self, dirty_tweets):
		clean_list = []
		
		for tweet in dirty_tweets:
			#print(tweet.__dict__.items())
			
			#key_list = tweet.__dict__.keys()
			
			#value_list = tweet.__dict__.values()
			
			#for i in range (0, len(key_list)):
				#print(key_list[i] + " " + value_list[i])
			

			link_list = []
			for link in tweet.entities['urls']:
				link_list.append(link['url'])
			
			mention_list = []
			for mention in tweet.entities['user_mentions']:
				mention_list.append(f"@{mention['screen_name']}")
				
			cleaned_tweet = tweet.text
			
			for link in link_list:
				cleaned_tweet = cleaned_tweet.replace(link, "")
			
			#for mention in mention_list:
			#	cleaned_tweet = cleaned_tweet.replace(mention, "")
			
			#http://stackoverflow.com/questions/15321138/removing-unicode-u2026-like-characters-in-a-string-in-python2-7
			#cleaned_tweet = str(cleaned_tweet.encode('ascii','ignore'))
			
			clean_list.append(cleaned_tweet)
		
		return clean_list
		
	def __str__(self):
		str = ''
	
		str = str + (f"Results for {self.region_str}\n")
		str = str + (f"Positive Percentage: {self.get_perc_positive_tweets()}%\n")
		str = str + (f"Negative Percentage: {self.get_perc_negative_tweets()}%\n\n")

		str = str + ("Positive Tweets:\n")
		str = str + (self.get_positive_tweets() + '\n\n')
		str = str + ("Neutral Tweets:\n")
		str = str + (self.get_neutral_tweets() + '\n\n')
		str = str + ("Negative Tweets:\n")
		str = str + (self.get_negative_tweets() + '\n\n')
		
		return str

cfg = ConfigParser()

cfg.read(os.path.join(os.pardir, os.pardir, 'twitter.ini'))
twitter_consumer_key = cfg.get('twitter_keys', 'consumer_key')
twitter_consumer_secret = cfg.get('twitter_keys', 'consumer_secret')
twitter_access_token = cfg.get('twitter_keys', 'access_token')
twitter_access_secret = cfg.get('twitter_keys', 'access_secret')

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_secret)

api = tweepy.API(auth)

places = api.geo_search(query='USA', granularity='country')
usa_id = places[0].id

str_query = input("What string would you like to search for?")

usa_test = TwitterQuery(api, str_query, usa_id, "USA")
print(usa_test)

#Let's crate a map

state_list = ("Alabama", "Alaska", "Arizona", "Arkansas", "California","Colorado","Connecticut","Delaware",
"Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
"Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
"New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon"
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia",
"Washington","West Virginia","Wisconsin","Wyoming")

state_dict = {}
state_queries = []

for state in state_list[0:2]:
	places = api.geo_search(query=state, granularity='admin')
	state_dict[state] = places[0].id
	query = TwitterQuery(api, str_query, state_dict[state], state)
	#query.get_tweets()
	state_queries.append(query)
	print(query)