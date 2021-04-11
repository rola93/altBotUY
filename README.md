# altBot
This is a twitter bot to promote the usage of alt_text to describe images in Twitter.

[Alternative text (alt_text)](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Accessibility/Alternative_text_for_images)
 is text associated with an image that serves the same purpose and conveys the same essential information as 
 the image. In situations where the image is not available to the reader, perhaps because they have turned off 
 images in their web browser or are using a screen reader due to a visual impairment, the alternative text ensures 
 that no information or functionality is lost.

# Logic

The logic goes like follows:

 * Some Twitter accounts are configured to be followed. 
 * Each time a new twit is published, the bot reads it and check for images with alt_text
     * if the tweet doesn't contain images, nothing is done
     * if the tweet contains images with at least one alt_text, then it is faved
     * if the tweet contains images without any alt_text, then the tweet is replied with a standard message: _Buenas! 
     Estaría bueno que usen textos alternativos (alt_text) para describir las imágenes, y así hacerlos accesibles a 
     quienes no pueden verlas... Saludos!_ 
     
`altBot_main.py` module contains all logic to run this, all you need is to implement a main function
to run all this, then its execution must be someway chroned, for instance with chron or chrontab in linux. 
    
# TODO:
 * Improve default message to a more friendly version avoiding the accounts from blocking the bot.
 * Add argparse to give parameters easier
 * Carefully test the alt_text detection logic, since some cases are failing (tweets with images without alt_text are not detected). Also test its logic with other media content (videos, gifs, links)
 * Add tesseract for OCR when alt_image is not provided, and reply with it instead of fixed message.
 * OCR is only useful when images does contain plain text, however, it doesn't apply for general images, so before running OCR, a classiffier is needed to know if OCR worth.
 * Include a real database to account for already processed tweets
 * Add a service to OCR/auto generate caption for images when invoked
 
# Requirements

Requirements can be installed with `pip install -r requirements.txt`, developed under python 3.7.7. 
 
Also need to provide the appropiated credentials to connect with Twitter, defined in `settings.py`. The interaction with twitter is done throgth tweepy API. 
[Here](https://realpython.com/twitter-bot-python-tweepy/#using-tweepy) you can find a complete tutorial on this API.
