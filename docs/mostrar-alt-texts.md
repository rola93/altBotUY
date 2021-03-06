# ¿Cómo saber si una imagen contiene alt_text?

Esta pregunta es muy válida. Si contamos con un lector de pantallas, 
es sencillo: al llegar a la imagen, el lector lo va leer el alt_text.

¿Y si no?

En este breve artículo se presenta una forma alternativa de hacerlo, enfocado en Twitter, aunque sirve para cualquier página.
Quizá pueda parecer engorrosa pero es bastante sencilla.

**NUEVO Ahora podés arrobar a [@AltBotUY](https://twitter.com/AltBotUY) en respuesta a un tweet con imágenes, y en algunos minutos te contestará con la descripción si la tiene.** Por ejemplo, mirá [este caso](https://twitter.com/ro_laguna_/status/1400979122801741824).

Algunos comentarios más antes de empezar: la funcionalidad que se verá no es 
exclusivamente para esto, sino que es una herramienta que utilizan desarrolladores 
web cuando crean un sitio o aplicación web. Por otro lado, esto aplica para 
cuando vemos tweets desde el navegador de la computadora (en el navegador del celular, si funciona, probablemente sea distinto, 
y en la app del cel seguro no funciona).

Cuando subimos una imagen con alt_text, como en [este tweet](https://twitter.com/ro_laguna_/status/1383906634171224072),
Twitter nos muestra abajo, a la izquierda un ícono que dice `alt` indicando que esa imagen tiene un alt_text:
 
![Captura de pantalla de un tweet con una foto de mi perro Latte. Abajo a la izquierda se ve el ícono que dice alt](https://github.com/rola93/altBotUY/blob/master/docs/media/latte_icono_alt_resaltado.png?raw=true)

Sin embargo, esto **sólo lo hace para las imágenes que subimos nosotros**: 
cuando alguien más sube una imagen con alt_text, Twitter no nos informa nada al respecto. La primera vez que lo ví,
pensé que al clickearlo podría ver el alt_text que tenía la imagen, pero esto tampoco ocurre: no hay una forma 
sencilla de hacerlo.

Recientemente [alguien comentó](https://twitter.com/SarAusten/status/1386002316055269384) que utilizando 
[Tweet Deck](https://tweetdeck.twitter.com) se muestran estos alt_text; la verdad 
es que aun no lo he probado, y tampoco es una aplicación que use.

¿Por qué querríamos ver los alt_text? Es una buena forma de mejorar nuestras propias descripciones a partir de leer 
las que generan otros.

Pero primero lo primero: una página web no es más que un montón de instrucciones que recibe tu navegador sobre qué y cómo mostrarte.
Esto lo recibe en un lenguaje llamado HTML, donde todo se organiza en etiquetas.

Para mostrar una imagen, por ejemplo, recibe una etiqueta que le indica que debe mostrar una imagen,
 con determinadas características, entre ellas, el alt_text, como en este ejemplo:
 
```html
<img alt="Mi perro, latte, sentado mirando fijo la cámara. Entre la cámara y él hay un plato de rissoto. La foto es en el living de mi casa" 
draggable="true" src="https://pbs.twimg.com/media/EzSfv0kVEAIxlbi?format=jpg&amp;name=small" 
class="css-9pa8cd">
```
 
Si usamos un lector de pantallas, al llegar a esa característica, el lector la leerá en voz alta; sino, 
el navegador la omite por completo.

Para ver el código crudo que recibe el navegador, y en particular esas etiquetas que contienen el texto buscado, vamos a hacer click derecho 
sobre la imagen y seleccionar la opción  `inspeccionar`. 

![Se muestra la misma captura anterior, en la que hicimos click derecho, y aparecen un montón de opciones.](https://github.com/rola93/altBotUY/blob/master/docs/media/latte_click_derecho.png?raw=true)

Esto abre una pequeña ventana que muestra un montón de información, entre otras cosas, 
el código que se está ejecutandoen el navegador. Generalmente, se resalta de azul/celeste la parte de código que corresponde a la imagen.

Ahí hay que buscar la etiqueta correspondiente a la imagen, comienza donde dice **`<img`** y termina con **`>`**. Dentro de ella, las propiedades tienen la siguiente sintaxis **`nombre_propiedad="valor"`**. En particular, nos interesa la propiedad `alt`, cuyo valor es el alt_text:

![Se muestra la captura anterior, con el panel a la derecha que contiene el códgo utilizado por el navegador, 
y en particular el código correspondiente a la imagen](https://github.com/rola93/altBotUY/blob/master/docs/media/latte_twit_y_herramienta.png?raw=true)


A veces el texto se muestra cortado con puntos suspensivos en medio: en esos casos basta darle doble click al 
texto para que se muestre por completo. En la siguiente imagen puede verse el texto ampliado:

![Se muestra la captura anterior, pero ampliado a la zona en que se lee la propiedad alt de la imagen. Claramente se lee la descripción de la imagen.](https://github.com/rola93/altBotUY/blob/master/docs/media/alt_text.png?raw=true)

Cuando el usuario no incluye un alt_text, twitter lo autocompleta con la palabra "Imagen", como en el siguiente ejemplo 
que tomé de [este tweet](https://twitter.com/portalmvd/status/1386689487221182470):

```html
<img alt="Imagen" draggable="true" 
src="https://pbs.twimg.com/media/Ez6CprMWYAIEcw7?format=jpg&amp;name=small" 
class="css-9pa8cd">
```
Por si se lo preguntan, el tweet contiene una imagen que, en su mitad izquierda muestra al Presidente de Uruguay sentado recibiendo la vacuna, y a la derecha, 
un cartel con la estética institucional de Montevideo Portal, fondo naranja y letras blancas, que dice <<"¡Segunda dosis! Gracias al equipo de vacunadores. 
¡Orgullo nacional!" LUIS LACALLE POU Presidente de la República>>

Si bien este método requiere varios pasos y al principio resulta algo engorroso,
 lo bueno que tiene es que sirve para cualquier página web, acá dejo una captura mostrando cómo hacerlo 
 [en esta noticia de Montevideo Portal](https://www.montevideo.com.uy/Noticias/Colectivo-Ciudad-Abierta-reclama-a-la-IM-que-vuelva-a-peatonalizar-la-rambla-los-domingos-uc784646):
  
![Captura de pantalla del nevegador. A la izquierda se ve la noticia y a la derecha el cuadro de herramientas de inspección](https://github.com/rola93/altBotUY/blob/master/docs/media/ejemplo_montevideo_portal.png?raw=true)

En particular, la etiqueta HTML que contiene el alt_text es la siguiente: 

```html
<img itemprop="image" src="https://imagenes.montevideo.com.uy/imgnoticias/202104/_W933_80/759739.jpg" 
srcset="https://imagenes.montevideo.com.uy/imgnoticias/202104/_W320_80/759739.jpg 1x, https://imagenes.montevideo.com.uy/imgnoticias/202104/_W640_80/759739.jpg 2x" 
alt="En bici o a pata">
```

No le puseron mucho amor a la descripción, la verdad... La cuestión es que los portales de noticias, en general, los llenan 
sólo para cumplir, porque los motores de búsqueda los posicionan mejor.

Volviendo al punto, si ven la etiqueta HTML de Montevideo Portal, es un poco distinta a las de Twitter: el tema es que 
lo básico es poner la fuente de la imagen (source, src), el resto es todo opcional, incluso el orden en que aparecen las propiedades. Directamente, podría 
no tener alt_text.    

Para simplificar este proceso, la próxima versión de AltBotUY incluirá la posibilidad de obtener el `alt_text` de una imagen, si el usuario la incluyó. 
Para ello, se deberá contestar el tweet con imagen de la que deseamos conocer el alt_text incluido por el usuario, mencionando sólo al bot. Luego, el bot contestará con el alt_text si lo contiene, o con un mensaje recordatorio si no lo tiene.

## Bonus track: ejemplos en otros navegadores, Mozilla Firefox en PC y Chrome desde el móvil

El truco que describí hasta acá puede variar un poco de navegador a navegador, e incluso un mismo navegador puede estar configurado 
algo diferente (colores, ubicaciones, contenido), pero en Twitter la propiedad `alt` **siempre está**. Los ejemplos que mostré hasta ahora son tomados 
desde [Brave](http://brave.com) que es el navegador que uso, y es lo mismo para 
[Chrome](https://www.google.com/intl/es/chrome/). Acá les dejo algunas capturas que tomé de lo mismo, con 
[Firefox](https://www.mozilla.org/es-ES/firefox/new/).

![En esta imagen se muestra el menu que se desplega cuando damos click derecho a la imagen desde firefox](https://github.com/rola93/altBotUY/blob/master/docs/media/latte_click_derecho_mozilla.png?raw=true)

Se puede ver de nuevo a la opción Inspeccionar, y lo que se abre es casi lo mismo: cambia un poco la estética, pero en si, el contenido que nos interesa
es el mismo. En este caso, el texto se muestra comprimido con puntos suspensivos en medio. Para ver el texto completo, basta dar doble click al texto.

![Se muestra de fondo el mismo tweet de Latte, y abajo, la herramienta para explorar el código de la página.](https://github.com/rola93/altBotUY/blob/master/docs/media/latte_panel_firefox.png?raw=true)

Una opción alternativa, que acabo de encontrar en FireFox y no sé que tan disponible esté en otros, es la opción 
`Inspeccionar elementos de accesibilidad` cuando hacemos click derecho. En este caso, se despliega un panel similar, pero que muestra todos los textos
alternativos de la página y no sólo el de Latte, e incluso se muestran los textos correspondientes a otros botones o partes de la página.

![Se muestra la captura que contiene la descripción de varias imágenes que figuran en la página, y otros elementos, como la cantidad de seguidores](https://github.com/rola93/altBotUY/blob/master/docs/media/inspeccionar-accesibilidad-firefox.png?raw=true)


Por último, probando con el navegador del celular, Chrome, al dejar presionada una imagen, se despliega un menú que incluye el alt_text de la imagen si lo tiene, como puede verse en la siguiente captura:

![Captura de pantalla en el celular. El primer item del menu desplegado muestra el alt text que corresponde con el de una imagen de Latte, la primera de este artículo.](https://github.com/rola93/altBotUY/blob/master/docs/media/captura_chrome_movil_alt_text.jpeg?raw=true)

Espero que el artículo sea de utilidad, y muchas gracias por llegar hasta acá!


**[Volver a la página principal](/altBotUY)**
