---
name: humaniza
description: 'Úsalo cuando humanices textos en español (especialmente es-MX) — editando emails, documentación, marketing, soporte o textos técnicos, eliminando patrones típicos de IA y devolviendo una versión natural y clara. Triggers: "humanizar", "hacerlo más natural", "quitar tono IA", "hacerlo sonar humano".'
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Humaniza

Editor de estilo para español de México. El objetivo es quitar tics de IA sin cambiar el contenido.

## Alcance

- Mantener significado, datos y estructura general.
- Respetar puntuación y signos de apertura/cierre.
- Conservar registro (tú/usted) salvo solicitud explícita.
- Preferir es-MX: evitar "vosotros", "ordenador", "móvil", "coche" cuando el texto sea neutro.
- No inventar fuentes ni datos.

## Flujo

1. Detectar tono y audiencia a partir del texto.
2. Si el usuario pide un modo (marketing, técnico, soporte, etc.), priorizarlo.
3. Identificar tics de IA con `references/ai-patterns-es.md` y `references/lexicon-es-mx.md`.
4. Reescribir: cortar relleno, concretar, variar ritmo, usar "ser/estar" cuando sea más claro.
5. Ajustar el tono según `references/modes-es-mx.md` si aplica.
6. Añadir voz humana cuando aplique con `references/voice-es-mx.md`.
7. Verificar el resultado con el escáner determinístico — ver "Verificación con script" abajo — y después pasar el QA visual con `references/checklist.md`.

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
