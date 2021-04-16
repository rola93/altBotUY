import json
import logging
import time
from datetime import timedelta

from typing import List, Optional, Set, Union, Iterable

import tweepy

try:
    from settings_prod import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET
except Exception as e:
    print('settings_prod not found; running just with settings')
    from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET

from settings import AUTO_DM_NO_ALT_TEXT, AUTO_REPLY_NO_ALT_TEXT, PATH_TO_PROCESSED_TWEETS, LOG_LEVEL, \
    LOG_FILENAME, LAST_N_TWEETS, ALT_BOT_NAME


class AltBot:

    def __init__(self):

        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(KEY, SECRET)

        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.processed_tweets = set()  # type: Set[str]
        self.load_database()

        try:
            self.api.verify_credentials()
        except Exception as e:
            logging.error(f'Exception: {e} on authentication', exc_info=True)
            raise Exception(f"Error during authentication: {e}")

    # region: database management
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

    # endregion

    # region: Tweeter API interaction
    def get_followers(self, screen_name: str, kindly_sleep: float = 60) -> Iterable[str]:
        """
        Read the followers list for the screen_name user
        :param screen_name: user to get its followers
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: List of followers
        """

        for page in tweepy.Cursor(self.api.followers, screen_name=screen_name).pages():
            start = time.time()
            for p in page:
                yield p.screen_name
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - start), 0))

    def get_friends(self, screen_name: str, kindly_sleep: float = 60) -> Iterable[str]:
        """
        Read the users being followed for the screen_name user (i.e its friends)
        :param screen_name: user to get its friends
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: List of friends
        """

        result = []

        for page in tweepy.Cursor(self.api.friends, screen_name=screen_name).pages():
            start = time.time()
            for p in page:
                yield p.screen_name
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - start), 0))

        return result

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

    def direct_message(self, message_to: str, msg: str) -> None:
        """
        send a direct message with the msg tex to the message_to user
        :param message_to: user to recieve the DM
        :param msg: message to be send, should contain less than 10k chars
        :return: None
        """

        self.api.send_direct_message(message_to, msg)
        logging.debug(f'Direct Message to {message_to}; images without alt text')

    # endregion

    # region: main logic

    @staticmethod
    def get_tweet_url(user_screen_name: str, tweet_id: str) -> str:
        """
        Return the public url corresponding to the given tweet
        :param user_screen_name: screen name of the user who wrote the tweet
        :param tweet_id: id of thetweet
        :return: public url for the tweet
        """
        return f'https://twitter.com/{user_screen_name}/status/{tweet_id}'

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
                result = [media['ext_alt_text'] for media in status.extended_entities['media'] if
                          media['type'] == 'photo']
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

    def process_account(self, screen_name: str, follower: bool, n_tweets: int) -> None:
        """
        Process an account checking its last n_tweets:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers reply for non-followers
         - Otherwise ignore it
        :param screen_name: account to be processed
        :param follower: whether or not the screen_name account is a follower
        :param n_tweets: number of tweetsto consider
        :return: None
        """

        last_tweets = self.get_last_tweets_for_account(screen_name, n_tweets)

        for tweet_id in last_tweets:

            try:
                if self.check_if_processed(tweet_id):
                    # skip the tweet since it was already processed
                    continue

                logging.info(f'Processing tweet {self.get_tweet_url(screen_name, tweet_id)}')

                alt_texts = self.get_alt_text(tweet_id)

                if alt_texts is None or not alt_texts:
                    # skip since the tweet does not contain images
                    logging.debug(f'This tweet is not interesting for us: '
                                  f'{self.get_tweet_url(screen_name, tweet_id)}')
                    self.set_as_processed(tweet_id)
                    continue

                if all(alt_texts):
                    # all of the images contains alt_text, let's like it
                    logging.debug(f'All images in tweet contain alt texts: '
                                  f'{self.get_tweet_url(screen_name, tweet_id)}')
                    self.fav_tweet(tweet_id)
                else:
                    # there are some images withut alt_text; alert message needed
                    if follower:
                        # if it is a follower,write a DM
                        logging.debug(f'Some images in tweet does not contain alt texts: '
                                      f'{self.get_tweet_url(screen_name, tweet_id)} | '
                                      f'DM the user, this is a follower')
                        self.direct_message(screen_name, AUTO_DM_NO_ALT_TEXT.format(self.get_tweet_url(screen_name,
                                                                                                       tweet_id)))
                        # TODO: what if DMs are not available? -> sendreply tweet

                    else:
                        # if it is a follower, write a DM
                        logging.debug(f'Some images in tweet does not contain alt texts: '
                                      f'{self.get_tweet_url(screen_name, tweet_id)} | '
                                      f'reply the user, is not a follower')
                        self.reply(screen_name, AUTO_REPLY_NO_ALT_TEXT, tweet_id)

                self.set_as_processed(tweet_id)

            except Exception as e:
                logging.error(f'Exception: {e} while processing tweet '
                              f'https://twitter.com/{screen_name}/status/{tweet_id}', exc_info=True)

    def process_followers(self, screen_name: str) -> Set[str]:
        """
        Read all followers of screen_name and process each follower account with self.process_account, as followers
        :param screen_name: name of the account to process its followers
        :return: set of followers screen names
        """
        processed_followers = []

        for follower_screen_name in self.get_followers(screen_name):
            logging.info(f'Processing follower @{follower_screen_name}...')
            self.process_account(follower_screen_name, follower=True, n_tweets=LAST_N_TWEETS)
            self.dump_database()
            processed_followers.append(follower_screen_name)

        return set(processed_followers)

    def process_friends(self, screen_name: str, followers: Set[str]) -> Set[str]:
        """
        Read all friends of screen_name and process each follower account with self.process_account, as non-followers.
        If a friend is also a follower (given in the folowers set) then it is not processed.
        :param screen_name: name of the account to process its friends
        :param followers: set of followers for the screen_name account
        :return: set of friends

        """
        processed_friends = []

        for friend_screen_name in self.get_friends(screen_name):

            if friend_screen_name in followers:
                # this friend is also a follower, we can skip it
                processed_friends.append(friend_screen_name)
                continue

            logging.info(f'Processing friend @{friend_screen_name}...')
            self.process_account(friend_screen_name, follower=False, n_tweets=LAST_N_TWEETS)
            self.dump_database()
            processed_friends.append(friend_screen_name)

        return set(processed_friends)

    def watch_for_alt_text_usage(self) -> None:
        """
        Process all followers and friends of AltBotUY to check for alt_text usage:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers reply for friends
         - Otherwise ignore it
        :return: None
        """

        followers = self.process_followers(ALT_BOT_NAME)
        logging.info(f'{len(followers)} followers were processed')
        friends = self.process_friends(ALT_BOT_NAME, followers)
        logging.info(f'{len(friends)} friends were processed')

    def main(self) -> None:
        """
        Main process for the AltBotUY
        :return: None
        """
        self.watch_for_alt_text_usage()
    # endregion


if __name__ == '__main__':

    logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME+'dev')

    bot = AltBot()
    logging.debug('===== FRIENDS =====')
    for f in bot.get_friends('ro_laguna_'):
        logging.debug(f)
    logging.debug('===== FOLLOWERS =====')
    for f in bot.get_followers('ro_laguna_'):
        logging.debug(f)
    # start = time.time()
    # bot.process_accounts(ACCOUNTS_TO_CHECK)
    # took_seconds = time.time() - start
    # logging.info(f'Execution took {timedelta(seconds=took_seconds)}.')
