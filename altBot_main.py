import json
import logging
import time
from datetime import timedelta

from typing import List, Optional, Set, Union

import tweepy

try:
    from settings_prod import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET
except Exception as e:
    print('settings_prod not found; running just with settings')
    from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET

from settings import ACCOUNTS_TO_CHECK, AUTO_REPLY_NO_ALT_TEXT, PATH_TO_PROCESSED_TWEETS, LOG_LEVEL, \
    LOG_FILENAME, LAST_N_TWEETS


class AltBot:

    def __init__(self):

        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(KEY, SECRET)

        self.api = tweepy.API(self.auth)
        self.processed_tweets = set()  # type: Set[str]
        self.load_database()

        try:
            self.api.verify_credentials()
        except Exception as e:
            logging.error(f'Exception: {e} on authentication', exc_info=True)
            raise Exception(f"Error during authentication: {e}")

    def load_database(self) -> None:
        """
        load database with the tweet ids that were processed
        :return: None
        """

        with open(PATH_TO_PROCESSED_TWEETS, 'r') as f:
            processed_tweets = json.load(f)

        self.processed_tweets = set(processed_tweets['tweets'])

    def dump_database(self) -> None:
        """
        dump database to save the tweet ids that were processed
        :return: None
        """

        with open(PATH_TO_PROCESSED_TWEETS, 'w') as f:
            json.dump({'tweets': list(self.processed_tweets)}, f)

    def check_if_processed(self, tweet_id: str) -> bool:
        """
        Given a tweet id, checks whether or not it was processed.
        This is to avoid duplicates of the same tweet being processed multiple times
        :param tweet_id: id of the tweet to
        :return: True iff the tweet was already processed
        """
        return tweet_id in self.processed_tweets

    def set_as_processed(self, tweet_id: str) -> None:
        """
        Given a tweet id, set the tweet as processed.
        This is to avoid duplicates of the same tweet being processed multiple times
        :param tweet_id: id of the tweet to
        :return: None
        """
        return self.processed_tweets.add(tweet_id)

    def get_last_tweets_for_account(self, screen_name: str, n_tweets: int, include_rts: bool = False) -> List[str]:

        results = self.api.user_timeline(screen_name=screen_name,
                                         # 200 is the maximum allowed count
                                         count=n_tweets,
                                         include_rts=include_rts,
                                         # Necessary to keep full_text
                                         # otherwise only the first 140 words are extracted
                                         tweet_mode='extended'
                                         )

        tweets_ids = [tweet.id_str for tweet in results]

        return tweets_ids

    def fav_tweet(self, tweet_id: str) -> None:
        """
        Add a fav (like) to the tweet with id tweet_id
        :param tweet_id: id of the tweet to be faved
        :return: None
        """
        self.api.create_favorite(tweet_id)
        logging.debug(f'fav {tweet_id}')

    def reply(self, reply_to: str, msg: str, tweet_id: str) -> None:
        """
        Write a tweet in response to the tweet_id with te message msg
        :param reply_to: string containing the user to reply the tweet
        :param msg: string containing the message to tweet
        :param tweet_id: tweet ID to reply
        :return: None
        """
        self.api.update_status(
            status=f'@{reply_to} {msg}',
            in_reply_to_status_id=tweet_id
        )
        logging.debug(f'reply {tweet_id}; images without alt text')

    def get_alt_text(self, tweet_id: str) -> Optional[List[Union[str, None]]]:
        """
        This method gets back alt_text from the given tweet_id
        :param tweet_id: str identifying a tweet
        :return: if the tweet does not contain media, returns None
                 if the tweet contain images, returns a list with.
                     Each element of the list contains a string with the alt_text if available,
                     None otherwise.
                Consider a single tweet may contain up to 4 images and each of them can not contain an alt_text.
        """

        status = self.api.get_status(tweet_id, include_ext_alt_text=True, include_entities=True)

        if hasattr(status, 'extended_entities'):
            if len(status.extended_entities['media']) > 0:
                result = [media['ext_alt_text'] for media in status.extended_entities['media'] if media['type'] == 'photo']
                logging.debug(f'Tweet {tweet_id} contains extended_entities and media: {result}.')
            else:
                # This is a tweet without media, not sure if this can happen
                logging.debug(f'Tweet {tweet_id} contains extended_entities but not media.')
                result = None
        else:
            # This is a tweet without images or multimedia
            logging.debug(f'Tweet {tweet_id} does not contain extended_entities.')
            result = None

        return result

    def process_account(self, screen_name: str):

        last_tweets = self.get_last_tweets_for_account(screen_name, LAST_N_TWEETS)

        for tweet_id in last_tweets:

            try:
                if self.check_if_processed(tweet_id):
                    # skip the tweet since it was already processed
                    continue

                logging.info(f'Processing tweet https://twitter.com/{screen_name}/status/{tweet_id}')

                alt_texts = self.get_alt_text(tweet_id)

                if alt_texts is None or not alt_texts:
                    # skip since the tweet does not contain images
                    logging.debug(f'This tweet is not interesting for us: '
                                  f'https://twitter.com/{screen_name}/status/{tweet_id}')
                    self.set_as_processed(tweet_id)
                    continue

                if all(alt_texts):
                    # all of the images contains alt_text, let's like it
                    logging.debug(f'All images in tweet contain alt texts: '
                                  f'https://twitter.com/{screen_name}/status/{tweet_id}')
                    self.fav_tweet(tweet_id)
                else:
                    logging.debug(f'Some images in tweet does not contain alt texts: '
                                  f'https://twitter.com/{screen_name}/status/{tweet_id}')
                    self.reply(screen_name, AUTO_REPLY_NO_ALT_TEXT, tweet_id)

                self.set_as_processed(tweet_id)

            except Exception as e:
                logging.error(f'Exception: {e} while processing tweet '
                              f'https://twitter.com/{screen_name}/status/{tweet_id}', exc_info=True)

    def process_accounts(self, screen_names: List[str]) -> None:
        """
        Process a batch of accounts
        :param screen_names: list of tweeter accounts to be processed
        :return: None
        """
        for screen_name in screen_names:
            logging.info(f'Processing @{screen_name}...')
            self.process_account(screen_name)
            self.dump_database()


if __name__ == '__main__':

    logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME)

    bot = AltBot()
    start = time.time()
    bot.process_accounts(ACCOUNTS_TO_CHECK)
    took_seconds = time.time() - start

    logging.info(f'Execution took {timedelta(seconds=took_seconds)}.')
