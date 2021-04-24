import logging
import sqlite3
from datetime import datetime
from typing import Set, Optional, Tuple

import pandas as pd

from data_access_layer import db_queries
from settings import DB_FILE


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

    def create_last_mention_if_needed(self):
        if self. get_last_mention_id() is None:
            self.connection.execute(db_queries.ADD_SETTING, (DBAccess.last_mention_key_setting,
                                                             DBAccess.last_mention_value_setting))
            self.connection.commit()

    def save_processed_tweet_with_with_alt_text_info(self, screen_name: str, user_id: int, tweet_id: str, n_images: int,
                                                     alt_score: float) -> None:
        """
        Stores the data related to processed tweets with images, needed to implement reports on alt_text usage
        :param screen_name: screen_name of user who wrote the tweet
        :param user_id: id of user who wrote the tweet
        :param tweet_id: id of the tweet
        :param n_images: number of images attached to the tweet
        :param alt_score: portion of attached images containing alt_text
        :return: None
        """
        processed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #
        follower = int(self.is_follower(user_id))
        friend = int(self.is_friend(user_id))

        self.connection.execute(db_queries.SAVE_TWEET_ALT_TEXT_INFO,
                                (tweet_id, screen_name, user_id, n_images, alt_score,
                                 processed_at, friend, follower))
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

    def get_alt_score_from_tweet(self, tweet_id: str) -> Optional[float]:
        query_result = self.connection.execute(db_queries.GET_ALT_SCORE_FOR_PROCESSED_TWEET, (tweet_id,)).fetchone()

        result = None if query_result is None else query_result[0]

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

    print(db.count_followers())
    print(db.count_friends())
    print(db.get_percentage_of_alt_text_usage(743235353235042304))
    print(db.get_percentage_of_alt_text_usage(74323535))
    print(db.get_percentage_of_alt_text_usage(226279188))

    print(db.get_alt_score_from_tweet('hola mundo'))

    # print(db.save_processed_tweet('hola'))
    print(db.save_processed_tweet('hola', True))
    # print(db.save_processed_tweet('hola'))

    print(db.get_last_tweet_with_info_date(743235353235042304))
    print(db.get_last_tweet_with_info_date(74323535))
    print(db.get_last_tweet_with_info_date(226279188))
