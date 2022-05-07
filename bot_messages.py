import emoji

ALT_TEXT_TUTORIAL_URL = 'https://help.twitter.com/es/using-twitter/picture-descriptions'

HELP_ARTICLE_MESSAGE = f'Este artículo podría ayudar: {ALT_TEXT_TUTORIAL_URL}'

# Direct message for followers
AUTO_DM_NO_ALT_TEXT = 'Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir ' \
                         'todas sus imágenes... {}. Este artículo podría ayudar: ' \
                      f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme!'

# Tweet for follower without DMs available
AUTO_REPLY_NO_DM_NO_ALT_TEXT = emoji.emojize(':point_up: Este tweet sería más inclusivo con el uso de textos '
                                             'alternativos (alt_text) para describir todas sus imágenes... '
                                             'Este artículo podría ayudar: ' 
                                             f'{ALT_TEXT_TUTORIAL_URL}\n Gracias por seguirme! ' 
                                             f'Mandame DM para recordarte por ahí a futuro :smile:',
                                             use_aliases=True)

# Reply messages to report use case
SINGLE_USER_REPORT = '@ {screen_name}: usó alt_texts en {score:.1f} % de imágenes, {n_images} analizadas'
SINGLE_USER_NO_IMAGES_FOUND_REPORT = '@ {screen_name}: no encontré tweets con imágenes.'
HEADER_REPORT = emoji.emojize(':mag_right::memo: Aquí está tu reporte :nerd_face::point_down:', use_aliases=True)
FOOTER_REPORT = f'+info acá https://rola93.github.io/altBotUY'

# Reply messages to @AltBotUY mentions use case
SINGLE_USER_NO_ALT_TEXT_QUERY = emoji.emojize(':point_up:️ Ese tweet de @ {} sería más inclusivo con el uso de textos '
                                              'alternativos (alt_text) para describir  todas sus imágenes... '
                                              f'{HELP_ARTICLE_MESSAGE}', use_aliases=True)

SINGLE_USER_WITH_ALT_TEXT_QUERY = emoji.emojize(':point_up:️ Ese tweet de @ {} contiene textos alternativos '
                                                '(alt_text) para describir todas sus imágenes :muscle::muscle::muscle:',
                                                use_aliases=True)

AUTO_REPLY_NO_IMAGES_FOUND = emoji.emojize(':point_up:️ Ese tweet de @ {} no contiene imágenes...  '
                                           'Por ahora no chequeo otros contenidos (GIFs, videos, links externos) '
                                           ':grin:.', use_aliases=True)

HEADER_ALT_TEXT_USER_PROVIDED = '@ {screen_name} describió así las imágenes:'
FIRST_ALT_TEXT_USER_PROVIDED = '1: {alt_text}'
SECOND_ALT_TEXT_USER_PROVIDED = '2: {alt_text}'
THIRD_ALT_TEXT_USER_PROVIDED = '3: {alt_text}'
FOURTH_ALT_TEXT_USER_PROVIDED = '4: {alt_text}'
ALL_ALT_TEXT_USER_PROVIDED = [FIRST_ALT_TEXT_USER_PROVIDED, SECOND_ALT_TEXT_USER_PROVIDED, THIRD_ALT_TEXT_USER_PROVIDED,
                          FOURTH_ALT_TEXT_USER_PROVIDED]

UNAVAILABLE_TWEET = emoji.emojize('Lamentablemente no puedo acceder al tweet de @ {screen_name}. '
                                   'Puede que lo haya borrado, me haya bloqueado o sean tuits protegidos. '
                                   ':disappointed_relieved:')

# Reply messages to periodic report use case
SINGLE_USER_REPORT_FIRST_PLACE = emoji.emojize(':one: @{screen_name}: {n_alts:d} '
                                               'imágenes ({score:.1f} %)', use_aliases=True)
SINGLE_USER_REPORT_SECOND_PLACE = emoji.emojize(':two: @{screen_name}: {n_alts:d} '
                                                'imágenes ({score:.1f} %)', use_aliases=True)
SINGLE_USER_REPORT_THIRD_PLACE = emoji.emojize(':three: @{screen_name}: {n_alts:d} '
                                               'imágenes ({score:.1f} %)', use_aliases=True)

HEADER_REPORT_PERIODIC_FRIENDS = emoji.emojize(':mag_right::memo: Este es el Top-3 de amigos que usaron alt_texts '
                                               'en el último mes :nerd_face::point_down:', use_aliases=True)

HEADER_REPORT_PERIODIC_FOLLOWERS = emoji.emojize(':mag_right::memo: Este es el Top-3 de seguidores que usaron '
                                                 ' alt_texts en el último mes :nerd_face::point_down:',
                                                 use_aliases=True)

SUMMARY_REPORT = '{n_accounts_some_texts} cuentas han usado algún texto alternativo en ese tiempo,' \
                 ' {n_accounts} analizadas ({portion:4.1f}%)'
FOOTER_REPORT_PERIODIC = f'+info https://rola93.github.io/altBotUY'
