ALT_TEXT_TUTORIAL_URL = 'https://help.twitter.com/es/using-twitter/picture-descriptions'

HELP_ARTICLE_MESSAGE = f'Este artículo podría ayudar: {ALT_TEXT_TUTORIAL_URL}'

# Direct message for followers
AUTO_DM_NO_ALT_TEXT = 'Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir ' \
                         'todas sus imágenes... {}. Este artículo podría ayudar: ' \
                      f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme!'

# Tweet for follower without DMs available
AUTO_REPLY_NO_DM_NO_ALT_TEXT = '☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) ' \
                               'para describir todas sus imágenes... Este artículo podría ayudar: ' \
                               f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme! ' \
                               f'Mandame DM para recordarte por ahí a futuro 😉'

# Reply messages to report use case
SINGLE_USER_REPORT = '@{screen_name}: usó alt_texts en {score:.1f} % de imágenes, {n_images} analizadas'
SINGLE_USER_NO_IMAGES_FOUND_REPORT = '@{screen_name}: no encontré tweets con imágenes.'
HEADER_REPORT = '🔎🗒️ Aquí está tu reporte 🤓👇'  # some emojis not shown in pycharm
FOOTER_REPORT = f'+ info acá https://rola93.github.io/altBotUY/#reportes'

# Reply messages to @AltBotUY mentions use case
SINGLE_USER_NO_ALT_TEXT_QUERY = '☝️ Ese tweet de @{} sería más inclusivo con el uso de textos alternativos (alt_text) ' \
                                f'para describir  todas sus imágenes... {HELP_ARTICLE_MESSAGE}'

SINGLE_USER_WITH_ALT_TEXT_QUERY = '☝️ Ese tweet de @{} contiene textos alternativos (alt_text) para describir ' \
                                  'todas sus imágenes 💪💪💪'

AUTO_REPLY_NO_IMAGES_FOUND = '☝️ Ese tweet de @{} no contiene imágenes...  Por ahora no chequeo otros contenidos ' \
    '(GIFs, videos, links externos) 😅😬.'
