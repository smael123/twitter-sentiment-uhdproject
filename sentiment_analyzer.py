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

	def __init__(self, api, str_query, region_query = None):
		self.api = api
		self.str_query = str_query
		self.region_query = region_query
		self.tweet_list = []
		
		self.positive_tweets = []
		self.neutral_tweets = []
		self.negative_tweets = []
		
		self.get_tweets()
	
	def get_tweets(self):
		dirty_tweets = self.api.search(q = f"place:{self.region_query} {self.str_query}", count = TwitterQuery.max_tweets)
		
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
	
	def print_positive_tweets(self):
		for tweet in self.positive_tweets:
			print(tweet.text)
	
	def print_neutral_tweets(self):
		for tweet in self.neutral_tweets:
			print(tweet.text)
	
	def print_negative_tweets(self):
		for tweet in self.negative_tweets:
			print(tweet.text)
	
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

cfg = ConfigParser()

cfg.read(os.path.join(os.pardir, os.pardir, 'twitter.ini'))
twitter_consumer_key = cfg.get('twitter_keys', 'consumer_key')
twitter_consumer_secret = cfg.get('twitter_keys', 'consumer_secret')
twitter_access_token = cfg.get('twitter_keys', 'access_token')
twitter_access_secret = cfg.get('twitter_keys', 'access_secret')

#use this to test if your keys work
auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_secret)

api = tweepy.API(auth)

"""places = api.geo_search(query='USA', granularity='country')
usa_id = places[0].id

usa_test = TwitterQuery(api, "Donald Trump", usa_id)
#usa_test.get_tweets()

print(f"Positive Percentage: {usa_test.get_perc_positive_tweets()}%")
print(f"Negative Percentage: {usa_test.get_perc_negative_tweets()}%\n")

print("Positive Tweets:\n")
usa_test.print_positive_tweets()
print("\nNeutral Tweets:")
usa_test.print_neutral_tweets()
print("\nNegative Tweets:\n")
usa_test.print_negative_tweets()"""

#Let's crate a map
 
state_list = ("Alabama", "Alaska", "Arizona", "Arkansas", "California","Colorado","Connecticut","Delaware",
"Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
"Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
"New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon"
"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia",
"Washington","West Virginia","Wisconsin","Wyoming")

state_dict = {}

for state in state_list:
	places = api.geo_search(query=state, granularity='admin')
	state_dict[state] = places[0].id
	
state_queries = []

for state in state_list:
	query = TwitterQuery(api, "Donald Trump", state_dict[state])
	#query.get_tweets()
	state_queries.append(query)
	
for state_query in state_queries:
	print(f"Positive Percentage: {state_query.get_perc_positive_tweets()}%")
	print(f"Negative Percentage: {state_query.get_perc_negative_tweets()}%\n")

	print("Positive Tweets:\n")
	state_query.print_positive_tweets()
	print("\nNeutral Tweets:")
	state_query.print_neutral_tweets()
	print("\nNegative Tweets:\n")
	state_query.print_negative_tweets()