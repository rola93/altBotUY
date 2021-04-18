
CREATE_PROCESSED_TWEETS_TABLE = """
 CREATE TABLE IF NOT EXISTS processed_tweets (
                                        tweet_id TEXT PRIMARY KEY
                                    );
"""

CREATE_PROCESSED_TWEETS_ALT_TEXT_INFO_TABLE = """
 CREATE TABLE IF NOT EXISTS processed_tweets_alt_text_info (
                                        tweet_id TEXT PRIMARY KEY,
                                        screen_name TEXT, 
                                        user_id INTEGER,
                                        n_images INTEGER,
                                        alt_score REAL,
                                        processed_at TEXT,
                                        friend INTEGER,
                                        follower INTEGER 
                                    );
"""

CREATE_FOLLOWERS_TABLE = """
 CREATE TABLE IF NOT EXISTS followers (
                                        screen_name TEXT,
                                        user_id INT PRIMARY KEY
                                    );
"""

CREATE_FRIENDS_TWEETS_TABLE = """
 CREATE TABLE IF NOT EXISTS friends (
                                        screen_name TEXT,
                                        user_id INT PRIMARY KEY
                                    );
"""

SAVE_PROCESSED_TWEET = """
INSERT INTO processed_tweets (tweet_id) 
      VALUES (?);
"""

SAVE_TWEET_ALT_TEXT_INFO = """
INSERT INTO processed_tweets_alt_text_info (tweet_id, screen_name, user_id, n_images, 
                                            alt_score, processed_at, friend, follower) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

GET_PROCESSED_TWEETS = "SELECT tweet_id from processed_tweets"

CHECK_TWEET_PROCESSED = "SELECT EXISTS(SELECT 1 FROM processed_tweets WHERE tweet_id=?);"

GET_FOLLOWERS = "SELECT screen_name, user_id from followers"

GET_FRIENDS = "SELECT screen_name, user_id from friends"

REMOVE_FRIEND = "DELETE FROM friends WHERE user_id=?"

REMOVE_FOLLOWER = "DELETE FROM followers WHERE user_id=?"

ADD_FRIEND = "INSERT INTO friends (screen_name, user_id) VALUES (?,?);"

ADD_FOLLOWER = "INSERT INTO followers (screen_name, user_id) VALUES (?,?);"

COUNT_FOLLOWERS = "SELECT Count() FROM followers"

COUNT_FRIENDS = "SELECT Count() FROM friends"

