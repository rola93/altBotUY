import logging

# Tweeter credentials must be obtained from tweeter;
# checkout this: https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
CONSUMER_KEY = 'API_KEY'
CONSUMER_SECRET = 'SECRET'

KEY = 'Access_TOKEN'
SECRET = 'Access_TOKEN_SECRET'

MAX_RECONNECTION_ATTEMPTS = 5

ALT_BOT_NAME = 'AltBotUY'

ACCOUNTS_TO_CHECK = ['ro_laguna_', 'raulsperoni', 'mili_costabel', 'bryant1410']
LAST_N_TWEETS = 10

PATH_TO_PROCESSED_TWEETS = 'processed_tweets.json'
LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log/alt-bot-logs.log'
