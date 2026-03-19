---
name: humaniza
description: Humaniza textos en español (especialmente es-MX) eliminando patrones típicos de IA y devolviendo una versión natural y clara. Úsalo al editar emails, documentación,  marketing, soporte o textos técnicos en español cuando el usuario pida "humanizar", "hacerlo más natural", "quitar tono IA" o "hacerlo sonar humano".
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
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
7. Pasar QA final con `references/checklist.md`.

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
