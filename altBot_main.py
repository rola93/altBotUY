import argparse
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Optional, Set, Union, Tuple

import tweepy

from bot_messages import AUTO_DM_NO_ALT_TEXT, AUTO_REPLY_NO_DM_NO_ALT_TEXT, \
    SINGLE_USER_NO_IMAGES_FOUND_REPORT, SINGLE_USER_REPORT, AUTO_REPLY_NO_IMAGES_FOUND, SINGLE_USER_WITH_ALT_TEXT_QUERY,\
    HEADER_REPORT, FOOTER_REPORT, SINGLE_USER_NO_ALT_TEXT_QUERY
from data_access_layer.data_access import DBAccess

try:
    from settings_prod import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET
except Exception as e:
    print('settings_prod not found; running just with settings')
    from settings import CONSUMER_KEY, CONSUMER_SECRET, KEY, SECRET

from settings import ACCEPT_DM_TWEET_ID, LOG_LEVEL, LOG_FILENAME, LAST_N_TWEETS, DB_FILE, ALT_BOT_NAME, \
    MAX_RECONNECTION_ATTEMPTS, MAX_MENTIONS_TO_PROCESS, MAINTEINER_NAME, MAINTAEINER_ID, LAST_N_MENTIONS,\
    MAX_DAYS_TO_REFRESH_TWEETS


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

        self.db = DBAccess(DB_FILE)

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

    def get_retweeters(self, tweet_id: int, kindly_sleep: float = 15) -> Set[int]:
        """
        get the list of user_ids who have retweeted the tweet with id=tweet_it
        :param tweet_id: id of thetweet to get its retweeters
        :param kindly_sleep: time to sleep to prevent overloading the API, 15 requests in 15 minutes
        :return: set of user ids who retweeted the tweet
        """
        result = set()  # type: Set[int]

        logging.info(f'Reading users who RTed this tweet: {tweet_id}')

        for page in tweepy.Cursor(self.api.retweeters, id=tweet_id, count=500).pages():
            begin = time.time()
            for p in page:
                result.add(p)
            # go to sleep some time to avoid being banned
            time.sleep(max(kindly_sleep - (time.time() - begin), 0))

        logging.info(f'{len(result)} RTed this tweet: {tweet_id}')

        return result

    def get_tweet(self, tweet_id: str):
        """
        Read particular tweet from the API
        :param tweet_id: id of the twet to be read from the API
        :return: tweet, as tweepy object
        """
        status = self.api.get_status(tweet_id, include_ext_alt_text=True, include_entities=True, tweet_mode="extended")
        return status

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

    def get_allowed_to_dm_from_api(self) -> Set[int]:
        """
        Read the followers list for the screen_name user
        :param screen_name: user to get its followers
        :return: list of (user_id)
        """
        result = self.get_retweeters(ACCEPT_DM_TWEET_ID)

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
            try:
                self.api.create_favorite(tweet_id)
            except tweepy.error.TweepError as tw_error:
                logging.error(f'Can not fav tweet {tweet_id}: {tw_error}')

        logging.debug(f'[live={self.live}] - fav {tweet_id}')

    def reply(self, reply_to: str, msg: str, tweet_id: str) -> None:
        """
        Write a tweet in response to the tweet_id with te message msg
        :param reply_to: string containing the user to reply the tweet
        :param msg: string containing the message to tweet
        :param tweet_id: tweet ID to reply
        :return: None
        """

        msg = f'@{reply_to} {msg}'

        if self.live:
            try:
                status = self.api.update_status(
                    status=msg,
                    in_reply_to_status_id=tweet_id
                )
            except tweepy.error.TweepError as tw_error:
                logging.error(f'Can not send tweet to {reply_to} in reply '
                              f'to {self.get_tweet_url(reply_to, tweet_id)}: {tw_error}')

        logging.debug(f'[live={self.live}] - reply tweet to {tweet_id} in {len(msg)} chars: [{msg}]'.replace("\n", ";"))

    def reply_thread(self, reply_to: str, thread_message: List[str], tweet_id: str) -> None:
        """
        Write a tweet in response to the tweet_id with te message msg;
        :param reply_to: string containing the user to reply the tweet
        :param thread_message: list of messages to tweet as a thread
        :param tweet_id: tweet ID to reply
        :return: None
        """

        for single_message in thread_message:
            msg = f'@{reply_to} {single_message}'

            if self.live:
                try:
                    status = self.api.update_status(
                        status=msg,
                        in_reply_to_status_id=tweet_id
                    )
                    tweet_id = status.id
                except tweepy.error.TweepError as tw_error:
                    logging.error(f'Can not send tweet to {reply_to} in reply '
                                  f'to {self.get_tweet_url(reply_to, tweet_id)}: {tw_error}')
            logging.debug(
                f'[live={self.live}] - reply tweet to {tweet_id} in {len(msg)} chars: [{msg}]'.replace("\n", ";"))

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
            logging.debug(f'[live={self.live}] - send Direct Message to {recipient_id}: [[{msg}]]'.replace("\n", ";"))
            ret = 0

        except tweepy.error.TweepError as tw_error:

            if tw_error.api_code == 349:
                # we do not follow the user or DMs are closed or we're blocked
                logging.info(f'Can not send message to {recipient_name}: {tw_error}')
                ret = 1
            else:
                logging.error(f'Unknown: Can not send message to {recipient_name}: {tw_error}')
                ret = -1

        return ret

    def follow_user(self, screen_name: str) -> None:
        """
        Let the bot follow the user @screen_name
        :param screen_name: name of the user to be followed by the bot
        :return: None
        """
        try:
            if self.live:
                self.api.create_friendship(screen_name)
            logging.debug(f'[live={self.live}] - Now following {screen_name}')

        except tweepy.error.TweepError as tw_error:
            logging.error(f'Can not follow user {screen_name}: {tw_error}')

    def get_mentions(self, since_id) -> List[tweepy.models.Status]:
        """
        Get last mentions to the bot since the mention since_id
        :param since_id: id o the oldest tweet which mention the bot
        :return: List of tweets that mention the bot
        """
        # 75 request/15 min
        mentions = []

        try:
            for page in tweepy.Cursor(self.api.mentions_timeline, since_id=since_id, count=LAST_N_MENTIONS).pages():
                # begin = time.time()
                for p in page:
                    mentions.append(p)
        except tweepy.error.TweepError as tw_error:
            logging.error(f'Can not load mentions: an error occurred: {tw_error}')

        return mentions

    # endregion

    # region: main logic

    @staticmethod
    def split_text_in_tweets(text: str, max_len: int = 250) -> List[str]:
        """
        Split the given string text into a list of strings where each string is shorter than max_len
        :param text: text to be split
        :param max_len: max number of char for each string in result
        :return: list of strings where each of them is shorter than specified
        """
        result = []

        words = text.split(' ')
        n = 0
        j = 0
        for i, word in enumerate(words):
            n += len(word) + 1  # +1 to consider spaces

            if n >= max_len:
                result.append(' '.join(words[j:i]))
                j = i
                n = len(word)

        result.append(' '.join(words[j:]))

        for r in result:
            print(f'{len(r)}/{max_len}: {r}')
            print('='*10)

        assert sum([len(m.replace(' ', '')) for m in result]) == len(text.replace(' ', ''))
        assert all([len(m) <= max_len for m in result])
        return result

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

    def update_allowed_to_dm_if_needed(self, needed: bool) -> None:
        """
        Update local list of followers if needed or #localFollowers != #realFollowers
        :param needed: Update the followers local list, no matter if is the same as in real Tweeter
        :return: None
        """
        n_local_allowed_to_dm = self.db.count_allowed_to_dm()
        n_real_allowed = self.get_tweet(ACCEPT_DM_TWEET_ID).retweet_count

        logging.info(f'Locally have {n_local_allowed_to_dm} allowed_to_dm currently they are {n_real_allowed}. '
                     f'Needed = {needed}')

        if n_local_allowed_to_dm != n_real_allowed or needed:
            local_allowed = self.db.get_allowed_to_dm()
            logging.info(f'Updating local allowed...')
            # need to update
            real_allowed = self.get_allowed_to_dm_from_api()
            new_allowed = real_allowed - local_allowed
            lost_allowed = local_allowed - real_allowed

            logging.info(f'New allowed: {len(new_allowed)} Lost allowed: {len(lost_allowed)} '
                         f'Win allowed: {len(new_allowed) - len(lost_allowed)}')
            self.db.update_allowed_to_dm(new_allowed, lost_allowed)

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
            logging.info(f'Updating local friends...')
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

        tweet = self.get_tweet(tweet_id)

        if hasattr(tweet, 'extended_entities'):
            if len(tweet.extended_entities['media']) > 0:
                result = [media['ext_alt_text'] for media in tweet.extended_entities['media'] if
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

    def process_account(self, screen_name: str, user_id: int, follower: bool, allowed_to_be_dmed: bool,
                        n_tweets: int) -> None:
        """
        Process an account checking its last n_tweets:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers who allowed_to_be_DMed or ignore
         - Otherwise ignore it
        :param screen_name: account to be processed
        :param user_id: user_id to be processed, only used to send DMs (followers)
        :param follower: whether or not the screen_name account is a follower
        :param allowed_to_be_dmed: whether or not the bot is allowed to contact the user via DM
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
                    if follower and allowed_to_be_dmed:
                        # if it is a follower who allowed to be DMed by the bot, write a DM
                        logging.debug(f'Some images ({alt_text_score*100} %) in tweet does not contain alt texts: '
                                      f'{self.get_tweet_url(screen_name, tweet_id)} | '
                                      f'DM the user, this is a follower')
                        self.direct_message(screen_name, user_id, AUTO_DM_NO_ALT_TEXT.format(
                            self.get_tweet_url(screen_name, tweet_id)))
                    else:
                        # if it is not a follower or is not allowed to be DMed by the bot, just log it
                        logging.debug(f'Some images ({alt_text_score*100} %) in tweet does not contain alt texts: '
                                      f'{self.get_tweet_url(screen_name, tweet_id)} | '
                                      f'IGNORED: follower: {follower} allowed_to_be_DMed: {allowed_to_be_dmed}')

                self.db.save_processed_tweet(tweet_id)
                self.db.save_processed_tweet_with_with_alt_text_info(screen_name, user_id, tweet_id, len(alt_texts),
                                                                     alt_text_score)

            except Exception as e:
                logging.error(f'Exception: {e} while processing tweet '
                              f'https://twitter.com/{screen_name}/status/{tweet_id}', exc_info=True)

    def process_followers(self, followers: Set[Tuple[str, int]], users_accepted: Set[int]) -> None:
        """
        Process each follower account in followers set with self.process_account, as followers
        :param followers: set of followers to be processed
        :param users_accepted: set of user ids who accepted to receive DMs
        :return: None
        """

        n_followers = len(followers)

        for i, (follower_screen_name, follower_id) in enumerate(followers):

            logging.info(f'[{i}/{n_followers}] Processing follower @{follower_screen_name}...')

            try:
                self.process_account(follower_screen_name, follower_id, follower=True, n_tweets=LAST_N_TWEETS,
                                     allowed_to_be_dmed=follower_id in users_accepted)
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
                self.process_account(friend_screen_name, friend_id, follower=False, n_tweets=LAST_N_TWEETS,
                                     allowed_to_be_dmed=False)
            except Exception as e:
                logging.error(f'Error while processing follower: {friend_screen_name}:\n{e}')
                continue

    def process_tweets_in_reply_to_other_tweet(self, mentions: List[tweepy.models.Status]):

        for mention in mentions:
            # need to check that only the bot is mention here; otherwise ignore it
            if self.check_text_only_mention_bot(mention.text, self.alt_bot_user.screen_name):
                logging.debug('Processing mention since only the bot was named')
                self.process_mention_in_reply_to_tweet(mention)
            else:
                logging.debug(f'skipping mention since not only the bot was named: {mention.text}')
                logging.debug(self.get_tweet_url(mention.author.screen_name, mention.id))

    def process_mention_in_reply_to_tweet(self, tweet) -> None:
        """
        mention is a tweet which mentioned AltBotUY in reply to another tweet; need to get this another tweet and
        check to see if there are images in it, with or without alt_text.
        :param tweet:
        :return None:
        """
        tweet_to_process_screen_name = tweet.in_reply_to_screen_name  # type: str
        tweet_to_process_user_id = tweet.in_reply_to_user_id  # type: int
        tweet_to_process_tweet_id = tweet.in_reply_to_status_id  # type: int
        tweet_to_process_url = self.get_tweet_url(tweet_to_process_screen_name, str(tweet_to_process_tweet_id))

        tweet_to_reply_screen_name = tweet.author.screen_name  # str
        tweet_to_reply_id = tweet.id_str  # type: str

        if self.db.tweet_was_processed(str(tweet_to_process_tweet_id)):
            logging.debug(f'This twit was already processed: {tweet_to_process_url} ; lets check on DB')
            # we already procesed this tweet; take results from DB
            alt_text_score = self.db.get_alt_score_from_tweet(str(tweet_to_process_tweet_id))
            if alt_text_score is None:
                # the tweet does not contain an image
                logging.debug(f'Tweet being reply was already processed and does not contain images')
                self.reply(tweet_to_reply_screen_name,
                           AUTO_REPLY_NO_IMAGES_FOUND.format(tweet_to_process_screen_name), tweet_to_reply_id)
            elif alt_text_score < 1:
                logging.debug(f'Tweet being reply was already processed and NOT all images contain alt_text')
                self.reply(tweet_to_reply_screen_name,
                           SINGLE_USER_NO_ALT_TEXT_QUERY.format(tweet_to_process_screen_name), tweet_to_reply_id)
            else:
                logging.debug(f'Tweet being reply was already processed and ALL images contain alt_text')
                self.reply(tweet_to_reply_screen_name,
                           SINGLE_USER_WITH_ALT_TEXT_QUERY.format(tweet_to_process_screen_name), tweet_to_reply_id)
        else:
            # tweet is not in our DB; we need to get it from the API and process accordingly
            alt_texts = self.get_alt_text(str(tweet_to_process_tweet_id))

            if alt_texts is None or not alt_texts:
                # skip since the tweet does not contain images
                logging.debug(f'This tweet is not interesting for us: {tweet_to_process_url}')
                self.db.save_processed_tweet(str(tweet_to_process_tweet_id))
                self.reply(tweet_to_reply_screen_name,
                           AUTO_REPLY_NO_IMAGES_FOUND.format(tweet_to_process_screen_name), tweet_to_reply_id)
            else:

                alt_text_score = self.compute_alt_text_score(alt_texts)

                if alt_text_score == 1:
                    # all of the images contains alt_text, let's like it
                    logging.debug(f'All images in tweet contain alt texts: {tweet_to_process_url}')
                    self.fav_tweet(str(tweet_to_process_tweet_id))
                    self.reply(tweet_to_reply_screen_name,
                               SINGLE_USER_WITH_ALT_TEXT_QUERY.format(tweet_to_process_screen_name), tweet_to_reply_id)
                else:
                    # some images with out alt_text; reply the tweet with proper message
                    logging.debug(f'Some images ({alt_text_score * 100} %) in tweet does not contain '
                                  f'alt texts: {tweet_to_process_url}')
                    self.reply(tweet_to_reply_screen_name,
                               SINGLE_USER_NO_ALT_TEXT_QUERY.format(tweet_to_process_screen_name), tweet_to_reply_id)
                    # also reply to the author if needed
                    if self.db.is_allowed_to_dm(tweet_to_process_user_id) and self.db.is_follower(
                            tweet_to_process_user_id):
                        logging.debug(f'the user is a follower with DMs allowed, so, need to write DM to user')
                        self.direct_message(tweet_to_process_screen_name, tweet_to_process_user_id,
                                            AUTO_REPLY_NO_DM_NO_ALT_TEXT.format(tweet_to_process_url))

                # save the processed tweet as processed with images data
                self.db.save_processed_tweet_with_with_alt_text_info(tweet_to_process_screen_name,
                                                                     tweet_to_process_user_id,
                                                                     str(tweet_to_process_tweet_id),
                                                                     len(alt_texts), alt_text_score)

        # save the processed tweet as processed if needed; notice that the tweet may be already processed
        # happens when user A tweets an image,
        # user B (bot's follower or friend) reply A's tweet
        # the watch use case is run; B's reply is processed
        # the mentions use case is run, B's reply must be processed again since
        # now we're checking for A's tweet
        self.db.save_processed_tweet(str(tweet_to_process_tweet_id), do_not_fail=True)

    @staticmethod
    def check_text_only_mention_users(text: str) -> bool:
        """
        Check if text only contain mentions to any user
        :param text: tweet text
        :return: True iff tweet only contains users mentioned
        """
        # remove named users in text
        result = re.sub(r'@[a-z\d_]{1,15}', '', text, flags=re.IGNORECASE)
        # remove empty chars and some punctuation before returning
        result = re.sub(r'[\s.:,;-]*', '', result)
        return len(result) == 0

    @staticmethod
    def check_text_only_mention_bot(text: str, bot_screen_name: str) -> bool:
        """
        Check if text only contain mentions to @bot_screen_name
        :param text: tweet text
        :param bot_screen_name: bot_screen_name
        :return: True iff tweet only contains @bot_screen_name mentioned
        """
        # remove named users in text (all users being reply and the bot)
        result = re.sub(r'^(@[a-z\d_]{1,15} )+' + f'@{bot_screen_name}', '', text, flags=re.IGNORECASE)
        # remove empty chars and some punctuation before returning
        result = re.sub(r'[\s.:,;-]*', '', result)
        return len(result) == 0

    def process_mentioned_users_in_tweet(self, tweet: tweepy.models.Status) -> None:
        """
        tweet is an original tweetwhich mentionthe bot; we need to extract other accounts mentioned in the tweet
        (up to MAX_MENTIONS_TO_PROCESS), process each of those and reply to tweet with a small report on the usage of
        alt_text.
        :param tweet: tweet whose mentions are going to be processed
        :return: None
        """

        report = []
        # get users mentioned filtering out the bot user
        mentions_without_bot = [user_mentioned for user_mentioned in tweet.entities['user_mentions']
                                if user_mentioned['screen_name'].lower() != self.alt_bot_user.screen_name.lower()]

        n = min(MAX_MENTIONS_TO_PROCESS, len(mentions_without_bot))
        tweet_url = self.get_tweet_url(tweet.author.screen_name, tweet.id)

        # check the users mentiioned in the tweet
        for i, user in enumerate(mentions_without_bot, start=1):

            logging.debug(f"[{i}/{n}] processing mentioned user: @{user['screen_name']} ({tweet_url})")

            # need to check if tweets we have are fresh enough
            last_date = self.db.get_last_tweet_with_info_date(user['id'])

            if last_date is None or (datetime.now() - last_date).days > MAX_DAYS_TO_REFRESH_TWEETS:
                # the user is not in our DB or there are no recent tweets from him
                # lets get some of its tweets
                follower = self.db.is_follower(user['id'])
                allowed = self.db.is_allowed_to_dm(user['id'])
                logging.debug(f"Processing @{user['screen_name']} account since most recent tweet is from {last_date}")
                # notice that this line will send the user a DM  if needed
                self.process_account(user['screen_name'], user['id'], follower, allowed, LAST_N_TWEETS)

            score, n_images = self.db.get_percentage_of_alt_text_usage(user['id'])

            logging.debug(f"@{user['screen_name']}: score is {score} in {n_images}")

            if score < 0:
                # score may still be < 0 if the user didn't posted any image recently
                report.append(SINGLE_USER_NO_IMAGES_FOUND_REPORT.format(screen_name=user['screen_name']))
            else:
                report.append(SINGLE_USER_REPORT.format(screen_name=user['screen_name'],
                                                        score=score, n_images=n_images))
            if len(report) == MAX_MENTIONS_TO_PROCESS:
                logging.info(f'[{i}/{n}] Stop processing mentioned users since {MAX_MENTIONS_TO_PROCESS} already processed')
                break

        if len(report) > 0:
            # report can be empty, for instance, if no user is mentioned but the bot
            # reply_to: str, msg: str, tweet_id: str
            logging.debug(f'reply with report for mentioned accounts')
            # add header and footer to report
            report.insert(0, HEADER_REPORT)
            report.append(FOOTER_REPORT)
            # convert report to string
            report = '\n'.join(report)
            self.reply(msg=report, reply_to=tweet.author.screen_name, tweet_id=tweet.id_str)

        # save the processed tweet as processed if needed; notice that the tweet may be already processed
        # happens when user A (bot's follower or friend) tweets mentioning some accounts,
        # the watch use case is run; A's tweet is processed
        # the mentions use case is run, A's tweet mentioning other accounts must be processed again since
        # now we're checking for accounts mentioned in A's tweet
        self.db.save_processed_tweet(str(tweet.id), do_not_fail=True)

    def process_original_tweets_mentioning_bot(self, tweets: List[tweepy.models.Status]):
        """
        process all original tweets that mention the bot: those tweets that only mention the bot and some other accounts
        (i.e. no more text than this) a report is given for the mentioned accounts.
        :param tweets: list of original tweets to be processed
        :return:
        """

        for tweet in tweets:
            if tweet.author.screen_name.lower() == self.alt_bot_user.screen_name.lower():
                logging.debug(f'Skip processing this mention since was written by the bot.')
                continue
            # here we also need to check if no other text than other mention is included and no media contained
            if self.check_text_only_mention_users(tweet.text):
                logging.debug(f'Process mention; Only users are mentioned in this tweet: {tweet.text}')
                self.process_mentioned_users_in_tweet(tweet)
            else:
                logging.debug(f'Skip processing mention: Not only users are mentioned in this tweet: {tweet.text}')
                logging.debug(self.get_tweet_url(tweet.author.screen_name, tweet.id))

    # endregion

    # region: use cases
    def process_mentions(self) -> None:
        """
        process last mentions to the bot
        :return: None
        """
        last_mention_id = self.db.get_last_mention_id()
        mention_tweets = self.get_mentions(last_mention_id)

        tweets_in_reply_to_other_mentioning_bot = []
        original_tweets_mentioning_bot = []
        next_last_mention_id = last_mention_id

        for tweet in mention_tweets:
            if tweet.in_reply_to_status_id is None:
                # this is an original tweet; need to process the mentioned accounts
                original_tweets_mentioning_bot.append(tweet)
            else:
                # this tweet is in reply to some other tweet; need to check this previous tweet
                tweets_in_reply_to_other_mentioning_bot.append(tweet)
            if tweet.id > next_last_mention_id:
                next_last_mention_id = tweet.id

        logging.info(f'[USE CASE] Processing original tweets mentioning the bot')
        self.process_original_tweets_mentioning_bot(original_tweets_mentioning_bot)

        logging.info(f'[USE CASE] Processing tweets that mention the bot AND reply to other tweets')
        self.process_tweets_in_reply_to_other_tweet(tweets_in_reply_to_other_mentioning_bot)

        self.db.update_last_mention_id(next_last_mention_id)

    def watch_for_alt_text_usage_in_followers(self) -> None:
        """
        Process all followers of AltBotUY to check for alt_text usage:
         - If all images in tweet contain alt_text, then it is faved
         - If some images in tweet does not contain alt_text, then DM for followers who accepted to be DMed or ignore
         - Otherwise ignore it
         Processed tweets are saved for reports
        :return: None
        """

        allowed_to_be_dmed = self.db.get_allowed_to_dm()
        followers = self.db.get_followers()
        self.process_followers(followers, allowed_to_be_dmed)
        logging.info(f'{len(followers)} followers were processed, {len(allowed_to_be_dmed)} allowed to DM '
                     f'({len(allowed_to_be_dmed)/len(followers)*100:.2} %)')

    def watch_for_alt_text_usage_in_friends(self) -> None:
        """
        Process all friends of AltBotUY to check for alt_text usage:
         - If all images in tweet contain alt_text, then it is faved
         - Otherwise ignore it.
         Processed tweets are saved for reports
        :return: None
        """

        followers = self.db.get_followers()
        friends = self.db.get_friends()
        self.process_friends(friends, followers)
        logging.info(f'{len(friends)} friends were processed.')

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
        logging.info('Updating allowed_to_dm if needed')
        self.update_allowed_to_dm_if_needed(needed)

    def main(self, update_users: bool, msg_to_followers: Optional[str], watch_for_alt_text_usage_in_friends: bool,
             watch_for_alt_text_usage_in_followers: bool, process_mentions: bool) -> None:
        """
        Main process for the AltBotUY
        :return: None
        """

        logging.info('Updating users')
        self.update_users_if_needed(update_users)

        if watch_for_alt_text_usage_in_followers:
            logging.info('Watching for alt_text usage in followers')
            self.watch_for_alt_text_usage_in_followers()
        if watch_for_alt_text_usage_in_friends:
            logging.info('Watching for alt_text usage in friends')
            self.watch_for_alt_text_usage_in_friends()
        if process_mentions:
            logging.info('Processing bot mentions')
            self.process_mentions()
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
    parser.add_argument("-u", "--update-users", help="Update the local list of followers and friends.",
                        action="store_true")
    parser.add_argument("-wfr", "--watch-alt-texts-friends", help="Run the watch-alt-text use case in friends.",
                        action="store_true")
    parser.add_argument("-wfw", "--watch-alt-texts-followers", help="Run the watch-alt-text use case in followers.",
                        action="store_true")
    parser.add_argument("-m", "--message", help="Send given message to followers. Can also be the path to a text file "
                                                "containing the message.", default=None, type=str)
    parser.add_argument("-l", "--live", help="Actually send DMs, tweets and favs, otherwise just logs it. "
                                             "Must use it for production.",
                        action="store_true")
    parser.add_argument("-p", "--process-mentions", help="Process tweets where the bot is mentioned.",
                        action="store_true")
    args = parser.parse_args()

    start = time.time()

    bot = AltBot(live=args.live)

    try:
        logging.debug(f'Running bot with args {args}')

        bot.main(update_users=args.update_users, msg_to_followers=args.message,
                 watch_for_alt_text_usage_in_friends=args.watch_alt_texts_friends,
                 watch_for_alt_text_usage_in_followers=args.watch_alt_texts_followers,
                 process_mentions=args.process_mentions)

    except Exception as e:
        error_msg = f'Unknown error on bot execution with args = {args}: {e}.\n\n'

        logging.critical(error_msg, exc_info=e)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.direct_message(MAINTEINER_NAME, MAINTAEINER_ID, f'[{now}] \n {error_msg}')

    took_seconds = time.time() - start

    logging.info(f'Execution ended, took {timedelta(seconds=took_seconds)}.')
