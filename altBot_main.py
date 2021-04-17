import json
import logging
import time
from datetime import timedelta

from typing import List, Optional, Set, Union, Iterable, Tuple

import tweepy

try:
    from settings_prod import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET
except Exception as e:
    print('settings_prod not found; running just with settings')
    from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET

from bot_messages import AUTO_DM_NO_ALT_TEXT, AUTO_REPLY_NO_ALT_TEXT, AUTO_REPLY_NO_DM_NO_ALT_TEXT
from settings import PATH_TO_PROCESSED_TWEETS, LOG_LEVEL, \
    LOG_FILENAME, LAST_N_TWEETS, ALT_BOT_NAME, MAX_RECONNECTION_ATTEMPTS


class AltBot:

    def __init__(self, live: bool = True):
        """
        Init the AltBot object which contains all code needed to execute it
        :param live: if True, the tweets/favs and DMs are sent. Useful for development
        """

        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(KEY, SECRET)
        self.live = live

        self.processed_tweets = set()  # type: Set[str]
        self.load_database()

        self.api = None  # type: tweepy.API
        self.alt_bot_user = None  # type: tweepy.models.User

        self.connect_api()
        self.load_alt_bot_user()

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
    def connect_api(self) -> None:
        """
        Stablish a connection with the Tweeter API. In case some other opperation get the connection closed,
        reopen it again
        :return: None; self.api is instantiated when succeeds, otherwise raises an arror
        """

        i = 0
        while i < MAX_RECONNECTION_ATTEMPTS:
            try:
                self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                break
            except Exception as e:
                logging.warning(f'[{i}/{MAX_RECONNECTION_ATTEMPTS}] Can not connect: {e}')
                i += 1

        if i >= MAX_RECONNECTION_ATTEMPTS:
            msj = f'[{i}/{MAX_RECONNECTION_ATTEMPTS}] Can not connect.'
            logging.error(msj)
            raise Exception(msj)
        logging.info('Connected to Tweeter API')

    def load_alt_bot_user(self):
        self.alt_bot_user = self.api.verify_credentials()

        if not self.alt_bot_user:
            raise Exception('Can not connect: verify credentials')

        logging.info('Credentials are ok.')

    def get_followers(self, screen_name: str, kindly_sleep: float = 60) -> Iterable[Tuple[str, int]]:
        """
        Read the followers list for the screen_name user
        :param screen_name: user to get its followers
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: yields pair of  (screen_name, id)
        """
        for page in tweepy.Cursor(self.api.followers, screen_name=screen_name, count=500).pages():
            start = time.time()
            for p in page:
                yield p.screen_name, p.id
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - start), 0))

    def get_friends(self, screen_name: str, kindly_sleep: float = 60) -> Iterable[Tuple[str, int]]:
        """
        Read the users being followed for the screen_name user (i.e its friends)
        :param screen_name: user to get its friends
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: yields pair of  (screen_name, id)
        """

        result = []

        for page in tweepy.Cursor(self.api.friends, screen_name=screen_name, count=500).pages():
            start = time.time()
            for p in page:
                yield p.screen_name, p.id
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - start), 0))

        return result

    def get_last_tweets_for_account(self, screen_name: str, n_tweets: int, include_rts: bool = False) -> List[str]:
        """
        get the last n_tweets for @screen_name user, as a list of tweeter_id strings
        :param screen_name: name of the account to extract its tweets
        :param n_tweets: max number of tweets to extract of accounts, 0 <= n_tweets <= 200
        :param include_rts: wether to include re tweets or not
        :return: List of ids for last tweets
        """

        try:
            results = self.api.user_timeline(screen_name=screen_name,
                                             # 200 is the maximum allowed count
                                             count=n_tweets,
                                             include_rts=include_rts,
                                             # Necessary to keep full_text
                                             # otherwise only the first 140 words are extracted
                                             tweet_mode='extended'
                                             )

            tweets_ids = [tweet.id_str for tweet in results]
        except tweepy.error.TweepError as tpe:
            # TODO: why? what should we do?
            logging.error(f'can not extract tweets for {screen_name}: {tpe}')
            tweets_ids = []

        return tweets_ids

    def fav_tweet(self, tweet_id: str) -> None:
        """
        Add a fav (like) to the tweet with id tweet_id
        :param tweet_id: id of the tweet to be faved
        :return: None
        """
        if self.live:
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
        if self.live:
            self.api.update_status(
                status=f'@{reply_to} {msg}',
                in_reply_to_status_id=tweet_id
            )
        logging.debug(f'reply tweet to {tweet_id}')

    def direct_message(self, recipient_name: str, recipient_id: int, msg: str) -> int:
        """
        send a direct message with the msg tex to the message_to user
        :param recipient_name: user name of user to recieve the DM, just for logging
        :param recipient_id: user to recieve the DM
        :param msg: message to be send, should contain less than 10k chars
        :return:
            0 if everything went ok;
            1 if could not send message for 349
            -1 otherwise
        """
        try:
            if self.live:
                self.api.send_direct_message(recipient_id, msg)
            logging.debug(f'send Direct Message to {recipient_id};')
            ret = 0

        except tweepy.error.TweepError as tw_error:

            if tw_error.api_code == 349:
                # we do not follow the user or DMs are closed or we're blocked
                logging.debug(f'Can not send message to {recipient_name}: {tw_error}')
                ret = 1
            else:
                logging.error(f'Unknown: Can not send message to {recipient_name}: {tw_error}')
                ret = -1

        return ret

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

    @staticmethod
    def compute_alt_text_score(alt_texts: List[Union[str, None]]) -> float:
        """
        Return the portion of alt_texts which in fact contain alt_text
        :param alt_texts: non-empty list of alt_texts
        :return: score in [0,1]
        """

        alt_text_count = [1 if at else 0 for at in alt_texts]

        return round(sum(alt_text_count) / len(alt_text_count), 2)

    def process_account(self, screen_name: str, user_id: int, follower: bool, n_tweets: int) -> None:
        """
        Process an account checking its last n_tweets:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers reply for non-followers
         - Otherwise ignore it
        :param screen_name: account to be processed
        :param user_id: user_id to be processed, only used to send DMs (followers)
        :param follower: whether or not the screen_name account is a follower
        :param n_tweets: number of tweets to consider
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

                alt_text_score = self.compute_alt_text_score(alt_texts)

                if alt_text_score == 1:
                    # all of the images contains alt_text, let's like it
                    logging.debug(f'All images in tweet contain alt texts: '
                                  f'{self.get_tweet_url(screen_name, tweet_id)}')
                    self.fav_tweet(tweet_id)
                else:
                    # there are some images without alt_text; alert message needed
                    if follower:
                        # if it is a follower, write a DM
                        logging.debug(f'Some images ({alt_text_score*100} %) in tweet does not contain alt texts: '
                                      f'{self.get_tweet_url(screen_name, tweet_id)} | '
                                      f'DM the user, this is a follower')
                        res = self.direct_message(screen_name, user_id, AUTO_DM_NO_ALT_TEXT.format(self.get_tweet_url(screen_name,
                                                                                                       tweet_id)))
                        if res == -1:
                            # The user follows us, but we can't DM it, so reply with a tweet
                            self.reply(screen_name, AUTO_REPLY_NO_DM_NO_ALT_TEXT, tweet_id)

                    else:
                        # if it is a follower, write a DM
                        logging.debug(f'Some images ({alt_text_score*100} %) in tweet does not contain alt texts: '
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

        logging.info(f'Extracting followers from @{screen_name}')
        followers = [follower for follower in self.get_followers(screen_name)]  # type: List[Tuple[str, int]]
        n_followers = len(followers)
        logging.info(f'{n_followers} followers extracted for @{screen_name}')

        for i, (follower_screen_name, follower_id) in enumerate(followers):

            logging.info(f'[{i}/{n_followers}] Processing follower @{follower_screen_name}...')

            try:
                self.process_account(follower_screen_name, follower_id, follower=True, n_tweets=LAST_N_TWEETS)
            except Exception as e:
                logging.error(f'Error while processing follower: {follower_screen_name}:\n{e}')
                continue
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

        logging.info(f'Extracting friends from @{screen_name}')
        friends = [friend for friend in self.get_friends(screen_name)]  # type: List[Tuple[str, int]]
        n_friends = len(friends)
        logging.info(f'{n_friends} friends extracted for @{screen_name}')

        for i, (friend_screen_name, friend_id) in enumerate(friends):

            if friend_screen_name in followers:
                # this friend is also a follower, we can skip it
                processed_friends.append(friend_screen_name)
                continue

            logging.info(f'[{i}/{n_friends}] Processing friend @{friend_screen_name}...')

            try:
                self.process_account(friend_screen_name, friend_id, follower=False, n_tweets=LAST_N_TWEETS)
            except Exception as e:
                logging.error(f'Error while processing follower: {friend_screen_name}:\n{e}')
                continue

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

    logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME+'dev',
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S'
                        )

    bot = AltBot(live=False)

    start = time.time()
    bot.main()
    took_seconds = time.time() - start

    msj = f'Execution ended, took {timedelta(seconds=took_seconds)}.'
    logging.info(msj)

    ro_id = 537304416

    bot.direct_message('ro_laguna_', ro_id, msj)
