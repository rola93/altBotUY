import logging

# Tweeter credentials must be obtained from tweeter;
# checkout this: https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
CONSUMER_KEY = 'API_KEY'
CONSUMER_SECRET = 'SECRET'

KEY = 'Access_TOKEN'
SECRET = 'Access_TOKEN_SECRET'

MAX_RECONNECTION_ATTEMPTS = 5
MAX_MENTIONS_TO_PROCESS = 3
MAX_DAYS_TO_REFRESH_TWEETS = 1

ALT_BOT_NAME = 'AltBotUY'

LAST_N_TWEETS = 25
LAST_N_MENTIONS = 100

LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log/alt-bot-logs.log'

DB_FILE = 'data_access_layer/.alt_bot_data.db'

# credentials to send DM to mantainer, only for messages on unexpected exceptions
MAINTEINER_NAME = 'ro_laguna_'
MAINTAEINER_ID = 537304416

# ID of the tweet that users must RT to allow for DMs:
# https://twitter.com/AltBotUY/status/1385971762819706888
ACCEPT_DM_TWEET_ID = 1385971762819706888

INIT_SYSTEM_DATE = '2021-01-01'
