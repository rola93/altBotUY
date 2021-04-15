import logging

# Tweeter credentials must be obtained from tweeter;
# checkout this: https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
CONSUMER_KEY = 'API_KEY'
CONSUMER_SECRET = 'SECRET'

KEY = 'Access_TOKEN'
SECRET = 'Access_TOKEN_SECRET'

PATH_TO_PROCESSED_TWEETS = 'processed_tweets.json'

AUTO_REPLY_NO_ALT_TEXT = 'Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir ' \
                         'todas sus imágenes...'

ACCOUNTS_TO_CHECK = ['ro_laguna_', 'raulsperoni', 'mili_costabel', 'bryant1410']
LAST_N_TWEETS = 50

LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log/alt-bot-logs.log'
