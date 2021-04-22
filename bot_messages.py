ALT_TEXT_TUTORIAL_URL = 'https://help.twitter.com/es/using-twitter/picture-descriptions'

HELP_ARTICLE_MESSAGE = f'Este artículo podría ayudar: {ALT_TEXT_TUTORIAL_URL}'

# Tweet message for friends
AUTO_REPLY_NO_ALT_TEXT = '☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para ' \
                         'describir  todas sus imágenes... Este artículo te podría ayudar: ' \
                         f'{ALT_TEXT_TUTORIAL_URL}'
# Direct message for followers
AUTO_DM_NO_ALT_TEXT = 'Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir ' \
                         'todas sus imágenes... {}. Este artículo podría ayudar: ' \
                      f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme!'

# Tweet for follower without DMs available
AUTO_REPLY_NO_DM_NO_ALT_TEXT = '☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) ' \
                               'para describir todas sus imágenes... Este artículo podría ayudar: ' \
                               f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme! ' \
                               f'Mandame DM para recordarte por ahí a futuro 😉'

AUTO_REPLY_NO_IMAGES_FOUND = f'☝️ Ese tweet no contiene imágenes...  Por ahora no chequeo otros contenidos (GIFs, ' \
    f'videos, links externos).'

SINGLE_USER_REPORT = '@{screen_name}: usó alt_texts en el {score:.2f} % de sus imágenes ({n_images} imágenes analizadas)'
SINGLE_USER_NO_IMAGES_FOUND = '@{screen_name}: no encontré tweets con imágenes.'

SINGLE_USER_NO_ALT_TEXT_QUERY = f'☝️ Ese tweet sería más inclusivo con el uso de textos alternativos (alt_text) para ' \
    f'describir  todas sus imágenes... {HELP_ARTICLE_MESSAGE}'

SINGLE_USER_WITH_ALT_TEXT_QUERY = f'☝️ Ese tweet contiene textos alternativos (alt_text) para ' \
    f'describir  todas sus imágenes 💪'
