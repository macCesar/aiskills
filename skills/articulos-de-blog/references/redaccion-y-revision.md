# Redacción y revisión de artículos

## Investigación antes del borrador

1. Identifica las afirmaciones de las que depende el artículo. Revisa especialmente cifras, fechas, citas, comparaciones, resultados de pruebas y afirmaciones sobre lo que una tecnología permite hacer. Distingue los hechos verificables de las opiniones del autor y los ejemplos hipotéticos.
2. Consulta las fuentes que pueden respaldar cada afirmación. Para una API o una función, revisa la documentación oficial y la versión aplicable. Para una cifra, abre el estudio o conjunto de datos original y comprueba la fecha, el alcance y la población. Para un caso del usuario, usa el material que aportó y atribuye los datos cuando corresponda. Busca una fuente independiente si una afirmación es controvertida o si depende solo de la publicidad de quien vende el producto.
3. Lee la fuente y confirma que respalde lo que vas a decir, con sus condiciones y excepciones. Enlaza la página, el documento o la sección consultada cerca de la afirmación. Usa comillas para citas textuales comprobadas y atribúyelas. Conserva los enlaces y su relación con las afirmaciones al traducir el artículo.
4. Ajusta el borrador a lo que encontraste. Si las fuentes discrepan, explica la diferencia relevante. Si no puedes comprobar una cifra, una cita o un resultado, elimínalo o explica el límite cuando de él dependa la conclusión. No inventes datos, fuentes, enlaces, testimonios ni resultados. Si una prueba sirve para ilustrar el artículo y todavía no se ha realizado, descríbela como propuesta. En un ensayo, sustenta los hechos en que se apoya la postura y presenta las interpretaciones como tales.

Por ejemplo, si el artículo compara una web y una app para registrar visitas sin señal, comprueba qué puede guardar cada opción y bajo qué condiciones. Si cuentas lo que sucede en un proyecto concreto al recuperar la conexión, apóyate en la documentación de ese proyecto o en una prueba realizada. Si esos datos faltan, plantea la prueba que el lector puede hacer.

## Del tema al borrador

1. Define quién lee y qué podrá decidir o hacer. Formula un título que prometa ese resultado. Por ejemplo, “¿Mi negocio necesita una app o basta con una página web?” plantea una decisión que el texto puede resolver.
2. Abre con una situación reconocible y responde la pregunta en los primeros párrafos. Para el ejemplo de web o app, presenta a quien abre un catálogo desde WhatsApp y a quien toma fotos y llena reportes sin señal. Explica desde el inicio que la elección depende de qué hará cada persona y en qué condiciones.
3. Usa subtítulos que indiquen qué pregunta resuelve cada sección. “Cuándo basta una página web” y “Qué necesita un equipo que trabaja sin señal” permiten seguir la comparación con solo recorrer los encabezados. Desarrolla una idea por párrafo y abre otro al pasar del problema a una opción.
4. Incorpora los ejemplos que dio el usuario. Describe quién actúa, qué cambia y qué pasa si algo falla. Para la captura duplicada, sigue el mismo pedido desde el mensaje hasta la factura. Presenta los ejemplos inventados como hipotéticos y conserva los detalles verificados de los casos reales.
5. Explica cada término técnico cuando aparece por primera vez y solo hasta donde ayude. Si mencionas una API en un artículo para comerciantes, explica que conecta la tienda con el inventario para enviar el pedido. Incluye código cuando sea parte de lo prometido en el título.
6. Termina con una pregunta, comparación o prueba que el lector pueda aplicar. En el caso de web o app, pídele que haga la tarea desde el celular que usará en el trabajo. Si necesita llenar un reporte sin señal, que compruebe si puede guardarlo y enviarlo al reconectarse.

## Títulos

- Nombra la pregunta, el problema o la decisión que el artículo resuelve. Usa pregunta, guía o comparación según lo que el lector encontrará en el texto.
- Lee el título por separado. Recorta repeticiones y pasa al sumario los detalles que solo sitúan la escena. Conserva lo que permite reconocer el problema. “Cómo dejar de capturar el mismo pedido en WhatsApp, Excel y facturación” justifica su extensión porque las tres herramientas muestran dónde se repite el trabajo. Usa la extensión que pida la promesa del artículo.
- Usa “Probé”, “Medimos” o fórmulas equivalentes solo cuando la prueba se haya realizado y el artículo documente el método y los resultados. Si el artículo orienta al lector, usa un título de guía como “¿Cuándo hace falta revisar los pedidos de WhatsApp capturados con IA?”.
- En cada idioma, escribe un título que se lea con naturalidad y conserve la misma promesa. Si el usuario pide un título para buscadores, prepara una versión descriptiva y concisa para el campo `<title>`. Google puede acortar el texto que muestra según el ancho disponible. [Google Search Central](https://developers.google.com/search/docs/appearance/title-link)

Por ejemplo, “¿Qué pasa con las fotos y los reportes de una app sin conexión?” conserva los dos tipos de contenido y la condición que importa. El sumario puede explicar que el equipo toma fotos y llena reportes durante una visita. En inglés, “What happens to app photos and reports when you go offline?” mantiene la misma pregunta.

## Sumario del artículo

Redacta siempre un sumario para la cabecera del artículo. El título plantea el tema o la pregunta. El sumario precisa qué encontrará el lector, qué podrá decidir o desde qué perspectiva se aborda el tema. La introducción desarrolla la primera situación del cuerpo.

Usa **25 a 45 palabras** como extensión habitual. Una sola oración puede bastar si ya deja claro el enfoque. Usa hasta tres oraciones en un párrafo breve cuando haga falta situar el tema o explicar la comparación. Ajusta la extensión a lo que aporta cada frase y al límite del formato, si existe.

Retoca el sumario cuando el cuerpo esté listo. Añade un detalle que el título no dé por sí solo y comprueba que el artículo desarrolle lo que adelanta. Si el borrador ya trae un sumario útil, consérvalo y revísalo junto con el resto. En una entrega bilingüe, traduce y revisa el sumario en ambos idiomas.

En el archivo Markdown, separa con líneas en blanco el título, la etiqueta del sumario, su párrafo en cursiva y el inicio del cuerpo. Usa `**Summary**` en la versión inglesa. Ejemplo de cabecera en español.

```markdown
# ¿Mi negocio necesita una app o basta con una página web?

**Sumario**

*Un catálogo que tus clientes consultan desde WhatsApp y un reporte que tu equipo llena en una zona sin señal tienen requisitos distintos. Compara ambas tareas para decidir cuándo basta una página web y cuándo conviene una app.*
```

## Complementos de publicación

Guarda un solo archivo por artículo con la sección sugerida del blog, las palabras clave, las etiquetas y el prompt de portada. Usa `<tema>-publicacion.md` si el artículo está en la raíz de la sesión, o `publicacion.md` dentro de la carpeta del tema. Si el usuario eligió otra ubicación, usa la carpeta de entrega del artículo. Mantén el prompt dentro de ese archivo.

En una entrega bilingüe, usa dos secciones en el mismo archivo. En cada una incluye los siguientes elementos en el idioma de esa versión.

- **Sección del blog.** Sugiere una sección principal según la pregunta que responde el artículo. Para Código Móvil, usa una de las cuatro opciones de [Organización del blog](organizacion.md#secciones-propuestas-para-código-móvil). Para otro blog, parte de su organización y señala si la sección es una propuesta. Si el CMS tiene nombres por idioma, usa los que correspondan. Si solo conoces el nombre oficial en un idioma, consérvalo como referencia y marca cualquier traducción como sugerida.
- **Palabras clave (`meta keywords`).** Entrega una sola línea lista para copiar al campo del CMS o al atributo `content`. Separa los términos con coma y espacio. Prefiere una palabra por término y usa hasta dos si forman un nombre o concepto preciso, como `Titanium SDK`. Elige términos relevantes para cada idioma. Evita las consultas completas y los campos de palabra clave principal y variantes. Si el usuario pide datos de volumen de búsqueda, usa cifras respaldadas por datos. Google Search prescinde de este metadato al indexar y posicionar páginas. [Google Search Central](https://developers.google.com/search/docs/crawling-indexing/special-tags)
- **Etiquetas.** Reutiliza las etiquetas cortas del blog que describan el tema y propón otras si hace falta. Escribe cada etiqueta como una sola unidad sin espacios. Si combina varias palabras, únelas con mayúsculas internas para que se lean, como `AudioParaJuegos`, y respeta la escritura oficial de nombres como `TiSynthEngine`. Para las etiquetas visibles del CMS, entrega los nombres sin `#`, separados por comas. Si el canal usa hashtags, escribe `#AudioParaJuegos`.
- **Prompt de portada.** Incluye el texto completo listo para copiar. En dos idiomas, conserva la misma escena y las mismas instrucciones visuales. Si se generó una portada, identifica el bloque que contiene el prompt exacto usado y vincula la imagen correspondiente.

Si el usuario solicita un slug, una descripción para buscadores o un texto alternativo, inclúyelos en el mismo archivo. Si hay una imagen generada, redacta el texto alternativo a partir de lo que se ve en ella.

Ejemplo de los dos campos para un artículo sobre TiSynthEngine.

| Campo | Español | English |
| --- | --- | --- |
| Palabras clave / Keywords | TiSynthEngine, Titanium SDK, audio, síntesis, videojuegos | TiSynthEngine, Titanium SDK, audio, synthesis, games |
| Etiquetas / Tags | TiSynthEngine, Audio, Videojuegos | TiSynthEngine, Audio, Games |

## Imagen editorial

1. Elige una escena que represente la pregunta, el caso o la decisión que desarrolla el artículo. Usa un detalle del texto que permita reconocer el tema. Para el artículo sobre web o app, puedes mostrar a una persona que consulta un catálogo en su teléfono y a un técnico que registra una visita en campo. Ajusta la escena a los ejemplos que realmente quedaron en el artículo.
2. Escribe un prompt que se pueda usar por sí solo en generadores como ChatGPT o Nano Banana. Describe el uso como imagen editorial, el sujeto y la acción, el entorno, el encuadre, el estilo visual, la iluminación y la orientación o proporción. Si el usuario no indica formato, pide una composición horizontal de portada con los elementos importantes alejados de los bordes. Por defecto, evita texto sobreimpreso, marcas de agua y logotipos. Si el artículo alude a un proyecto real, evita presentar una imagen generada como fotografía documental o captura real del proyecto.
3. En Codex, sigue `imagegen` y genera a partir del prompt del idioma original. Usa una portada para ambas versiones, salvo que el usuario pida imágenes distintas o que la imagen incluya texto que deba localizarse. Copia la imagen seleccionada a la carpeta de entrega y conserva la extensión del archivo generado. Usa un nombre como `<tema>-portada.png` en la raíz o `portada.png` en la carpeta del tema. Si ajustas el prompt para generar la versión seleccionada, guarda el texto exacto en los complementos y actualiza la versión traducida si corresponde. Si entregas variantes con prompts distintos, identifica cuál corresponde a cada imagen. Usa nombres alternativos para proteger archivos que ya existan.
4. En la respuesta, comparte los enlaces al artículo, al archivo de publicación y a la imagen cuando exista. Incluye debajo cada prompt completo, en bloques de texto fáciles de copiar. Si hay varios artículos o idiomas, identifica a cuál corresponde cada bloque. El contenido del artículo se entrega en sus archivos.

## Antes de entregar

- **Promesa y apertura.** Comprueba que el título se entienda de un vistazo, que sus detalles ayuden a reconocer el problema y que el artículo cumpla lo que promete. Lee la apertura en voz alta. Si tarda en exponer la situación o en responder la pregunta, acércalas al inicio.
- **Sumario.** Comprueba que aparezca entre el título y la introducción, aporte una idea concreta y coincida con el contenido de la versión final.
- **Recorrido.** Lee solo los subtítulos y comprueba que muestren la secuencia de decisiones o pasos. Cambia encabezados genéricos por el tema concreto que resuelve la sección. Confirma que cada párrafo desarrolla una idea.
- **Contenido.** Revisa que se conserven la postura y los ejemplos del usuario. Comprueba datos, citas y enlaces pertinentes. En una comparación, revisa que cada opción incluya las condiciones que le corresponden. Si un ejemplo depende de una prueba, distingue el método propuesto de los resultados observados.
- **Respaldo factual.** Contrasta las afirmaciones decisivas del título, el sumario y el cuerpo con las fuentes consultadas. Comprueba las citas y que cada enlace lleve a la evidencia correspondiente. Después de la edición final por idioma, vuelve a comprobar cualquier afirmación que haya cambiado.
- **Cierre.** Identifica qué puede hacer el lector al terminar. Una pregunta que le permita revisar su operación aporta más que un resumen de la introducción.
- **Edición.** Comprueba ortografía, gramática y puntuación. Aplica después el flujo de [revisión final obligatoria](../SKILL.md#revisión-final-obligatoria) con Humaniza para español o Humanizer para inglés. En español, comprueba al final que la prosa use comillas dobles tipográficas (`“` y `”`). En una entrega bilingüe, revisa el original antes de traducir y coteja la versión traducida y revisada con el original.
- **Archivos.** Confirma que cada versión solicitada esté completa en su propio `.md`, con la etiqueta del sumario en el idioma correcto y su texto entre asteriscos simples. Sigue las [pautas de entrega](../SKILL.md#entrega-en-archivos) y comparte los enlaces en la conversación.
- **Complementos e imagen.** Verifica que el archivo de publicación incluya la sección sugerida, las palabras clave, las etiquetas y el prompt completo por idioma. Comprueba que las palabras clave estén en una sola lista separada por comas, con un máximo de dos palabras por término, y que cada etiqueta se escriba sin espacios. Coteja los prompts del chat con los del `.md`. Si generaste una imagen, abre el archivo entregado y comprueba que corresponda al artículo y al prompt archivado.
