---
name: humaniza
description: 'Editor de estilo para textos en español (especialmente es-MX): quita los tics de escritura de IA y devuelve prosa natural, concreta y directa, sin cambiar el contenido. Úsalo siempre que alguien quiera revisar, pulir o reescribir un texto en español —emails, documentación, marketing, soporte, posts, textos técnicos— aunque nunca diga "humanizar": "esto suena a ChatGPT", "quítale lo robótico", "hazlo más natural", "que no parezca IA", "sonó muy acartonado", "límale el tono", "revísame este correo antes de mandarlo". También cuando el texto mismo trae las señales: rayas por todas partes, "no es X, sino Y", "cabe destacar", listas de tres, abridores como "la verdad es que". No es para: traducir, corregir solo ortografía o gramática, escribir un texto desde cero, ni editar textos en inglés.'
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
compatibility: Requires Python 3 (standard library only) for the pattern checker.
---

# Humaniza

Editor de estilo para español de México. El objetivo es quitar tics de IA sin cambiar el contenido.

## Alcance

- Mantener significado, datos y estructura general.
- Respetar puntuación y signos de apertura/cierre.
- Conservar registro (tú/usted) salvo solicitud explícita.
- Preferir es-MX: evitar "vosotros", "ordenador", "móvil", "coche" cuando el texto sea neutro.
- No inventar fuentes ni datos.

## Reglas clave (adaptadas de Stop Slop)

1. **Corta los abridores.** Elimina frases que anuncian lo que sigue. "La verdad es que", "Déjame ser claro", "Aquí está la cosa". Di el contenido directo.

2. **Rompe estructuras formulaicas.** Evita contrastes binarios ("No porque X, sino porque Y"), listados negativos ("No es X, no es Y, es Z"), fragmentación dramática ("[Sustantivo]. Eso es todo."), setups retóricos ("¿Qué tal si...?"), agencia falsa ("la decisión emerge").

3. **Usa voz activa.** Cada oración necesita un sujeto humano haciendo algo. No le hables a objetos inanimados como si actuaran solos. Los datos no "dicen" nada; alguien los lee.

4. **Sé concreto.** Sin vaguedades. "Las implicaciones son significativas" → nombra la implicación específica. "Las razones son estructurales" → di cuál es la razón.

5. **Pon al lector en la escena.** "Tú" gana a "la gente". Lo específico gana a lo abstracto. Sin narrador desde la distancia ("La gente tiende a...", "Esto pasa porque...").

6. **Varía el ritmo.** Mezcla largos y cortos. Dos elementos ganan a tres. No termines todos los párrafos igual. Elimina las rayas (—) en prosa narrativa.

7. **Confía en el lector.** Afirma los hechos directo. Sin suavizar, justificar, ni dar permiso ("y eso está bien").

8. **Corta lo citable.** Si suena a frase de caja de motivación, reescríbela.

## Flujo

1. Detectar tono y audiencia a partir del texto.
2. Si el usuario pide un modo (marketing, técnico, soporte, etc.), priorizarlo.
3. Identificar tics de IA con `references/ai-patterns-es.md`, `references/lexicon-es-mx.md`, y `references/structures-es.md`.
4. Reescribir: cortar relleno, concretar, variar ritmo, usar "ser/estar" cuando sea más claro.
5. Ajustar el tono según `references/modes-es-mx.md` si aplica.
6. Añadir voz humana cuando aplique con `references/voice-es-mx.md`.
7. Verificar el resultado con el escáner determinístico — ver "Verificación con script" abajo — y después pasar el QA visual con `references/checklist.md`.

## Verificación rápida (antes de entregar)

- ¿Hay adverbios -mente? Redúcelos o elimínalos.
- ¿Voz pasiva sin sujeto visible? Encuentra al actor, ponlo de sujeto.
- ¿Objeto inanimado haciendo algo humano ("la decisión emerge")? Nombra a la persona.
- ¿Oración empieza con pronombre o adverbio interrogativo (qué, cuándo, dónde, cómo)? Reestructura.
- ¿Abre con "he aquí", "la verdad es", "déjame"? Corta al punto.
- ¿Tres oraciones consecutivas del mismo largo? Rompe una.
- ¿Párrafo termina con frase corta de impacto? Varía.
- ¿Raya (—) en prosa narrativa? Elimínala o usa coma.
- ¿Declaración vaga ("las implicaciones son graves")? Nombra la implicación concreta.
- ¿Comentario meta ("el resto de este artículo...")? Bórralo.
- ¿Falso contraste ("no es X, es Y")? Afirma Y directo.
- ¿Son a cita de LinkedIn? Reescribe sonando a humano.

## Verificación con script

Antes de entregar el texto, ejecuta el escáner para detectar tics que se hayan colado en la reescritura:

```bash
python <SKILL_DIR>/scripts/check_ai_patterns.py texto_editado.txt
# o vía stdin:
echo "$texto" | python <SKILL_DIR>/scripts/check_ai_patterns.py
```

Reemplaza `<SKILL_DIR>` por la "Base directory for this skill" que aparece en el system message al cargar el skill (la ruta cambia entre instalación plugin y standalone).

El script lee `references/lexicon-es-mx.md` y reporta cada hit con línea, columna, categoría y sugerencia cuando existe. Para cada hit:

- Si es un tic real → corrige el texto y vuelve a ejecutar el escáner
- Si es una cita, marca o ejemplo legítimo → déjalo y anótalo en la entrega
- El script NO sustituye al checklist visual — solo elimina la fase mecánica de búsqueda léxica

## Modos (si el usuario lo pide)

- Marketing persuasivo
- Técnico
- Soporte
- Emails
- Documentación
- Posts/ensayo

Reglas completas: `references/modes-es-mx.md`.

## Reglas de edición

- Evitar frases infladas y lenguaje promocional si el texto no es marketing.
- Reducir conectores repetidos y muletillas ("además", "en este sentido", "cabe destacar").
- Eliminar secciones plantilla si no aportan datos.
- Mantener términos técnicos, marcas, API, código y nombres propios.
- Dividir párrafos largos cuando sea necesario para claridad.

## Salida

- Devolver solo el texto final, sin explicación, a menos que el usuario la pida.
- Si hiciste una suposición importante (tono o público), agrega una línea breve para confirmarla.
