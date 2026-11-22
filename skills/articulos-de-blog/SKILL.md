---
name: articulos-de-blog
description: Úsalo cuando se pida elegir el estilo, organizar secciones, proponer temas o redactar, revisar o traducir artículos para el blog de una empresa tecnológica. Incluye blogs de software, desarrollo web y móvil, e IA, como el de Código Móvil.
---

# Artículos para blogs de empresas tecnológicas

Escribe divulgación tecnológica con un estilo expositivo y práctico. Parte de lo que el lector necesita resolver o entender. Explica qué problema resuelve la tecnología, cómo se usa y cuándo le conviene a alguien sin experiencia en programación. Añade el detalle técnico cuando ayude a entender el problema o cuando el lector lo necesite para implementar la solución.

## Flujo de trabajo

Identifica quién leerá el artículo, qué necesita resolver y qué ejemplos o datos aporta el usuario. Antes de trabajar, abre las referencias que correspondan al encargo.

| Encargo | Referencia |
| --- | --- |
| Elegir el enfoque o redactar un artículo nuevo | [Estilo de redacción](references/estilo.md) |
| Definir la categoría, proponer secciones o clasificar un artículo | [Organización del blog](references/organizacion.md) |
| Proponer títulos, priorizar temas o preparar un calendario | [Ideas por servicio](references/temas.md) |
| Redactar, revisar o preparar la versión final de una traducción | [Redacción y revisión de artículos](references/redaccion-y-revision.md) |

Para Código Móvil, consulta también [la guía original](references/estilo-de-redaccion.md). Ahí están sus categorías, los ejemplos de rondines y de web frente a app, las doce ideas por servicio y el orden inicial sugerido. Para ejemplos de código, consulta sus [tecnologías habituales](references/estilo-de-redaccion.md#tecnologías-para-los-ejemplos-de-código-móvil). Adapta los criterios a los lectores y servicios de cada empresa.

## Investigación y verificación

Antes de redactar un artículo, identifica sus afirmaciones verificables e investiga las que sostienen la explicación o la recomendación. Consulta fuentes pertinentes y cita los enlaces directos en el Markdown, cerca de las afirmaciones que respaldan. En una revisión, contrasta también las afirmaciones del borrador recibido. Si falta evidencia, omite el dato prescindible, acota la afirmación a lo que puedas sostener o señala qué quedó sin verificar cuando afecte la conclusión. Sigue el [flujo de investigación](references/redaccion-y-revision.md#investigación-antes-del-borrador).

## Estructura del artículo

Escribe cada artículo en Markdown, con el título como encabezado `#`. El título debe permitir que el lector reconozca su pregunta de un vistazo. Conserva los detalles que cambien la promesa y lleva el contexto adicional al sumario. Sigue los [criterios para títulos](references/redaccion-y-revision.md#títulos).

Debajo del título, coloca la etiqueta `**Sumario**` en español o `**Summary**` en inglés y el texto del sumario en su propio párrafo, entre asteriscos simples (`*texto*`). Después empieza el cuerpo. Sigue las pautas de [redacción del sumario](references/redaccion-y-revision.md#sumario-del-artículo).

## Entrega en archivos

Cuando el encargo incluya un artículo completo, guárdalo en un archivo `.md` por cada idioma. Usa la ubicación indicada por el usuario. Por defecto, guarda un solo artículo en un solo idioma en la raíz de la carpeta de trabajo de la sesión, con un nombre descriptivo como `web-o-app.md`. Cuando haya varios artículos o idiomas, usa `articulos/<tema>/` dentro de esa raíz, con un archivo `es.md` o `en.md` por versión. Por ejemplo, `articulos/web-o-app/es.md` y `articulos/web-o-app/en.md`.

Si el usuario pide revisar un archivo concreto, respeta la ubicación solicitada para esa revisión. Usa nombres distintos cuando guardes una traducción o un artículo nuevo y ya exista un archivo en la ruta elegida. Comprueba que los archivos guardados contengan el título, el sumario en cursiva y el cuerpo completo. En el chat, comparte los enlaces a los archivos, el prompt visual completo y cualquier nota de revisión necesaria. Mantén el texto del artículo en el archivo.

## Imagen editorial

En una revisión, conserva los complementos de publicación y la portada que sigan representando el tema y la escena del artículo. Actualiza los elementos afectados por el nuevo enfoque.

Cuando prepares un artículo completo para publicar, escribe un prompt detallado a partir del texto final. Inclúyelo, junto con la sección sugerida del blog, una lista de palabras clave para `meta keywords` y las etiquetas visibles del artículo, en un solo archivo Markdown de publicación por artículo. Separa las palabras clave con comas, usa una palabra por término de preferencia y un máximo de dos. Escribe las etiquetas sin espacios y añade `#` solo si el canal usa hashtags. Cuando haya dos idiomas, incluye un bloque por idioma en ese mismo archivo y muestra ambos prompts completos en el chat. Consulta los [complementos de publicación](references/redaccion-y-revision.md#complementos-de-publicación).

Cuando corresponda generar una portada en Codex, abre la skill `imagegen` y úsala. Por defecto, usa el prompt en el idioma original y una sola portada para ambas versiones. Identifica en el archivo de publicación el prompt exacto usado. Guarda la imagen junto al artículo y al archivo de publicación, comprueba que abra y agrega su enlace a la entrega. Si la generación falla o la herramienta no está disponible, entrega el artículo y el archivo de publicación e indica el estado de la imagen. En otros entornos, entrega los prompts listos para usar. Sigue las [pautas de imagen editorial](references/redaccion-y-revision.md#imagen-editorial).

## Idioma y traducción

- Redacta en español de México por defecto. Cuando se pida un artículo en inglés, redacta directamente en inglés. Si se pide un solo idioma, entrega únicamente esa versión.
- En los artículos en español, usa comillas dobles tipográficas (`“` y `”`) en la prosa, incluidas las citas. Sustituye por ellas las comillas angulares de los borradores. Conserva los caracteres literales dentro del código y el texto exacto de las citas.
- Cuando se pidan las dos versiones, redacta primero en el idioma de origen indicado. Si no se indica, usa español de México para un artículo nuevo. Revisa y cierra esa versión antes de traducirla. Entrega primero el original revisado y después su traducción al otro idioma.
- Traduce el título, el sumario y el cuerpo a partir de la versión revisada. Conserva la estructura, la voz, los ejemplos, los datos, los matices y las referencias. Escribe con naturalidad en el idioma de destino y mantén los nombres propios, el código y los destinos de los enlaces.

## Revisión final obligatoria

Abre la skill que corresponda y sigue su procedimiento para el título, el sumario y el cuerpo de cada versión que vayas a entregar, incluso si el usuario ya proporcionó el borrador. Usa los nombres registrados en la sesión y sus alias sin depender de rutas de instalación fijas.

| Idioma del artículo | Skill de revisión |
| --- | --- |
| Español | `$aiskills:humaniza`. Ejecuta el escáner de patrones y completa la revisión visual que pide la skill. |
| Inglés | `$humanizer:humanizer`. Usa su modo integrado para entregar el artículo final. |

En una entrega bilingüe, compara la traducción ya revisada con el original revisado. Corrige cualquier cambio de sentido u omisión y vuelve a pasar la revisión del idioma en la versión que hayas corregido. Entrega las versiones finales y conserva las notas de revisión que la skill aplicable requiera. Si falta una skill o no puedes completar su procedimiento, indica qué revisión quedó pendiente.

Antes de entregar el Markdown en español, revisa las comillas de la prosa después de aplicar Humaniza y de cualquier ajuste posterior.

## Datos y pruebas

La guía conserva cifras y enlaces del momento en que se escribió. Comprueba la fuente y su vigencia antes de reutilizarlos como datos actuales. Si propones un artículo sobre una prueba, presenta el método como propuesta hasta que se ejecute. Para un artículo sobre IA aplicada a pedidos, documenta los ejemplos, los errores y los aciertos de la prueba. Para uno sobre resultados de Google, documenta las búsquedas y las fuentes observadas.
