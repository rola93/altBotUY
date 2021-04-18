import logging
import sqlite3
from datetime import datetime
from typing import Set, Tuple

from data_access_layer import db_queries
from settings import DB_FILE


class DBAccess:

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
        self.connection.execute(db_queries.CREATE_FRIENDS_TWEETS_TABLE)
        self.connection.execute(db_queries.CREATE_FOLLOWERS_TABLE)

    def save_processed_tweet_with_with_alt_text_info(self, screen_name: str, user_id: int, tweet_id: str, n_images: int,
                                                     alt_score: float, follower: bool, friend: bool) -> None:
        """
        Stores the data related to processed tweets with images, needed to implement reports on alt_text usage
        :param screen_name: screen_name of user who wrote the tweet
        :param user_id: id of user who wrote the tweet
        :param tweet_id: id of the tweet
        :param n_images: number of images attached to the tweet
        :param alt_score: portion of attached images containing alt_text
        :param follower: True iff the user is a follower of the bot, when tweet is processed
        :param friend: True iff the user is a friend of the bot, when tweet is processed
        :return: None
        """
        processed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #
        self.connection.execute(db_queries.SAVE_TWEET_ALT_TEXT_INFO,
                                (tweet_id, screen_name, user_id, n_images, alt_score,
                                 processed_at, int(friend), int(follower)))
        self.connection.commit()

    def save_processed_tweet(self, tweet_id: str) -> None:
        """
        Stores the id of processed tweet, no matter if contains images or not
        :param tweet_id: id of a processed tweet
        :return: None
        """
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

    def get_friends(self) -> Set[Tuple[str, int]]:
        return {(row[0], row[1]) for row in self.connection.execute(db_queries.GET_FRIENDS)}

    def get_followers(self) -> Set[Tuple[str, int]]:
        return {(row[0], row[1]) for row in self.connection.execute(db_queries.GET_FOLLOWERS)}

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

    def count_followers(self) -> int:
        return self.connection.execute(db_queries.COUNT_FOLLOWERS).fetchone()[0]

    def count_friends(self) -> int:
        return self.connection.execute(db_queries.COUNT_FRIENDS).fetchone()[0]


if __name__ == '__main__':

    db = DBAccess(f'../{DB_FILE}')
    # db.save_processed_tweet('pepe4456')
    # db.save_processed_tweet('pepe5')
    # db.save_processed_tweet('pepe6')
    #
    # db.save_processed_tweet_with_with_alt_text_info('user_claudio123', 0, '00twit156', 3, 0., True, True)
    # db.save_processed_tweet_with_with_alt_text_info('user_claudio123', 0, 'twit256', 4, 0.25, False, False)
    # db.save_processed_tweet_with_with_alt_text_info('user_claudio123', 0, 'twit356', 4, 0.75, False, True)
    # db.save_processed_tweet_with_with_alt_text_info('user_claudio123', 0, 'twit456', 4, 1, True, False)

    # print(db.tweet_was_processed('pepe4'))
    # print('='*10)
    # print(db.tweet_was_processed('este no'))
    #
    # db.update_friends({('hola', 1), ('mundo',3)},  {('inexistente',2)})
    # print(';'.join([str(s) for s in db.get_friends()]))
    # print('='*10)
    # db.update_followers({('sumado',123)}, {('mundo',2)})
    # print(';'.join([f[0] for f in db.get_friends()]))
    # print(';'.join([f[0] for f in db.get_followers()]))

    print(db.count_followers())
    print(db.count_friends())
