import logging

# Tweeter credentials must be obtained from tweeter;
# checkout this: https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
CONSUMER_KEY = 'API_KEY'
CONSUMER_SECRET = 'SECRET'

KEY = 'Access_TOKEN'
SECRET = 'Access_TOKEN_SECRET'

MAX_RECONNECTION_ATTEMPTS = 5

ALT_BOT_NAME = 'AltBotUY'

LAST_N_TWEETS = 10

LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log/alt-bot-logs.log'

DB_FILE = 'data_access_layer/.alt_bot_data.db'

# credentials to send DM to mantainer, only for unexpected exceptions
MAINTEINER_NAME = 'ro_laguna_'
MAINTAEINER_ID = 537304416
