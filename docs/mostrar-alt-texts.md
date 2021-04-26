# ¿Cómo saber si una imagen contiene alt_text?

Esta pregunta es muy válida. Si contamos con un lector de pantallas, 
es sencillo: al llegar a la imagen, el lector lo va a leer.

¿Y si no?

En este breve artículo presentamos una forma alternativa de hacerlo, 
quizá pueda sonar engorrosa pero es bastante sencilla.

Algunos comentarios más antes de empezar: la funcionalidad que vamos a ver no es 
exclusivamente para esto, sino que es una herramienta que utilizan desarrolladores 
web cuando crean un sitio o aplicación web. Por otro lado, esto aplica para 
cuando vemos tweets desde el navegador de la computadora (en el navegador del celular puede que sea algo distinto, 
y en la app del cel seguro no funciona).

Cuando subimos una imagen con alt_text, twitter nos muestra abajo de la imagen, a la izquierda un icono que dice `alt`
indicando que esa imagen tiene un alt_text:
 
![Captura de pantalla de un twit con una foto de Latte. Abajo a la izquierda se ve el ícono que dice alt]()

[Acá](https://twitter.com/ro_laguna_/status/1383906634171224072) pueden accederal tweet en cuestión.

Sin embargo, esto **sólo lo hace para las imágenes que subimos nosotros**:
cuando alguien más sube una imagen con alt_text, twittter no nos informa nada al respecto. La primera vezque lo ví
pensé que al clickearlo podría ver el alt_text que tenía la imagen, pero esto tampoco ocurre: no hay una forma 
sencilla de hacerlo.

Recientemente [alguien comentó](https://twitter.com/SarAusten/status/1386002316055269384) que utilizando 
[tweet Deck](https://tweetdeck.twitter.com) estos alt_text; la verdad 
es que aun no lo he probado, y tampoco es una apicación que use.

¿Por qué querríamos ver los alt_text? Es una buena forma de mejorar nuestraspropias descripciones a partir de leer 
las que generan otros.

Primero lo primero: una página web no es más que un montón de instrucciones que recibe tu navegador sobre qué y cómo mostrarte.
Esto lo recibe en un lenguaje llamado html, donde todo se organiza en etiquetas.

Para mostrar una imagen por ejemplo, recibe unaetiqueta que le indica que debe mostrar una imagen,
 con determinadas características, entre ellas, el alt_text, como en este ejemplo:
 
```html
<img alt="Mi perro, latte, sentado mirando fijo la cámara. Entre la cámara y él hay un plato de rissoto. La foto es en el living de mi casa" 
draggable="true" src="https://pbs.twimg.com/media/EzSfv0kVEAIxlbi?format=jpg&amp;name=small" 
class="css-9pa8cd">
```
 
Si usamos un lector de pantallas, al llegar a esa característica, el lector la leerá en voz alta; sino, 
el navegador la omite por completo.

Para ver el código crudo querecibe el navegador, y en particular esas etiquetas quecontienen el texto buscado, vamos a hacer click derecho sobre laimagen y seleccionar la opción 
`inspeccionar`. Esto abre una pequeña ventana que muestra un montón de información, entre otras cosas, el código que
se está ejecutandoen el navegador.

![Se muestra la misma captura anterior, en la que hicimos click derecho, y aparecen un montón de opciones.]()

Generalmente, se resalta de azul/celeste la parte de código que corresponde a la imagen.

Ahí hay que buscar la etiqueta imagen, y dentro de ella, la propiedad alt_text:

![Se muestra la captura anterior, con el panel a la derecha que contiene el códgo utilizado por el navegador, 
y en particular el código correspondiente a la imagen]()


A veces el texto se muestra cortado con puntos suspensivos en medio: en esos casos basta darle doble click al 
texto para que se muestre por completo.

Cuando elusuario no incluye un alt_text, twitter lo autocompleta con la palabra "Imagen", como en el siguiente ejemplo 
que tomé de [este tweet](https://twitter.com/portalmvd/status/1386689487221182470):

```html
<img alt="Imagen" draggable="true" 
src="https://pbs.twimg.com/media/Ez6CprMWYAIEcw7?format=jpg&amp;name=small" 
class="css-9pa8cd">
```

Por último, esto puede variar un poco de navegador a navegador, e incluso un mismo navegador puede estar configurado 
algo diferente (colores, ubicaciones, contenido), pero **siempre está**. Los ejemplos que mostré ahsta ahora son tomados 
desde [Brave](http://brave.com) que es el navegador que uso, y es lo mismo para 
[Chrome](https://www.google.com/intl/es/chrome/). Más abajo dejo algunas capturas que tomé de lo mismo, con 
[Firefox](https://www.mozilla.org/es-ES/firefox/new/).

Si bien este método requiere varios pasos y alprincipio resulta algo engorroso,
 lo bueno que tiene es que sirve para cualquier página web, acá dejo una captura mostrando 
 cómo hacerlo 
 [en esta noticia de Montevideo Portal](https://www.montevideo.com.uy/Noticias/Colectivo-Ciudad-Abierta-reclama-a-la-IM-que-vuelva-a-peatonalizar-la-rambla-los-domingos-uc784646):
 
 
![Captura de pantalla del nevegador. A la izquierda se ve la noticia y a la derecha el cuadro de herramientas de inspección](./docs/media/ejemplo_montevideo_portal.png)

En particular, la etiqueta HTML que contiene el alt_text es la siguiente: 

```html
<img itemprop="image" src="https://imagenes.montevideo.com.uy/imgnoticias/202104/_W933_80/759739.jpg" 
srcset="https://imagenes.montevideo.com.uy/imgnoticias/202104/_W320_80/759739.jpg 1x, https://imagenes.montevideo.com.uy/imgnoticias/202104/_W640_80/759739.jpg 2x" 
alt="En bici o a pata">
```

No le puseron mucho amor a la descripción, la verdad... El tema es que los portales de noticias en general los llenan 
sólo para cumplir, porque los motores de búsqueda los posicionan mejor.

Volviendo al punto, si ven la etiqueta HTML de Montevideo Portal, es un poco distinta a las de twitter: el tema es que 
lo básico es poner la fuente de la imagen (source, src), el resto es todo opcional, incluso el orden. Incluso, podría 
no tener alt_text directamente.    

 

