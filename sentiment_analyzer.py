import os
from configparser import ConfigParser
import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
import codecs

class Tweet:
	def __init__(self, text, mood = -1.0):
		self.text = text
		self.mood = mood
		
		self.get_sentiment()
	
	def get_sentiment(self):
		self.mood = TextBlob(self.text).polarity

class TwitterQuery:
	max_tweets = 20

	def __init__(self, api, str_query, region_id, region_str):
		self.api = api
		self.str_query = str_query
		self.region_id = region_id
		self.region_str = region_str
		
		self.positive_tweets = []
		self.neutral_tweets = []
		self.negative_tweets = []
		
		self.get_tweets()
	
	def get_tweets(self):
		dirty_tweets = self.api.search(q = f"place:{self.region_id} {self.str_query}", count = TwitterQuery.max_tweets)
		
		if len(dirty_tweets) == 0:
			print("No tweets found for that query")
		
		clean_text = self.clean_tweets(dirty_tweets)
		
		tweet_list = []
		
		for tweet in clean_text:
			tweet_list.append(Tweet(tweet))
		
		#print(tweet.text + " | " + tweet.place.name if tweet.place else "Undefined place")
		
		#for tweet_obj in self.tweet_list:
		#	tweet_obj.get_sentiment()
		
		for tweet_obj in tweet_list:
			if tweet_obj.mood > 0:
				self.positive_tweets.append(tweet_obj)
			elif tweet_obj.mood < 0:
				self.negative_tweets.append(tweet_obj)
			else:
				self.neutral_tweets.append(tweet_obj)
	
	def get_perc_negative_tweets(self):
		try:
			return (len(self.negative_tweets) / (len(self.negative_tweets) + len(self.neutral_tweets) + len(self.positive_tweets))) * 100
		except ZeroDivisionError:
			return 0
	
	def get_perc_neutral_tweets(self):
		try:
			return (len(self.neutral_tweets) / (len(self.negative_tweets) + len(self.neutral_tweets) + len(self.positive_tweets))) * 100
		except ZeroDivisionError:
			return 0
	
	def get_perc_positive_tweets(self):
		try:
			return (len(self.positive_tweets) / (len(self.negative_tweets) + len(self.neutral_tweets) + len(self.positive_tweets))) * 100
		except ZeroDivisionError:
			return 0
	
	def get_num_tweets(self):
		return len(self.negative_tweets) + len(self.neutral_tweets) + len(self.positive_tweets)
	
	def get_max_sentiment(self):	
		if (self.get_perc_positive_tweets() > 50):
			return 'positive'
		elif (self.get_perc_neutral_tweets() > 50):
			return 'neutral'
		elif (self.get_perc_negative_tweets() > 50):
			return 'negative'
		else:
			return 'none'
	
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
			link_list = []
			for link in tweet.entities['urls']:
				link_list.append(link['url'])
			
			#mention_list = []
			#for mention in tweet.entities['user_mentions']:
			#	mention_list.append(f"@{mention['screen_name']}")
				
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
		str = str + (f"Neutral Percentage: {self.get_perc_neutral_tweets()}%\n")
		str = str + (f"Negative Percentage: {self.get_perc_negative_tweets()}%\n\n")

		str = str + ("Positive Tweets:\n")
		str = str + (self.get_positive_tweets() + '\n\n')
		str = str + ("Neutral Tweets:\n")
		str = str + (self.get_neutral_tweets() + '\n\n')
		str = str + ("Negative Tweets:\n")
		str = str + (self.get_negative_tweets() + '\n\n')
		
		return str

		
class SentimentAnalyzer:
	state_list = ("Alabama", "Alaska", "Arizona", "Arkansas", "California","Colorado","Connecticut","Delaware",
		"Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
		"Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
		"New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
		"Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia",
		"Washington","West Virginia","Wisconsin","Wyoming")
		
	def __init__(self, str_query):
		self.str_query = str_query

		self.twitter_keys = self.read_config_file()
		
		self.api = self.connect_to_api()
		self.usa_id = self.get_usa_id()
		
		self.console_file = codecs.open("console.txt",'w','utf-8')
		
		self.state_queries = []
		self.state_ids = self.get_state_ids()
		self.get_state_queries()
		
		self.console_file.close()
		self.create_us_map()
		
	def read_config_file(self):
		cfg = ConfigParser()

		cfg.read(os.path.join('necessary_files', 'twitter.ini'))
		twitter_consumer_key = cfg.get('twitter_keys', 'consumer_key')
		twitter_consumer_secret = cfg.get('twitter_keys', 'consumer_secret')
		twitter_access_token = cfg.get('twitter_keys', 'access_token')
		twitter_access_secret = cfg.get('twitter_keys', 'access_secret')
		
		return {'twitter_consumer_key' : twitter_consumer_key, 'twitter_consumer_secret': twitter_consumer_secret, 'twitter_access_token': twitter_access_token, 'twitter_access_secret' : twitter_access_secret}
		
	def connect_to_api(self):
		auth = tweepy.OAuthHandler(self.twitter_keys['twitter_consumer_key'], self.twitter_keys['twitter_consumer_secret'])
		auth.set_access_token(self.twitter_keys['twitter_access_token'], self.twitter_keys['twitter_access_secret'])

		return tweepy.API(auth)
	
	def get_usa_id(self):
		places = self.api.geo_search(query='USA', granularity='country')
		return places[0].id
	
	def get_usa_query(self):
		usa_query = TwitterQuery(api, str_query, usa_id, "USA")
		print(usa_query)
		console_file.write(str(usa_test))
	
	def get_state_ids(self):
		try:
			state_ids = []
			geo_file = open(os.path.join('necessary_files', 'geo.txt'), 'r')
			for line in geo_file:
				state_ids.append(line.split()[-1])

			geo_file.close()
			
			return state_ids
		except FileNotFoundError as fe:
			print("geo.txt not found in necessary_files. Please run geo.py before running this program.")
			return
		except ex:
			print("Error:", ex)
	
	def get_state_queries(self):
		i = 0	
		print(len(self.state_ids))
		for state in self.state_list:
			query = TwitterQuery(self.api, self.str_query, self.state_ids[i], state)
			self.state_queries.append(query)
			print(query)
			self.console_file.write(str(query))
			i += 1
			
	def create_us_map(self):
		#Let's create a map	
		bmap = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
				  projection='lcc',lat_1=33,lat_2=45,lon_0=-95)

		shapefile_loc = os.path.join('necessary_files', 'st99_d00')		  
				  
		# load the shapefile, use the name 'states'
		bmap.readshapefile(shapefile_loc, name='states', drawbounds=True)


		# collect the state names from the shapefile attributes so we can
		# look up the shape obect for a state by it's name
		state_names = []
		for shape_dict in bmap.states_info:
			 state_names.append(shape_dict['NAME'])

		ax = plt.gca() # get current axes instance
		#print(ax.get_xlim())
		#print(ax.get_ylim())
		ax.set_xlim([-4000000, 4777416.6])
		ax.set_ylim([0, 6000000])

		# get Texas and draw the filled polygon
		#seg = map.states[state_names.index('Texas')]
		#poly = Polygon(seg, facecolor='red',edgecolor='red')
		#ax.add_patch(poly)

		for state_query in self.state_queries:
			if (state_query.get_max_sentiment() == 'positive'):
				seg = bmap.states[state_names.index(state_query.region_str)]
				poly = Polygon(seg, facecolor='red',edgecolor='red')
				ax.add_patch(poly)
			elif (state_query.get_max_sentiment() == 'neutral'):
				seg = bmap.states[state_names.index(state_query.region_str)]
				poly = Polygon(seg, facecolor='gray',edgecolor='gray')
				ax.add_patch(poly)
			elif state_query.get_max_sentiment() == 'negative':
				seg = bmap.states[state_names.index(state_query.region_str)]
				poly = Polygon(seg, facecolor='blue',edgecolor='blue')
				ax.add_patch(poly)
			else:
				pass

		#console_file.close()
		plt.tight_layout()
		plt.show()

