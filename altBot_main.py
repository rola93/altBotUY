import argparse
import logging
import os
import time
from datetime import timedelta, datetime
from typing import List, Optional, Set, Union, Tuple

import tweepy

from bot_messages import AUTO_DM_NO_ALT_TEXT, AUTO_REPLY_NO_ALT_TEXT, AUTO_REPLY_NO_DM_NO_ALT_TEXT
from data_access_layer.data_access import DBAccess

try:
    from settings_prod import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET
except Exception as e:
    print('settings_prod not found; running just with settings')
    from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET

from settings import LOG_LEVEL, LOG_FILENAME, LAST_N_TWEETS, ALT_BOT_NAME, MAX_RECONNECTION_ATTEMPTS, \
    MAINTEINER_NAME, MAINTAEINER_ID


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
        self.db = DBAccess()

        self.api = None  # type: tweepy.API
        self.alt_bot_user = None  # type: tweepy.models.User

        self.connect_api()
        self.load_alt_bot_user()

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
            msg = f'[{i}/{MAX_RECONNECTION_ATTEMPTS}] Can not connect.'
            logging.error(msg)
            raise Exception(msg)
        logging.info('Connected to Tweeter API')

    def load_alt_bot_user(self):
        self.alt_bot_user = self.api.verify_credentials()

        if not self.alt_bot_user:
            raise Exception('Can not connect: verify credentials')

        logging.info('Credentials are ok.')

    def get_followers_from_api(self, screen_name: str, kindly_sleep: float = 60) -> Set[Tuple[str, int]]:
        """
        Read the followers list for the screen_name user
        :param screen_name: user to get its followers
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: yields pair of  (screen_name, id)
        """
        result = set()  # type: Set[Tuple[str, int]]

        for page in tweepy.Cursor(self.api.followers, screen_name=screen_name, count=500).pages():
            begin = time.time()
            for p in page:
                result.add((p.screen_name, p.id))
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - begin), 0))

        return result

    def get_friends_from_api(self, screen_name: str, kindly_sleep: float = 60) -> Set[Tuple[str, int]]:
        """
        Read the users being followed for the screen_name user (i.e its friends)
        :param screen_name: user to get its friends
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: set of pairs (screen_name, id)
        """

        result = set()  # type: Set[Tuple[str, int]]

        for page in tweepy.Cursor(self.api.friends, screen_name=screen_name, count=500).pages():
            begin = time.time()
            for p in page:
                result.add((p.screen_name, p.id))
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - begin), 0))

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
            logging.error(f'can not extract tweets for {screen_name}: {tpe}')
            # start to follow it trying to unlock if user accepts
            self.follow_user(screen_name)
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

    def follow_user(self, screen_name):
        try:
            if self.live:
                self.api.create_friendship(screen_name)
            logging.debug(f'Now following {screen_name}')

        except tweepy.error.TweepError as tw_error:
            logging.error(f'Can not follow user {screen_name}: {tw_error}')

    # endregion

    # region: main logic

    def update_followers_if_needed(self, needed: bool) -> None:
        """
        Update local list of followers if needed or #localFollowers != #realFollowers
        :param needed: Update the followers local list, no matter if is the same as in real Tweeter
        :return: None
        """
        n_local_followers = self.db.count_followers()
        n_real_followers = self.alt_bot_user.followers_count

        logging.info(f'Locally have {n_local_followers} followers currently they are {n_real_followers}. '
                     f'Needed = {needed}')

        if n_local_followers != n_real_followers or needed:
            local_followers = self.db.get_followers()
            logging.info(f'Updating local followers...')
            # need to update
            real_followers = self.get_followers_from_api(ALT_BOT_NAME)
            new_followers = real_followers - local_followers
            lost_followers = local_followers - real_followers

            logging.info(f'New followers: {"; ".join([f[0] for f in new_followers])}')
            logging.info(f'Lost followers: {"; ".join([f[0] for f in lost_followers])}')
            logging.info(f'New followers: {len(new_followers)} Lost followers: {len(lost_followers)} '
                         f'Win followers: {len(new_followers) - len(lost_followers)}')
            self.db.update_followers(new_followers, lost_followers)

    def update_friends_if_needed(self, needed: bool) -> None:
        """
        Update local list of followers if needed or #localFollowers != #realFollowers
        :param needed: Update the followers local list, no matter if is the same as in real Tweeter
        :return: None
        """
        n_local_friends = self.db.count_friends()
        n_real_friends = self.alt_bot_user.friends_count

        logging.info(f'Locally have {n_local_friends} friends currently they are {n_real_friends}. '
                     f'Needed = {needed}')

        if n_local_friends != n_real_friends or needed:
            local_friends = self.db.get_friends()
            logging.info(f'Updating local followers...')
            # need to update
            real_friends = self.get_friends_from_api(ALT_BOT_NAME)
            new_friends = real_friends - local_friends
            lost_friends = local_friends - real_friends

            logging.info(f'New friends: {"; ".join([f[0] for f in new_friends])}')
            logging.info(f'Lost friends: {"; ".join([f[0] for f in lost_friends])}')
            logging.info(f'New friends: {len(new_friends)} Lost friends: {len(lost_friends)} '
                         f'Win friends: {len(new_friends) - len(lost_friends)}')
            self.db.update_friends(new_friends, lost_friends)

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

        status = self.api.get_status(tweet_id, include_ext_alt_text=True, include_entities=True, tweet_mode="extended")

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
                if self.db.tweet_was_processed(tweet_id):
                    # skip the tweet since it was already processed
                    continue

                logging.info(f'Processing tweet {self.get_tweet_url(screen_name, tweet_id)}')

                alt_texts = self.get_alt_text(tweet_id)

                if alt_texts is None or not alt_texts:
                    # skip since the tweet does not contain images
                    logging.debug(f'This tweet is not interesting for us: '
                                  f'{self.get_tweet_url(screen_name, tweet_id)}')
                    self.db.save_processed_tweet(tweet_id)
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

                self.db.save_processed_tweet(tweet_id)
                self.db.save_processed_tweet_with_with_alt_text_info(screen_name, user_id, tweet_id, len(alt_texts),
                                                                     alt_text_score, follower, not follower)

            except Exception as e:
                logging.error(f'Exception: {e} while processing tweet '
                              f'https://twitter.com/{screen_name}/status/{tweet_id}', exc_info=True)

    def process_followers(self, followers: Set[Tuple[str, int]]) -> None:
        """
        Process each follower account in followers set with self.process_account, as followers
        :param followers: set of followers to be processed
        :return: None
        """

        n_followers = len(followers)

        for i, (follower_screen_name, follower_id) in enumerate(followers):

            logging.info(f'[{i}/{n_followers}] Processing follower @{follower_screen_name}...')

            try:
                self.process_account(follower_screen_name, follower_id, follower=True, n_tweets=LAST_N_TWEETS)
            except Exception as e:
                logging.error(f'Error while processing follower: {follower_screen_name}:\n{e}')
                continue

    def process_friends(self, friends: Set[Tuple[str, int]], followers: Set[Tuple[str, int]]) -> None:
        """
        Process each friend account in friends set with self.process_account, as friends if they are not in
        followers set, otherwise skip their processing
        :param friends: set of friends
        :param followers: set of followers
        :return: None

        """
        followers_ids = {f[1] for f in followers}  # type: Set[int]
        n_friends = len(friends)

        for i, (friend_screen_name, friend_id) in enumerate(friends):

            if friend_id in followers_ids:
                # this friend is also a follower, we can skip it
                continue

            logging.info(f'[{i}/{n_friends}] Processing friend @{friend_screen_name}...')

            try:
                self.process_account(friend_screen_name, friend_id, follower=False, n_tweets=LAST_N_TWEETS)
            except Exception as e:
                logging.error(f'Error while processing follower: {friend_screen_name}:\n{e}')
                continue

    def watch_for_alt_text_usage(self) -> None:
        """
        Process all followers and friends of AltBotUY to check for alt_text usage:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers reply for friends
         - Otherwise ignore it
        :return: None
        """

        self.update_users_if_needed(False)
        followers = self.db.get_followers()
        self.process_followers(followers)
        logging.info(f'{len(followers)} followers were processed')
        friends = self.db.get_friends()
        self.process_friends(friends, followers)
        logging.info(f'{len(friends)} friends were processed')

    def send_message_to_all_followers(self, msg: str) -> None:
        """
        Send a DM to every follower
        :param msg: string message to the followers or path to the file containing the message
        :return: None
        """
        if os.path.isfile(msg):
            logging.info(f'Reading message from file {msg}')
            with open(msg, 'r') as f:
                msg = f.read()
            logging.info(f'Read message: {msg}')

        followers = self.db.get_followers()
        msg_sent = 0

        for follower_screen_name, follower_id in followers:
            if self.direct_message(follower_screen_name, follower_id, msg) == 0:
                msg_sent += 1
            else:
                logging.info(f'Can not write DM to {follower_screen_name}')

        logging.info(f'{msg_sent}/{len(followers)} messages sent')

    def update_users_if_needed(self, needed: bool) -> None:
        """
        Update boh, friends and followers
        :param needed: True to Update the users (followers and friends) local list,
        no matter if is the same as in real Tweeter, otherwise only update when local and twitter number differ
        :return: None
        """
        logging.info('Updating followers if needed')
        self.update_followers_if_needed(needed)
        logging.info('Updating friends if needed')
        self.update_friends_if_needed(needed)

    def main(self, update_users: bool, msg_to_followers: Optional[str], watch_for_alt_text_usage: bool) -> None:
        """
        Main process for the AltBotUY
        :return: None
        """
        if update_users:
            logging.info('Updating users')
            self.update_users_if_needed(True)
        if watch_for_alt_text_usage:
            logging.info('Watching for alt_text usage')
            self.watch_for_alt_text_usage()
        if msg_to_followers:
            logging.info(f'Sending message to all followers: {msg_to_followers}')
            self.send_message_to_all_followers(msg_to_followers)

    # endregion


if __name__ == '__main__':

    logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S'
                        )

    parser = argparse.ArgumentParser(description="This script runs AltBotUY.")
    parser.add_argument("-u", "--update-users", help="Update the local list of followers and friends",
                        action="store_true")
    parser.add_argument("-w", "--watch-alt-texts", help="Run the watch-alt-text use case",
                        action="store_true")
    parser.add_argument("-m", "--message", help="Send given message to followers. Can also be the path to a text file "
                                                "containing the message", default=None, type=str)
    args = parser.parse_args()

    start = time.time()

    bot = AltBot(live=False)

    try:
        logging.debug(f'Running bot with args {args}')
        bot.main(update_users=args.update_users, msg_to_followers=args.message,
                 watch_for_alt_text_usage=args.watch_alt_texts)
    except Exception as e:
        error_msg = f'Unknown error on bot execution with args = {args}: {e}.\n\n'
        logging.critical(error_msg)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.direct_message(MAINTEINER_NAME, MAINTAEINER_ID, f'[{now}] \n {error_msg}')

    took_seconds = time.time() - start

    logging.info(f'Execution ended, took {timedelta(seconds=took_seconds)}.')
