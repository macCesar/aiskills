"""
slug_demangle.py — Reverses Stitch's accent stripping in screen filenames.

Google Stitch replaces accented characters (á, é, í, ó, ú, ñ, ü) with `_`
when exporting screens, so "Configuración" becomes "configuraci_n" and
"Membresías" becomes "membres_as".

This module exposes a single function `demangle_to_title(slug)` that infers
the readable display title for a Stitch-style mangled slug, using a
dictionary of common Spanish words with their accent positions.

For slugs the dictionary doesn't cover, the user can still override the
title explicitly via `Title | Description` in DESIGN.md.
"""
import re


# Mangled → fixed (lowercase). Longer entries are applied first so that
# composites like "men_m_s" beat the standalone "men_".
WORD_REPLACEMENTS: dict[str, str] = {
    # -ción / -sión nouns
    "acci_n": "acción",
    "aceptaci_n": "aceptación",
    "activaci_n": "activación",
    "actualizaci_n": "actualización",
    "administraci_n": "administración",
    "aplicaci_n": "aplicación",
    "asignaci_n": "asignación",
    "autenticaci_n": "autenticación",
    "calificaci_n": "calificación",
    "cancelaci_n": "cancelación",
    "clasificaci_n": "clasificación",
    "comunicaci_n": "comunicación",
    "configuraci_n": "configuración",
    "confirmaci_n": "confirmación",
    "conexi_n": "conexión",
    "creaci_n": "creación",
    "descripci_n": "descripción",
    "direcci_n": "dirección",
    "discusi_n": "discusión",
    "donaci_n": "donación",
    "duraci_n": "duración",
    "edici_n": "edición",
    "educaci_n": "educación",
    "elecci_n": "elección",
    "evaluaci_n": "evaluación",
    "exclusi_n": "exclusión",
    "facturaci_n": "facturación",
    "geolocalizaci_n": "geolocalización",
    "habitaci_n": "habitación",
    "identificaci_n": "identificación",
    "informaci_n": "información",
    "inscripci_n": "inscripción",
    "instalaci_n": "instalación",
    "introducci_n": "introducción",
    "modificaci_n": "modificación",
    "navegaci_n": "navegación",
    "notificaci_n": "notificación",
    "opci_n": "opción",
    "operaci_n": "operación",
    "organizaci_n": "organización",
    "personalizaci_n": "personalización",
    "posici_n": "posición",
    "publicaci_n": "publicación",
    "recuperaci_n": "recuperación",
    "registraci_n": "registración",
    "relaci_n": "relación",
    "reservaci_n": "reservación",
    "revisi_n": "revisión",
    "secci_n": "sección",
    "selecci_n": "selección",
    "soluci_n": "solución",
    "suscripci_n": "suscripción",
    "transacci_n": "transacción",
    "ubicaci_n": "ubicación",
    "validaci_n": "validación",
    "verificaci_n": "verificación",
    "visualizaci_n": "visualización",
    # composite phrases (must beat their standalone parts)
    "men_m_s": "menú más",
    "men_principal": "menú principal",
    # standalone words with accents
    "men_": "menú",
    "caf_": "café",
    "p_gina": "página",
    "p_ginas": "páginas",
    "art_culo": "artículo",
    "art_culos": "artículos",
    "categor_a": "categoría",
    "categor_as": "categorías",
    "membres_a": "membresía",
    "membres_as": "membresías",
    "pol_tica": "política",
    "pol_ticas": "políticas",
    "m_s": "más",
    "qu_": "qué",
    "c_mo": "cómo",
    "d_a": "día",
    "d_as": "días",
    # words with ñ
    "esc_ner": "escáner",
    "rese_a": "reseña",
    "rese_as": "reseñas",
    "espa_a": "españa",
    "espa_ol": "español",
    "peque_o": "pequeño",
    "peque_a": "pequeña",
    "compa_a": "compañía",
    "compa_as": "compañías",
    "se_al": "señal",
    "se_ales": "señales",
    "ma_ana": "mañana",
    "due_o": "dueño",
    "ni_o": "niño",
    "ni_a": "niña",
    "a_o": "año",
    "a_os": "años",
    # other common standalone
    "_xito": "éxito",
    "_rea": "área",
    "_reas": "áreas",
    "_ltimo": "último",
    "_ltima": "última",
    "_nico": "único",
    "_nica": "única",
    "_til": "útil",
    "_tiles": "útiles",
    "tel_fono": "teléfono",
    "n_mero": "número",
    "n_meros": "números",
    "c_digo": "código",
    "c_digos": "códigos",
    "m_dico": "médico",
    "m_dica": "médica",
    "p_blico": "público",
    "p_blica": "pública",
    "f_cil": "fácil",
    "r_pido": "rápido",
    "r_pida": "rápida",
    "_ndice": "índice",
    "_xitos": "éxitos",
}


def demangle_word(token: str) -> str:
    """
    Try to recover the accented form of a single mangled token (no separators).
    Returns the token unchanged if no entry matches.
    """
    return WORD_REPLACEMENTS.get(token.lower(), token)


def demangle_to_title(slug: str) -> str:
    """
    Convert a (possibly mangled) snake-case slug into a readable display title.

    Examples:
        "configuraci_n_oscuro" → "Configuración Oscuro"
        "membres_as_y_pagos"   → "Membresías Y Pagos"
        "home_screen"          → "Home Screen"
        "men_m_s"              → "Menú Más"
    """
    if not slug:
        return ""

    s = slug.strip().lower()

    # Apply dictionary replacements, longest first to handle composites correctly.
    # We anchor each match to slug-token boundaries (start, end, or non-mangled `_`
    # separator) so a short entry like "men_" does not eat into "menma".
    for mangled in sorted(WORD_REPLACEMENTS.keys(), key=len, reverse=True):
        fixed = WORD_REPLACEMENTS[mangled]
        pattern = re.compile(
            rf"(?:^|(?<=[^a-záéíóúñü\d]))"
            rf"{re.escape(mangled)}"
            rf"(?=$|[^a-záéíóúñü\d])",
            re.IGNORECASE,
        )
        s = pattern.sub(fixed, s)

    # Replace remaining separators and apply Title Case.
    return s.replace("_", " ").replace("-", " ").title()


def slug_to_title(slug: str) -> str:
    """
    Canonical slug → display title for the showcase pipeline.

    Strips a leading numeric ordering prefix (``01_splash_screen`` →
    ``splash_screen``) and then delegates to :func:`demangle_to_title`.
    Falls back to ``slug.title()`` only in the edge case where the entire
    slug is digits/underscores.

    This is the single source of truth used by both ``parse_design_md`` and
    ``build_showcase``.
    """
    if not slug:
        return ""
    stripped = re.sub(r"^[\d_]+", "", slug)
    return demangle_to_title(stripped) or slug.title()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python slug_demangle.py <slug>", file=sys.stderr)
        sys.exit(1)
    print(slug_to_title(sys.argv[1]))
