# AltBotUY

[@AltBotUY](https://twitter.com/AltBotUY) es un bot de Twitter para fomentar el uso de textos alternativos (alt_text), 
100% en español.

¿Qué es un texto alternativo? Es un texto breve que describe la imagen para quienes no pueden verla. Twitter permite 
descripciones de hasta 1000 caracteres por imagen, [acá](https://help.twitter.com/es/using-twitter/picture-descriptions)
hay un tutorial que explica cómo hacerlo.

## Estado: tweet fijado

El tweet fijado contiene información importante respecto al funcionamiento del bot:

<!--html_preserve-->
<blockquote class="twitter-tweet" data-lang="es" data-dnt="true" data-theme="dark"><p lang="es" dir="ltr">Momentáneamente fuera de servicio: el acceso automatizado al bot está suspendido porque se supone que viola las reglas de automatización 😭😭😭<br>En cuanto quede resuelto, vuelve la programación habitual. <a href="https://t.co/QTd2QBDcYG">pic.twitter.com/QTd2QBDcYG</a></p>&mdash; AltBotUY (@AltBotUY) <a href="https://twitter.com/AltBotUY/status/1384269443128201218?ref_src=twsrc%5Etfw">19 de abril de 2021</a></blockquote> 
<!--/html_preserve-->

## ¿Por qué son importantes los alt_text?
Básicamente los [alt_text](https://es.wikipedia.org/wiki/Wikipedia:Texto_alternativo_para_las_im%C3%A1genes) son la única forma de acceder a las imágenes para muchas personas, en [este artículo](https://www.lacunavoices.com/explore-world-with-lacuna-voices/being-blind-in-digital-world-social-media-inernet-accessibility)
de [@mili_costabel](https://twitter.com/mili_costabel) lo explica mucho mejor (está en inglés), y en
[este hilo](https://twitter.com/mili_costabel/status/1383129606803369990) (en español) hay un montón de reflexiones 
interesantes al respecto. 


## ¿Cómo funciona AltBotUY?
La versión actual únicamente implementa la detección de twits con imágenes sin textos alternativos entre sus 
seguidores y seguidos (a estos últimos los llamaremos amigos), de la siguiente manera:

* **Amigos**: el bot responde al tweet con un tweet que indica lo siguiente:
       _☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para 
       describir  todas sus imágenes... Este artículo te podría ayudar: 
       https://help.twitter.com/es/using-twitter/picture-descriptions_
* **Seguidores** el bot responde por mensaje directo al seguidor con el siguiente mensaje: 
     _Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para describir todas sus imágenes... http://link-al-tweet. Este artículo podría ayudar: https://help.twitter.com/es/using-twitter/picture-descriptions \n 
      Gracias por seguirme!_
* **Seguidores sin Mensaje Directo**: si el seguidor no tiene los mensajes directos habilitados, el bot responde con un tweet con el
 siguiente texto: 
 _☝️ Este tweet sería más inclusivo con el uso de textos alternativos (alt_text) para 
        describir todas sus imágenes... Este artículo podría ayudar: 
        https://help.twitter.com/es/using-twitter/picture-descriptions \n Gracias por seguirme! Mandame DM para 
        recordarte por ahí a futuro 😉._

Si un usuario es amigo y seguidor, el bot lo trata como seguidor.
        
**IMPORTANTE**: Si en algún momento el bot sigue tu cuenta, es porque el contenido de tu cuenta es relevante.
Por favor, **no lo bloquees**: a futuro se añadirán servicios de descripción automática de imágenes, que si tu cuenta bloquea al bot, otros usuarios no van a poder usar estos servicios de descripción automática de imágenes sobre tus tweets, y se verán 
perjudicados. **Ponte en contacto con [@ro_laguna_](https://twitter.com/ro_laguna_)** para solucionar cualquier inconveniente o para solicitar que el bot deje de seguirte. 

Actualmente sólo se chequean imágenes: los gifs, videos y similares son ignorados.

El bot se ejecuta periódicamente, por lo tanto, entre que el tuit original se postea y AltBotUY lo procesa pueden pasar algunas horas.

## Sobre el proyecto

El proyecto surgió una noche de Netflix mirando una serie algo aburrida, me encontré con 
[este tweet](https://twitter.com/mili_costabel/status/1380992677727117317) con una 
observación bien interesante sobre accesibilidad, alt_text y pandemia. Luego de intercambiar algunas ideas,
 agarré la máquina y me puse a escribir... Veremos a dónde nos lleva...

## ¿Qué esperar en el futuro de AltBotUY?

Lo más próximo es la generación de reportes automáticos sobre el uso de alt_text entre los usuarios (amigos y seguidores).
Aún no está del todo definido, pero la idea es publicar un podio mensual de las cuentas que más lo usan.

Es posible también que incluya algunos tweets manuales con contenido relacionado a los alt_text: reflexiones, ejemplos, 
consejos.

A mediano plazo, la idea es introducir OCR como servicio: un usuario llama al bot respondiendo a un tweet con imágenes, 
y el bot intenta extraer el texto de la imagen (OCR: Optical Character Recognition).

A largo plazo, incluir además un servicio de descripción de imágenes (Image Captioning). Acá el desafío es 
doble: por un lado, conseguir mejor infraestructura, y por otro, es necesario ver qué hay de esto en español. 
Una versión inicial quizá pueda ser con transcripciones en inglés + traducción.


Cada novedad del bot será compartida por mensaje directo a sus seguidores.

## ¿Qué datos almacena AltBotUY?  

Sólo se almacena lo mínimo necesario para el funcionamiento del bot: id de los tweets que fueron procesados 
(para evitar duplicados), qué cuentas sigue el bot y cuáles lo siguen, y para el ranking, se guardan la cantidad de 
imágenes e imágenes con texto alternativo que cada usuario twitea.

A futuro no está descartado publicar un dataset con imágenes y descripciones. En tal caso, al igual que todo el proyecto, 
va a estar enmarcado en [#DatosAbiertos](https://twitter.com/hashtag/DatosAbiertos) y 
[#OpenSource](https://twitter.com/hashtag/OpenSource).

Si querés saber más al respecto, no dudes en escribir!

## Información técnica
La descripción técnica del bot, podés encontrarla [acá](docs/technical-readme.md), está en inglés.
Contiene instruccciones y requerimientos para ejecutar el bot, así como la descripción de su funcionamiento.

# Proyectos relacionados:

[@ImageAltText](https://twitter.com/ImageAltText) y [@get_altText](https://twitter.com/get_altText) son otros bots de 
Twitter que implementan image captioning: vos los arrobas contestando un tweet que tiene una imagen y el bot intenta
describirla. Ambos están en inglés, 
[acá pueden ver un ejemplo](https://twitter.com/ImageAltText/status/1383873803860602891).

[@AltTxtReminder](https://twitter.com/AltTxtReminder) es otro bot que sugiere el uso de alt_text a sus seguidores cuando 
no lo utilizan, mediante mensaje directo.  Hay otro bot similar, [@AltTextCrew](https://twitter.com/AltTextCrew) que retwitea 
contenido que necesita una descripción. Ambos proyectos también están en inglés.
