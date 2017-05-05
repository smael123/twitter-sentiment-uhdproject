import os
from configparser import ConfigParser
import tweepy
from textblob import TextBlob

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

places = api.geo_search(query='Texas', granularity='admin')
print(places)