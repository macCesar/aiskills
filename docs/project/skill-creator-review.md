# Skill Creator y habilidad de fichas de tienda

Revisión del 2026-10-30, Codex · GPT-6. Se verificaron los archivos instalados y las fuentes oficiales, no sólo sus fechas de instalación.

## Comparación y limpieza solicitada

| Variante encontrada | Fuente y revisión real | Resultado |
| --- | --- | --- |
| OpenAI integrado: `~/.codex/skills/.system/skill-creator/SKILL.md` | `openai/codex`, cambio `5e32f728f1f86a967c6be057351f12505778df8f`, 2026-08-13; archivo idéntico al upstream consultado | Conservado y usado como guía principal |
| Anthropic: `skill-creator@claude-plugins-official` | `anthropics/skills`, cambio `b0cbd3df1533b396d281a6886d5132f623393a9c`, 2026-03-06; archivo idéntico al upstream consultado | Desinstalado de Codex y Claude Code por instrucción explícita de César |
| Copia importada en `~/.agents/skills/synced/.../skill-creator/` | Adaptación de Anthropic con sustituciones de nombre; conservaba referencias como `Codex -p`, que en Codex selecciona un perfil, no equivale a `claude -p` | Carpeta y copia en `~/.claude/skills/synced/.../skill-creator/` eliminadas por la misma instrucción |

La instalación de Anthropic tenía fecha de octubre, pero esa fecha no acreditaba instrucciones posteriores a las de OpenAI. Anthropic era una guía oficial vigente para su producto, no un archivo falsificado u obsoleto por existir OpenAI. Se retiró para dejar una sola opción, según la preferencia expresa de César. Las dos guías oficiales tienen énfasis distintos: OpenAI prioriza alcance, instrucciones breves, referencias condicionales y validación proporcional; Anthropic incluye un flujo más extenso de pruebas, comparación y optimización de descripciones para Claude.

Se usaron `codex plugin remove skill-creator@claude-plugins-official --json` y `claude plugin uninstall skill-creator@claude-plugins-official --scope user --json`. Ambos confirmaron éxito. Después se comprobaron ausencia del registro de Codex, del registro instalado de Claude, de la caché de ese plugin en Codex y de las dos carpetas sincronizadas; el creador integrado permanece. Un catálogo ya cargado en una sesión puede seguir mostrando entradas anteriores hasta recargarlo. No se eliminó el marketplace ni otros plugins.

Fuentes: [OpenAI Skill Creator](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md), [historial de OpenAI](https://github.com/openai/codex/commits/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md), [Anthropic Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), [historial de Anthropic](https://github.com/anthropics/skills/commits/main/skills/skill-creator/SKILL.md), [especificación Agent Skills](https://agentskills.io/specification).

## Decisión de diseño

Se creó `skills/store-listing-optimization/`, independiente de `store-screenshots`. La nueva habilidad cubre textos, palabras clave, localizaciones, adquisición/conversión, escenarios proporcionales y la ejecución/verificación autorizada en consolas. La existente conserva producción visual, especificaciones de imágenes/video y configuración de páginas/experimentos. Ambas se enlazan sin duplicar esos procedimientos.

César pidió explícitamente Humanizer para inglés y Humaniza para español. El flujo abre esos editores antes de guardar/enviar, ejecuta el escáner de Humaniza, conserva hechos/limitaciones y vuelve a contar los campos. Si un editor falta, se informa y se hace una revisión manual identificada como tal, sin afirmar que se ejecutó la habilidad ausente. La guía distingue propuesta, guardado, envío, revisión y publicación; separa clics, adquisiciones, base instalada y actividad; preserva otros borradores y autorizaciones existentes.

La integración toca únicamente el catálogo de producto en `lib/config.js`, la documentación y habilidades. No modifica el motor compartido, instalador, prompts o regresiones comunes. Paridad con TiTools: **excepción de producto**, porque su catálogo Titanium no debe instalar esta habilidad general. No se requiere copiarla al hermano ni se declara una nueva verificación del motor.

Se crearon enlaces al checkout en `~/.agents/skills/store-listing-optimization` y su espejo de Claude, según el esquema de desarrollo existente. No se publicó a npm/marketplace ni se hizo commit/push/tag. Se conserva 1.28.1 y la entrada Unreleased; el incremento coordinado de versiones y las comprobaciones completas de release quedan para una publicación explícitamente solicitada.

## Verificación

- Validador oficial de Skill Creator: válido. El primer intento encontró que el Python del entorno no tenía PyYAML; se ejecutó después mediante `uv run --with pyyaml --no-project`, aislando la dependencia y sin cambiar las dependencias de AISkills.
- `node --test --test-name-pattern='skills are wired|store-listing-optimization|store-screenshots has no broken|release manifests stay in sync' test/manifest.test.js`: 11 pruebas, 11 correctas, cero fallos.
- `npx eslint lib/config.js`: correcto. Referencias locales, ausencia de placeholders y delimitadores de bloques: correctos.
- Prueba independiente con cuatro escenarios sintéticos, sólo simulación: copia bilingüe y afirmaciones no acreditadas con otro binario pendiente; Apple publicado con campos bloqueados; periodos/métricas e ingresos no especificados; envío con verificaciones pendientes. No encontró un fallo sustantivo del flujo. La comprobación de longitud detectó y corrigió una descripción de 81 caracteres antes de entregar; los cinco campos españoles pasaron el escáner. No se usaron cuentas ni se enviaron textos reales durante estas pruebas.
- Cierre: prueba JSON enfocada 1/1; npm dry run incluye los seis archivos nuevos y excluye notas privadas/bytecode; enlaces, imports sin status y whitespace correctos.
- Enrutamiento observado: redimensionar capturas y corregir un crash no activan esta habilidad; revisar conversión/descripción y aplicar textos bilingües aprobados sí.

Los escenarios reproducibles están en `skills/store-listing-optimization/evals/evals.json`. La evidencia detallada temporal de esta ejecución está en `/tmp/store-listing-skill-eval/review/`; no se depende de que esa carpeta sobreviva. Las simulaciones no certifican publicación real ni mejora de conversión, y no se midió una ganancia frente a una ejecución sin habilidad.

## Ampliación de estadísticas y presencia completa

Tras revisar la primera versión, César pidió que las decisiones partan de las estadísticas de ambas tiendas, que la auditoría abarque las herramientas disponibles y que la nueva habilidad invoque explícitamente `store-screenshots` sin duplicarla. Se amplió el flujo con inventario de presencia/herramientas, disponibilidad frente a uso/configuración, requisitos/costes, análisis por fuente/país/idioma/versión, cobertura/consentimiento, prioridades y métricas/guardarraíles por acción. Una revisión limitada a texto no se presenta como auditoría completa de la tienda.

La referencia adicional `store-capabilities.md` relaciona CPP/PPO/Asset Library/In-App Events/featuring/campañas de Apple con fichas personalizadas/experimentos/biblioteca/Promotional Content/herramientas de crecimiento de Google, sin transferir requisitos ni suponer elegibilidad. La sección inicial del skill enlaza e invoca `store-screenshots` antes de capturar, generar, exportar o configurar recursos/páginas/experimentos, y conserva sus fuentes, generadores y validación.

La investigación usó documentación oficial vigente de Apple Analytics, definiciones de conversión, fuentes y cobertura de uso; y de Google Statistics, benchmarks, crecimiento, experimentos y novedades. Se documentó expresamente que las métricas de tiendas no acreditan uso de funciones concretas sin eventos/pruebas adicionales. Las fuentes están enlazadas en las cuatro referencias de la habilidad.

El quinto caso independiente distinguió correctamente conversión Apple 3%→1.4% de descargas/visitantes 30%→14%, detectó la mezcla de tráfico y evitó inferir una caída poblacional de actividad al cambiar la cobertura. Se corrigió una ambigüedad menor del cierre: sólo pedir texto propuesto cuando realmente se recomienda modificarlo. La validación enfocada tras la ampliación pasó 5/5; validador oficial, enlaces y empaquetado de siete archivos correctos. El sexto escenario cubre una auditoría completa pedida con acceso parcial a consolas. No se configuraron herramientas reales ni se atribuye a estos casos una mejora medida de descargas.

El sexto caso independiente terminó sin fallos sustantivos: inventarió medios, promoción, atribución y programas condicionales; mantuvo sin verificar lo que no podía observar y preparó el brief para `store-screenshots`, sin repetir producción ni activar herramientas. Resultado temporal: `/tmp/store-listing-skill-eval/review/capability-case.md`. Se verificó también el enlace local directo al skill compañero tras añadir esa sección.
