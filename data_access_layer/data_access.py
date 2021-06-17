import logging
import sqlite3
from datetime import datetime
from typing import Set, Optional, Tuple, List, Dict, Union

import pandas as pd

from data_access_layer import db_queries
from settings import DB_FILE, INIT_SYSTEM_DATE


class DBAccess:

    last_mention_key_setting = 'last_mention_id'
    last_mention_value_setting = 1382671652857786368

    def __init__(self, db_file: str = DB_FILE):

        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)

        if self.connection is None:
            raise Exception(f'Cannot connect with database {DB_FILE}')

        self.create_tables()

    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()

    def create_tables(self) -> None:
        """
        This method allows to create tables needed to store processed tweets
        :return: None
        """
        self.connection.execute(db_queries.CREATE_PROCESSED_TWEETS_TABLE)
        self.connection.execute(db_queries.CREATE_PROCESSED_TWEETS_ALT_TEXT_INFO_TABLE)
        self.connection.execute(db_queries.CREATE_INDEX_FOR_HISTORIC_USER)
        self.connection.execute(db_queries.CREATE_FRIENDS_TWEETS_TABLE)
        self.connection.execute(db_queries.CREATE_FOLLOWERS_TABLE)
        self.connection.execute(db_queries.CREATE_ALLOWED_TO_DM_TABLE)
        self.connection.execute(db_queries.CREATE_SETTINGS_TABLE)
        self.create_last_mention_if_needed()
        self.add_alt_text_columns_if_needed()

    def add_alt_text_columns_if_needed(self):
        columns = [row[0].lower() for row in self.connection.execute(db_queries.GET_TABLE_INFO,
                                                             ('processed_tweets_alt_text_info',))]
        if 'user_alt_text_1'not in columns:
            for single_query in db_queries.ALTER_PROCESSED_TWEETS_ALT_TEXT_INFO_TABLE.split(';'):
                self.connection.execute(single_query + ';')
            self.connection.commit()

    def create_last_mention_if_needed(self):
        if self. get_last_mention_id() is None:
            self.connection.execute(db_queries.ADD_SETTING, (DBAccess.last_mention_key_setting,
                                                             DBAccess.last_mention_value_setting))
            self.connection.commit()

    def save_processed_tweet_with_with_alt_text_info(self, screen_name: str, user_id: int, tweet_id: str, n_images: int,
                                                     alt_score: float, user_alt_text_1: Optional[str] = None,
                                                     user_alt_text_2: Optional[str] = None,
                                                     user_alt_text_3: Optional[str] = None,
                                                     user_alt_text_4: Optional[str] = None,
                                                     bot_alt_text_1: Optional[str] = None,
                                                     bot_alt_text_2: Optional[str] = None,
                                                     bot_alt_text_3: Optional[str] = None,
                                                     bot_alt_text_4: Optional[str] = None) -> None:
        """
        Stores the data related to processed tweets with images, needed to implement reports on alt_text usage
        :param screen_name: screen_name of user who wrote the tweet
        :param user_id: id of user who wrote the tweet
        :param tweet_id: id of the tweet
        :param n_images: number of images attached to the tweet
        :param alt_score: portion of attached images containing alt_text
        :param user_alt_text_1: alt text provided by the user in the 1st image of the tweet
        :param user_alt_text_2: alt text provided by the user in the 2nd image of the tweet
        :param user_alt_text_3: alt text provided by the user in the 3rd image of the tweet
        :param user_alt_text_4: alt text provided by the user in the 4th image of the tweet
        :param bot_alt_text_1: alt text figured out by the bot for the 1st image of the tweet
        :param bot_alt_text_2: alt text figured out by the bot for the 2nd image of the tweet
        :param bot_alt_text_3: alt text figured out by the bot for the 3rd image of the tweet
        :param bot_alt_text_4: alt text figured out by the bot for the 4th image of the tweet
        :return: None
        """
        processed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #
        follower = int(self.is_follower(user_id))
        friend = int(self.is_friend(user_id))

        self.connection.execute(db_queries.SAVE_TWEET_ALT_TEXT_INFO,
                                (tweet_id, screen_name, user_id, n_images, alt_score,
                                 processed_at, friend, follower,
                                 user_alt_text_1, user_alt_text_2, user_alt_text_3, user_alt_text_4,
                                 bot_alt_text_1, bot_alt_text_2, bot_alt_text_3, bot_alt_text_4
                                 ))
        self.connection.commit()

    def save_processed_tweet(self, tweet_id: str, do_not_fail: bool = False) -> None:
        """
        Stores the id of processed tweet, no matter if contains images or not
        :param tweet_id: id of a processed tweet
        :param do_not_fail: do not fail if tweet_id already processed
        :return: None
        """
        if do_not_fail:
            # this query ignores the insertion if twet was already in table
            self.connection.execute(db_queries.SAVE_PROCESSED_TWEET_NO_FAIL, (tweet_id,))
        else:
            self.connection.execute(db_queries.SAVE_PROCESSED_TWEET, (tweet_id,))
        self.connection.commit()

    def tweet_was_processed(self, tweet_id: str) -> bool:
        """
        Check whether or not the given tweet was processed
        :param tweet_id: id of the tweet to be checked
        :return: True iff the tweet already exist on db
        """
        res = self.connection.execute(db_queries.CHECK_TWEET_PROCESSED, (tweet_id,)).fetchone()[0]
        return bool(res)

    def is_follower(self, user_id) -> bool:
        res = self.connection.execute(db_queries.CHECK_FOLLOWER, (user_id,)).fetchone()[0]
        return bool(res)

    def is_friend(self, user_id) -> bool:
        res = self.connection.execute(db_queries.CHECK_FRIEND, (user_id,)).fetchone()[0]
        return bool(res)

    def is_allowed_to_dm(self, user_id) -> bool:
        res = self.connection.execute(db_queries.CHECK_ALLOWED_TO_DM, (user_id,)).fetchone()[0]
        return bool(res)

    def get_friends(self) -> Set[Tuple[str, int]]:
        return {(row[0], row[1]) for row in self.connection.execute(db_queries.GET_FRIENDS)}

    def get_followers(self) -> Set[Tuple[str, int]]:
        return {(row[0], row[1]) for row in self.connection.execute(db_queries.GET_FOLLOWERS)}

    def get_allowed_to_dm(self) -> Set[int]:
        return {row[0] for row in self.connection.execute(db_queries.GET_ALLOWED)}

    def update_friends(self, new_friends: Set[Tuple[str, int]], lost_friends: Set[Tuple[str, int]]) -> None:

        for friend_name, friend_id in lost_friends:
            try:
                self.connection.execute(db_queries.REMOVE_FRIEND, (friend_id,))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not remove friend {friend_name}: {ie}')

        for friend_name, friend_id in new_friends:
            try:
                self.connection.execute(db_queries.ADD_FRIEND, (friend_name, friend_id))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not add friend {friend_name}: {ie}')

        self.connection.commit()

    def update_followers(self, new_followers: Set[Tuple[str, int]], followers: Set[Tuple[str, int]]) -> None:

        for follower_name, follower_id in followers:
            try:
                self.connection.execute(db_queries.REMOVE_FOLLOWER, (follower_id,))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not remove follower {follower_name}: {ie}')

        for follower_name, follower_id in new_followers:
            try:
                self.connection.execute(db_queries.ADD_FOLLOWER, (follower_name, follower_id))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not add follower {follower_name}: {ie}')

        self.connection.commit()

    def update_allowed_to_dm(self, new_allowed: Set[int], no_more_allowed_to_dm: Set[int]) -> None:

        for allowed_id in no_more_allowed_to_dm:
            try:
                self.connection.execute(db_queries.REMOVE_ALLOWED_TO_DM, (allowed_id,))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not remove allowed_to_dm {allowed_id}: {ie}')

        for allowed_id in new_allowed:
            try:
                self.connection.execute(db_queries.ADD_ALLOWED_TO_DM, (allowed_id,))
            except sqlite3.IntegrityError as ie:
                logging.error(f'Can not add allowed_to_dm {allowed_id}: {ie}')

        self.connection.commit()

    def count_followers(self) -> int:
        return self.connection.execute(db_queries.COUNT_FOLLOWERS).fetchone()[0]

    def count_friends(self) -> int:
        return self.connection.execute(db_queries.COUNT_FRIENDS).fetchone()[0]

    def count_allowed_to_dm(self) -> int:
        return self.connection.execute(db_queries.COUNT_ALLOWED_TO_DM).fetchone()[0]

    def get_last_tweet_with_info_date(self, user_id: int) -> Optional[datetime]:
        """
        return the datime when the last tweet with info was inserted for the user.
        If no tweets are found for the user, return None
        :param user_id: user to get the last time his tweet was processed
        :return: the datetime when last tweet of the user was processed
        """

        last_update = self.connection.execute(db_queries.MOST_RECENT_WITH_IMAGES, (user_id,)).fetchone()[0]
        ret = last_update if last_update is None else datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')

        return ret

    def get_percentage_of_alt_text_usage(self, user_id: int) -> Tuple[float, int]:
        """
        Compute the % of images from the user that contain alt text with the number of images considered
        :param user_id: id of the user to be queried
        :return: Tuple of float in [0, 100] corresponding to percentage or -1 if user not found;
                int with the number of images analyzed
        """

        df = pd.DataFrame([
            dict(n_images=row[0], alt_score=row[1]) for row in
            self.connection.execute(db_queries.GET_HISTORIC_SCORE_TABLE, (user_id,))])

        if len(df) > 0:
            n_images = df['n_images'].sum()
            fraction = (df['n_images'] * df['alt_score']).sum() / n_images if n_images > 0 else 0
            return fraction * 100, n_images
        else:
            return -1, -1

    def get_top_alt_text_users(self, followers: bool = False, friends: bool = False, start_date: str = INIT_SYSTEM_DATE,
                               top_n: int = 3) -> Tuple[List[Dict[str, Union[int, float, str]]], int, int]:

        # screen_name, user_id, n_images, alt_score, processed_at, friend, follower
        df = pd.DataFrame(
            [dict(screen_name=row[0], user_id=row[1], n_images=row[2], alt_score=row[3], friend=row[4], follower=row[5])
             for row in
             self.connection.execute(db_queries.GET_HISTORIC_INFO_TABLE_FULL, (start_date,))
             if ((row[4] and friends) or (row[5] and followers))])

        if len(df) == 0:
            # if no results were read, return empty list
            return [], -1, -1

        # compute number of images with alt text
        df['alt_text_images'] = df['n_images'] * df['alt_score']

        # group records by user_id, summing records
        df_grouped = df.groupby(['user_id', 'screen_name'])[['alt_text_images', 'n_images']].sum().sort_values(
            ['alt_text_images', 'n_images'], ascending=False)

        n_accounts = len(df_grouped['alt_text_images'].values)
        n_accounts_some_texts = len(df_grouped['alt_text_images'].values.nonzero()[0])
        df_result = df_grouped.head(top_n)

        result = []

        for (user_id, screen_name), row in df_result.iterrows():
            result.append({
                'user_id': user_id,
                'screen_name': screen_name,
                'n_images': row['n_images'],
                'alt_text_images': row['alt_text_images'],
                'portion': row['alt_text_images']/row['n_images']
            })

        return result, n_accounts, n_accounts_some_texts

    def update_user_alt_text_info(self, tweet_id: str, user_alt_text_1: str = None, user_alt_text_2: str = None,
                                  user_alt_text_3: str = None, user_alt_text_4: str = None):

        self.connection.execute(db_queries.UPDATE_USER_ALT_TEXT_INFO,
                                (user_alt_text_1, user_alt_text_2, user_alt_text_3, user_alt_text_4, tweet_id))
        self.connection.commit()

    def update_bot_alt_text_info(self, tweet_id: str, bot_alt_text_1: str = None, bot_alt_text_2: str = None,
                                  bot_alt_text_3: str = None, bot_alt_text_4: str = None):

        self.connection.execute(db_queries.UPDATE_USER_ALT_TEXT_INFO,
                                (bot_alt_text_1, bot_alt_text_2, bot_alt_text_3, bot_alt_text_4, tweet_id))
        self.connection.commit()

    def get_alt_score_from_tweet(self, tweet_id: str) -> Optional[float]:
        query_result = self.connection.execute(db_queries.GET_ALT_SCORE_FOR_PROCESSED_TWEET, (tweet_id,)).fetchone()

        result = None if query_result is None else query_result[0]

        return result

    def get_alt_text_info_from_tweet(self, tweet_id: str) -> Optional[Dict[str, Union[List[Optional[str]], int, float]]]:

        query_result = self.connection.execute(db_queries.GET_ALT_TEXT_INFO_FROM_TWEET, (tweet_id,)).fetchone()

        if query_result is not None:
            result = dict(n_images=int(query_result[0]), alt_score=float(query_result[1]),
                          user_alt_text=[txt for txt in query_result[2:6]],
                          bot_alt_text=[txt for txt in query_result[6:10]])
        else:
            result = None

        return result

    def get_last_mention_id(self) -> Optional[int]:
        query_result = self.connection.execute(db_queries.GET_SETTING, (DBAccess.last_mention_key_setting,)).fetchone()
        result = None if query_result is None else int(query_result[0])
        return result

    def update_last_mention_id(self, last_mention_id: int) -> None:
        self.connection.execute(db_queries.UPDATE_SETTING, (last_mention_id, DBAccess.last_mention_key_setting))
        self.connection.commit()


if __name__ == '__main__':

    db = DBAccess(f'../{DB_FILE}')
    db.add_alt_text_columns_if_needed()
    # print(db.get_alt_text_info_from_tweet('1383088783361458176'))


    print(db.get_top_alt_text_users(start_date='2020-05-01', followers=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-10'))
    # print(db.get_top_alt_text_users(start_date='2021-05-15'))
    # print(db.get_top_alt_text_users(start_date='2021-05-17'))
    #
    # print('FOLLOWERS')
    # print(db.get_top_alt_text_users(start_date='2021-05-19', followers=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-26', followers=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-13', followers=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-10', followers=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-17', followers=True))
    #
    # print('FRIENDS')
    # print(db.get_top_alt_text_users(start_date='2021-04-19', friends=True))
    # print(db.get_top_alt_text_users(start_date='2021-04-26', friends=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-03', friends=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-10', friends=True))
    # print(db.get_top_alt_text_users(start_date='2021-05-17', friends=True))

    # print(db.count_followers())
    # print(db.count_friends())
    # print(db.get_percentage_of_alt_text_usage(743235353235042304))
    # print(db.get_percentage_of_alt_text_usage(74323535))
    # print(db.get_percentage_of_alt_text_usage(226279188))
    #
    # print(db.get_alt_score_from_tweet('hola mundo'))
    #
    # # print(db.save_processed_tweet('hola'))
    # print(db.save_processed_tweet('hola', True))
    # # print(db.save_processed_tweet('hola'))
    #
    # print(db.get_last_tweet_with_info_date(743235353235042304))
    # print(db.get_last_tweet_with_info_date(74323535))
    # print(db.get_last_tweet_with_info_date(226279188))
