import json
from typing import List, Optional, Union
from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET, PATH_TO_PROCESSED_TWEETS

import tweepy


class AltBot:

    def __init__(self):

        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(KEY, SECRET)

        self.api = tweepy.API(self.auth)
        self.processed_tweets = []  # type: List[str]
        self.load_database()

        try:
            self.api.verify_credentials()
        except Exception as e:
            raise Exception(f"Error during authentication: {e}")

    def load_database(self) -> None:
        """
        load database with the tweet ids that were processed
        :return: None
        """

        with open(PATH_TO_PROCESSED_TWEETS, 'r') as f:
            processed_tweets = json.load(f)

        self.processed_tweets = processed_tweets['tweets']

    def dump_database(self) -> None:
        """
        dump database to save the tweet ids that were processed
        :return: None
        """

        with open(PATH_TO_PROCESSED_TWEETS, 'w') as f:
            json.dump({'tweets': self.processed_tweets}, f)

    def check_if_processed(self, tweet_id: str) -> bool:
        """
        Given a tweet id, checks whether or not it was processed.
        This is to avoid duplicates of the same tweet being processed multiple times
        :param tweet_id: id of the tweet to
        :return: True iff the tweet was already processed
        """
        return tweet_id in self.processed_tweets

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

    def reply(self, msg: str, tweet_id: str) -> None:
        """
        Write a tweet in response to the tweet_id with te message msg
        :param msg: string containing the message to tweet
        :param tweet_id: tweet ID to reply
        :return: None
        """
        self.api.update_status(
            status=msg,
            in_reply_to_status_id=tweet_id
        )

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
                result = [media['ext_alt_text']for media in status.extended_entities['media']]
            else:
                # This is a tweet without media, not sure if this can happen
                result = None
        else:
            # This is a tweet without images or multimedia
            result = None

        return result

    def process_account(self, screen_name: str):
        last_tweets = self.get_last_tweets_for_account(screen_name, 5)

        for tweet_id in last_tweets:

            if self.check_if_processed(tweet_id):
                # skip the tweet since it was already processed
                continue

            alt_texts = self.get_alt_text(tweet_id)

            if alt_texts is None:
                # skip since the tweet does not contain images
                continue

            if any(alt_texts):
                # at least one of the images contains alt_text, let's like it
                self.fav_tweet(tweet_id)
            else:
                self.reply('Buenas! Estaría bueno que usen textos alternativos (alt_text) para '
                           'describir las imágenes, y así hacerlos accesibles a quienes no pueden verlas... Saludos!', tweet_id)

    def process_accounts(self, screen_names: List[str]) -> None:
        """
        Process a batch of accounts
        :param screen_names: list of tweeter accounts to be processed
        :return: None
        """
        for screen_name in screen_names:
            self.process_account(screen_name)


if __name__ == '__main__':

    bot = AltBot()

    # print('alt_text sample:')
    # r = bot.get_alt_text('1373498941732454402')
    # print(r)
    # print('='*10)
    #
    # print('common answer tweet, no media:')
    # r = bot.get_alt_text('1373500714606075905')
    # print(r)
    # print('=' * 10)

    # Following two tests are not running as expected.
    # print('single image no alt sample:')
    # r = bot.get_alt_text('1380902052050702338')
    # print(r)
    # print('=' * 10)
    # following sample is not working as expected:
    print('two images no alt sample:')
    r = bot.get_alt_text('1380570480269266948')
    print(r)
    print('=' * 10)


