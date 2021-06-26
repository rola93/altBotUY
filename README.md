# AltBotUY

[@AltBotUY](https://twitter.com/AltBotUY) es un bot de Twitter para fomentar el uso de textos alternativos (alt_text), 
100% en español.

¿Qué es un texto alternativo? Es un texto breve que describe la imagen para quienes no pueden verla. Twitter permite 
descripciones de hasta 1000 caracteres por imagen, [acá](https://help.twitter.com/es/using-twitter/picture-descriptions)
hay un tutorial que explica cómo hacerlo.

## ¿Por qué son importantes los alt_text?
Básicamente los [alt_text](https://es.wikipedia.org/wiki/Wikipedia:Texto_alternativo_para_las_im%C3%A1genes) son la única forma de acceder a las imágenes para muchas personas, en [este artículo](https://www.lacunavoices.com/explore-world-with-lacuna-voices/being-blind-in-digital-world-social-media-inernet-accessibility)
de [@mili_costabel](https://twitter.com/mili_costabel) lo explica mucho mejor (está en inglés), y en
[este hilo](https://twitter.com/mili_costabel/status/1383129606803369990) (en español) hay un montón de reflexiones 
interesantes al respecto. 

## ¿Cómo funciona AltBotUY?

Actualmente está en función la versión 2 del bot, que implementa algunos cambios en el bot para cumplir las 
políticas de twiter respecto a [mensajes automatizados](https://help.twitter.com/es/rules-and-policies/twitter-automation).
Esto recorta posibilidades al bot: no puede contactar a usuarios que no lo deseen. Por otro lado **empodera a los 
usuarios**, así que recuerden:

![Es un gif con la escena de Spiderman donde el tío Ben le dice "with great power comes great responsabilities"](https://i.pinimg.com/originals/4c/3b/39/4c3b395bb7e3b40b780ac97f287b6ab3.gif)

Su funcionamiento es el siguiente:

* Si lo seguis y autorizas los DMs, el bot te avisa por DM cuando escribas un tweet con imágenes sin alt_text. 
Para autorizarlo, basta dar RT a [este tweet](https://twitter.com/AltBotUY/status/1385971762819706888). 
**En cualquier momento podés dejar de usarlo deshaciendolo o dejando de seguir al bot**. 

* Podés pedir reportes de uso de alt_text para cuentas arbitrarias. Basta publicar un twit mencionando al bot y 
hasta tres cuentas más, [aca tenés un ejemplo](https://twitter.com/ro_laguna_/status/1387866272705261569). 

<img src="https://pbs.twimg.com/media/E0QMRefXMAUySF_?format=jpg&name=large" width="300" alt="Captura de pantalla del tweet anterior que muestra el pedido del reporte, y la respuesta.">

* Podés preguntar si una imagen en particular contiene alt_text. Tenés que mencionar al bot en respuesta a un tweet con 
imágenes (sólo al bot). 
[Acá podés ver un ejemplo](https://twitter.com/ro_laguna_/status/1388105417574727682):

<img src="https://pbs.twimg.com/media/E0QM9hcX0AI9NUx?format=jpg&name=large" width="300" alt="Captura de pantalla del tweet anterior que muestra un Tweet de Montevideo tránsito, un usuario contesta arrobando al bot y luego el bot contesta indicando que no hay alt_texts en las imágenes de ese tweet de Montevideo tránsito">



* Todos los twits que procesa el bot y contienen alt_text se ganan un fav/like ❤️ del bot: no se chequea el contenido ni la calidad.

* **[NUEVO]** Una vez al mes se publica el Top-3 de **seguidores** que publican más imágenes utilizando alt_text. El reporte en la imagen de ejemplo dice:

> 🔎📝 Este es el Top-3 de seguidores que usan alt_texts en el último mes  🤓👇
> 1️⃣ @SarAusten: 75 imágenes (88.2 %)
> 2️⃣ @CICR_es: 25 imágenes (100.0 %)
> 3️⃣ @KimiSurrealist: 23 imágenes (95.8 %)
> +info https://rola93.github.io/altBotUY

<img src="https://github.com/rola93/altBotUY/blob/master/docs/media/followers-report.png?raw=true" width="300" alt="Captura de pantalla de un tweet con el reporte de seguidores descrito.">

* **[NUEVO]** Una vez al mes se publica el Top-3 de **amigos** que publican más imágenes utilizando alt_text. El reporte en la imagen de ejemplo dice:
> 🔎📝 Este es el Top-3 de amigos que usan alt_texts en el último mes 🤓👇
> 1️⃣ @impouruguay: 67 imágenes (77.0 %)
> 2️⃣ @MeteorologiaUy: 38 imágenes (97.4 %)
> 3️⃣ @SarAusten: 17 imágenes (77.3 %)
> +info https://rola93.github.io/altBotUY

<img src="https://github.com/rola93/altBotUY/blob/master/docs/media/friends-report.png?raw=true" width="300" alt="Captura de pantalla de un tweetcon el reporte de amigos descrito.">

* **[NUEVO]** El bot contesta con el alt_text dado por el usuario cuando lo llaman en respuesta a un tweet con imágenes, en forma de hilo, como en [este caso](https://twitter.com/ro_laguna_/status/1400979352871911425).

**MUY IMPORTANTE**: Si en algún momento el bot te sigue, es porque el contenido de tu cuenta es relevante.
Por favor, **no lo bloquees**: a futuro se añadirán servicios de descripción automática de imágenes, 
que si tu cuenta bloquea al bot, otros usuarios no van a poder usar estos servicios de descripción automática de 
imágenes sobre tus tweets, y se verán perjudicados. 
**Ponte en contacto con [@ro_laguna_](https://twitter.com/ro_laguna_)** para solucionar cualquier inconveniente o 
para solicitar que el bot deje de seguirte. 

Actualmente sólo se chequean imágenes: los gifs, videos y similares son ignorados.

El bot se ejecuta periódicamente, por lo tanto, entre que el twit se postea y AltBotUY lo procesa pueden 
pasar algunas horas.

### Otros detalles

Un **seguidor** es cualquier usuario que sigue al bot. Un **amigo** es un usuario seguido por el bot. 
Si un usuario es amigo y seguidor, el bot lo trata como seguidor.

Los amigos del bot todavía son procesados para mejorar los reportes, pero no reciben ninguna respuesta. 
En general son cuentas institucionales o de personas importantes. Si hay alguna cuenta que crees que el bot 
debería seguir, podés sugerirla.

Para pedir un reporte sólo tenés que mencionar hasta tres cuentas deseadas. El bot muestra el porcentaje de imágenes 
que utilizan alt_text para cada cuenta, y la cantidad de imágenes analizadas. Los reportes se basan en todos los tweets 
procesados encualquier forma (amigos, seguidores o mencionados). Los aimigos y seguidores se analizan con 
más frecuencia, de manera que es esperable contar con más imágenes analizadas para ellos.

Si el bot no tiene datos para un usuario, o sus datos tienen más de 3 días, el bot procesa al usuario sin importar si 
es amigo o seguidor (o ninguno de los dos).

Chequear el uso de alt_text en imágenes sin un lector de pantallas puede ser complicado. Arrobar al bot en respuesta a 
una imagen puede servir para usuarios curiosos que quieran chequear si alguna imagen relevante contiene alt_text de 
manera sencila, además contribuye a la visibilidad del bot, y a futuro se va a agregar el OCR/Captioning de esa imagen 
como respuesta.  

## Sobre el proyecto

El proyecto surgió una noche de Netflix mirando una serie algo aburrida, me encontré con 
[este tweet](https://twitter.com/mili_costabel/status/1380992677727117317) con una 
observación bien interesante sobre accesibilidad, alt_text y pandemia. Luego de intercambiar algunas ideas,
 agarré la máquina y me puse a escribir... Veremos a dónde nos lleva...

## Estado: tweet fijado

El [tweet fijado](https://twitter.com/AltBotUY/status/1388263808393678850) contiene información importante respecto al funcionamiento del bot:

<!--html_preserve-->
<blockquote class="twitter-tweet"><p lang="es" dir="ltr">Seguime y autorizá los DMs 📩 para poder avisarte cuando olvides utilizar alt_text en tus imágenes.<br>La autorización es muy sencilla: debes dar RT 🔃 al tweet que cito aquí 👉<a href="https://t.co/QJHsyqC2Ns">https://t.co/QJHsyqC2Ns</a><br>Además...</p>&mdash; AltBotUY (@AltBotUY) <a href="https://twitter.com/AltBotUY/status/1388263808393678850?ref_src=twsrc%5Etfw">April 30, 2021</a></blockquote>
<!--/html_preserve-->

## ¿Qué esperar en el futuro de AltBotUY?

Honestamente, el bloqueo de twitter implicó re-pensar al bot, y mucho trabajo para tenerlo disponible tan pronto
como era posible, así que la siguiente actualización va a demorar.

Lo más próximo es la generación de reportes automáticos sobre el uso de alt_text a partir de los tweets procesados.
Aún no está del todo definido, pero la idea es publicar un podio mensual o semanal de las cuentas que más los usan.

Es posible también que incluya algunos tweets manuales con contenido relacionado a los alt_text: reflexiones, ejemplos, 
consejos.

A mediano plazo, la idea es introducir OCR como servicio: un usuario llama al bot respondiendo a un tweet con imágenes, 
y el bot intenta extraer el texto de la imagen (OCR: Optical Character Recognition).

A largo plazo, incluir además un servicio de descripción de imágenes (Image Captioning). Acá el desafío es 
doble: por un lado, conseguir mejor infraestructura, y por otro, es necesario ver qué hay de esto en español. 
Una versión inicial quizá pueda ser con transcripciones en inglés + traducción.


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
Contiene instruccciones y requerimientos para ejecutar el bot, así como la descripción de su funcionamiento. Bienvenidos esos PRs!

# Proyectos relacionados:

[@TextoAlt](https://twitter.com/TextoAlt) es una cuenta de Twitter en español, manejada por un humano, 
que busca crear historias alternativas a partir de tweets que contengan una imagen no accesible (sin alt_texts). 
Un ejemplo es [esta graciosa historia](https://twitter.com/TextoAlt/status/1408468153533972492) de Fran y Firulais.

[@get_altText](https://twitter.com/get_altText) es un bot que lee los alt_text provistos por los usuarios, en forma de tweets: lo citas en respuesta a una imagen, y si tiene alt_text, responde con él. Esto hace que sea agnóstico respecto al idioma: siempre contesta con el texto dadpo por el usuario.

[@ImageAltText](https://twitter.com/ImageAltText) es otro bots de 
Twitter que implementa image captioning: vos lo arrobas contestando un tweet que tiene una imagen y el bot intenta
describirla. Está en inglés, 
[acá pueden ver un ejemplo](https://twitter.com/ImageAltText/status/1383873803860602891).

[@captionerbot](https://twitter.com/captionerbot) es otro bot para describir imágenes, en inglés. Basta con mencionarlo en respuesta a alguna imagen con la palabra _caption_. Además se le puede sugerir palabras para que use como entrada para generar las descripciones. Está en inglés.

[@AltTxtReminder](https://twitter.com/AltTxtReminder) es otro bot que sugiere el uso de alt_text a sus seguidores cuando 
no lo utilizan, mediante mensaje directo.  Hay otro bot similar, [@AltTextCrew](https://twitter.com/AltTextCrew) que retwitea 
contenido que necesita una descripción. Ambos proyectos también están en inglés.

# AltBotUY en la prensa
* [Ingeniero uruguayo se inspira en Milagros Costabel y diseña solución para ciegos en internet](https://www.elpais.com.uy/vida-actual/ingeniero-uruguayo-inspira-milagros-costable-disena-solucion-ciegos-internet.html), El país, Montevideo, Uruguay, 19/04/2021
* [Rodrigo Laguna, creador de una app para ciegos en internet](https://www.canal10.com.uy/rodrigo-laguna-creador-una-app-ciegos-internet-n746089), La Mañana en casa, Canal 10, Montevideo, Uruguay, 03/05/2021
* [AltBotUY en Objetivo Principal](https://www.youtube.com/watch?v=8UVZrMx2F-0), Objetivo Principal, Emisora Principal 107.9 FM de San José, Uruguay, 04/05/2021

## Otros artículos disponibles
 * [¿Cómo ver el alt-text de una imagen?](docs/mostrar-alt-texts.md)
 * [Technical readme](docs/technical-readme.md)
