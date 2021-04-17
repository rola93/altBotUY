# altBot
[@AltBotUY](https://twitter.com/AltBotUY) is a twitter bot to promote the usage of alt_text to describe images in Twitter.

[Alternative text (alt_text)](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Accessibility/Alternative_text_for_images)
 is text associated with an image that serves the same purpose and conveys the same essential information as 
 the image. In situations where the image is not available to the reader, perhaps because they have turned off 
 images in their web browser or are using a screen reader due to a visual impairment, the alternative text ensures 
 that no information or functionality is lost. 
 
 [Here](https://www.lacunavoices.com/explore-world-with-lacuna-voices/being-blind-in-digital-world-social-media-inernet-accessibility) you can find an article from [@mili_costabel](https://twitter.com/mili_costabel) that perfectly describes how important are those alt_texts. 

# Logic

Currently, the logic goes like follows:

 * Some Twitter accounts are configured to be followed, check in `settings.ACCOUNTS_TO_CHECK`. 
 * Each time a new tweet is published and the bot reads it, checks for images with alt_text
     * if the tweet doesn't contain images, nothing is done
     * if the tweet contains images, and for all of them an alt_text is given, then it is faved
     * if the tweet contains images without any alt_text, then it depends if it is a Follower or a Friend:
     
        * Friends: the tweet is responded with another tweet with the following text:
       _☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para 
       describir  todas sus imágenes... Este artículo te podría ayudar: 
       https://help.twitter.com/es/using-twitter/picture-descriptions_, defined in `bot_messages.AUTO_REPLY_NO_ALT_TEXT`
        * Followers: the tweet is replied with a direct message if possible: 
     _Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir todas sus imágenes...
      <link-to-tweet>. Este artículo podría ayudar: https://help.twitter.com/es/using-twitter/picture-descriptions\n 
      Gracias por seguirme!_, defined in `bot_messages.AUTO_DM_NO_ALT_TEXT`
        * Followers, **without DMs**: the tweet is responded with another tweet since DMs are unavailable, 
        with a different text: _☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para 
        describir todas sus imágenes... Este artículo podría ayudar: 
        https://help.twitter.com/es/using-twitter/picture-descriptions\n Gracias por seguirme! Mandame DM para 
        recordarte por ahí a futuro 😉_, defined in `bot_messages.AUTO_REPLY_NO_DM_NO_ALT_TEXT`.
        
    
A Follower is any user that follows the bot [@AltBotUY](https://twitter.com/AltBotUY), a friend is any user followed 
by the bot. If a user is both friend and follower, it is processed as follower.
                        
     
`altBot_main.py` module contains all logic to run this, all you need is to implement a main function
to run all this, then its execution must be someway chroned, for instance with chron or chrontab in linux. 

You needalso to supply your tweeter credentials in `settings` module, read 
[here](https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials) how
to do it.

# Change log
This section summarizes the differences and improvements from version to version. Notice that not all of them are 
currently in production (prod branch). Some of them are closed issues in master, waiting to be released

## V1.0.
[prod] Initial version: check for some hardcoded accounts only and reply them publicly if alt_text is not used.

## V1.1
[master] Those changes are not in production yet. A database is first needed to make it robust enough.
 *  Usage of alt_text is now checked for both: followers and friends. Friends are reply publicly while for followers a 
 DM is sent if possible, other wise a public tweet inviting them to DM the bot
 * Current version add timestamp to log file
 * Messages are are now defined in `bot_messages.py` module, and include a link to a tutorial on how to add alt_text 
 to images.  
    
# ROAD MAP (prioritized):
 * ~~**IMPROVEMENT**: Read the following list and use this instead of the `settings.ACCOUNTS_TO_CHECK`.~~
 * ~~**IMPROVEMENT**: crontab based local deploy, run it once a day~~
 * **IMPROVEMENT**: Follow back followers whose tweets can't be read.
 * **IMPROVEMENT**: Currently, last `settings.LAST_N_TWEETS` (10) are retrieved from tweeter for the configured accounts, 
  then each of them is checked in our local database to see if it was already processed. This is inefficient. 
  We only need to retrieve new tweets since last download to avoid duplicates.
 * **USE CASE**: Add logs to track alt_text usage and later analise how it evolves
 * **IMPROVEMENT**: Include a real database to account for already processed tweets, dockerized if possible
 * **IMPROVEMENT**: Add DataBase management module
 * **IMPROVEMENT**: Add Tweeter API management module
 * ~~**IMPROVEMENT**: Modify loggs format to include timestamp~~
 * **IMPROVEMENT**: Web page, possibly as [github io page](https://pages.github.com/), in Spanish
 * **IMPROVEMENT**: Tutorial on how to include alt_texts on images. Tweeter thread / page article, spanish
 * **IMPROVEMENT**: Importance of alt_texts on images. Tweeter thread / page article, spanish
 * **IMPROVEMENT**: Add a "terms of use" or privacy section thread/page
 * **IMPROVEMENT**: Add an about the project section thread/page
 * **IMPROVEMENT**: Add argparse to give parameters easier
 * **IMPROVEMENT**: dockerize current solution
 * **IMPROVEMENT**: improve deploy to be available all time, remotely hosted
 * ~~**USE CASE**: Add a service for followers to friendly remind them by DM instead of by public tweets~~
 * **IMPROVEMENT**: Improve the manage of tweeter credentials
 * **COMPLEMENT**: OCR module, based *probably* in tesseract, spanish output
 * **COMPLEMENT**: image captioning module, spanish output. Initially migth be based on Azure: Caption module in 
 English + translate, since spanish model is hard to obtain
 * **USE CASE**: Add a service to OCR/auto generate caption for images when invoked
 * **IMPROVEMENT**: A classifier is needed to know if OCR worth.
 * **USE CASE**: Add tesseract for OCR when alt_image is not provided, and reply with it instead of fixed message.
 * **USE CASE**: Add image captioning when alt_image is not provided, and reply with it instead of fixed message.
 * **USE CASE**: Auto generate monthly report with top 5 alt_text users

Feel free to tackle any of those or even add new ones!
 
 
# Requirements

Requirements can be installed with `pip install -r requirements.txt`, developed under python 3.7.7. 
 
Also need to provide the appropiated credentials to connect with Twitter, defined in `settings.py`. The interaction with twitter is done throgth tweepy API. 
[Here](https://realpython.com/twitter-bot-python-tweepy/#using-tweepy) you can find a complete tutorial on this API.

# Related work:

[@ImageAltText](https://twitter.com/ImageAltText) and [@get_altText](https://twitter.com/get_altText) are both Twitter 
bots for Image captioning: once you call them from a tweet, they answer with their best effort image caption. 
However, both of them only work in English.

[@AltTxtReminder](https://twitter.com/AltTxtReminder) is another bot which just suggest the usage of alt_text when not
 used. They also offer a service for their followers: suggest alt_text usage on DMs. Similarly, 
 [@AltTextCrew](https://twitter.com/AltTextCrew) offer a similar service, which also provides a bot to inspect external 
 links and report the usage of alt_text on those links
