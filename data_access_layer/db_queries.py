
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

CREATE_INDEX_FOR_HISTORIC_USER = """
CREATE INDEX IF NOT EXISTS processed_tweets_alt_text_info_user_id_index ON processed_tweets_alt_text_info(user_id);
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

CREATE_ALLOWED_TO_DM_TABLE = """
 CREATE TABLE IF NOT EXISTS allowed_to_dm (
                                        user_id INT PRIMARY KEY
                                    );
"""

CREATE_SETTINGS_TABLE = """
 CREATE TABLE IF NOT EXISTS bot_settings (
                                        setting_key TEXT PRIMARY KEY,
                                        setting_value TEXT 
                                    );
"""

SAVE_PROCESSED_TWEET = """
INSERT INTO processed_tweets (tweet_id) 
      VALUES (?);
"""

SAVE_PROCESSED_TWEET_NO_FAIL = """
INSERT OR IGNORE INTO processed_tweets (tweet_id) 
      VALUES (?);
"""

SAVE_TWEET_ALT_TEXT_INFO = """
INSERT INTO processed_tweets_alt_text_info (tweet_id, screen_name, user_id, n_images, 
                                            alt_score, processed_at, friend, follower) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

GET_PROCESSED_TWEETS = "SELECT tweet_id from processed_tweets"

GET_ALT_SCORE_FOR_PROCESSED_TWEET = "SELECT alt_score from processed_tweets_alt_text_info WHERE tweet_id=? "

CHECK_TWEET_PROCESSED = "SELECT EXISTS(SELECT 1 FROM processed_tweets WHERE tweet_id=?);"

CHECK_FOLLOWER = "SELECT EXISTS(SELECT 1 FROM followers WHERE user_id=?);"

CHECK_FRIEND = "SELECT EXISTS(SELECT 1 FROM friends WHERE user_id=?);"

CHECK_ALLOWED_TO_DM = "SELECT EXISTS(SELECT 1 FROM allowed_to_dm WHERE user_id=?);"

GET_FOLLOWERS = "SELECT screen_name, user_id from followers"

GET_FRIENDS = "SELECT screen_name, user_id from friends"

GET_ALLOWED = "SELECT user_id from allowed_to_dm"

REMOVE_FRIEND = "DELETE FROM friends WHERE user_id=?"

REMOVE_ALLOWED_TO_DM = "DELETE FROM allowed_to_dm WHERE user_id=?"

REMOVE_FOLLOWER = "DELETE FROM followers WHERE user_id=?"

ADD_FRIEND = "INSERT INTO friends (screen_name, user_id) VALUES (?,?);"

ADD_FOLLOWER = "INSERT INTO followers (screen_name, user_id) VALUES (?,?);"

ADD_ALLOWED_TO_DM = "INSERT INTO allowed_to_dm (user_id) VALUES (?);"

COUNT_FOLLOWERS = "SELECT Count() FROM followers"

COUNT_FRIENDS = "SELECT Count() FROM friends"

COUNT_ALLOWED_TO_DM = "SELECT Count() FROM allowed_to_dm"

GET_HISTORIC_SCORE_TABLE = "SELECT n_images, alt_score FROM processed_tweets_alt_text_info WHERE user_id=?;"

GET_SETTING = "SELECT setting_value FROM bot_settings WHERE setting_key=?"

UPDATE_SETTING = "UPDATE bot_settings SET setting_value=? WHERE setting_key=?"

ADD_SETTING = "INSERT INTO bot_settings (setting_key, setting_value) VALUES (?,?);"

MOST_RECENT_WITH_IMAGES = """
Select MAX(processed_at) from processed_tweets_alt_text_info
WHERE user_id=?;
"""
