#!/usr/bin/env python3
"""Audit how a repository publishes to npm and what it installs from it.

Reads the repo, the npm configuration and the GitHub Actions setup, and reports
the state of each: credentials on disk, orphaned Actions secrets, how the
publishing workflow authenticates, version files that disagree, README badges
pointing at a package that does not exist, dependencies that run scripts at
install time, and the local npm version against v12.

    python3 auditar_npm.py                 # the repo in the current directory
    python3 auditar_npm.py ~/code/foo
    python3 auditar_npm.py --no-network    # skip the registry and gh lookups

Writes nothing. Every finding is a proposal for the user to approve.

Standard library only: runs on any macOS or Linux with Python 3.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

OK, FALTA, REVISAR, INFO = "ok", "falta", "revisar", "info"

SIMBOLO = {OK: "  ok  ", FALTA: " MISS ", REVISAR: "CHECK ", INFO: " info "}

# Names that look like an npm publishing credential. Matched case-insensitively
# against secret names; the value of a secret is never read, here or anywhere.
PATRON_SECRETO_NPM = re.compile(r"NPM.*(TOKEN|AUTH|PUBLISH)|(TOKEN|AUTH).*NPM", re.I)

# The first npm version whose install-time defaults are the ones described in
# references/install-defaults.md.
NPM_V12 = 12

CONSULTAR_RED = True


# ---------------------------------------------------------------- utilities


def correr(comando: list[str], tiempo: int = 20) -> tuple[int, str]:
    """Run a command and return (exit code, stdout). 127 means it is not installed."""
    try:
        r = subprocess.run(
            comando, capture_output=True, text=True, timeout=tiempo, check=False
        )
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""


def existe(programa: str) -> bool:
    return correr([programa, "--version"], tiempo=10)[0] not in (127, 124)


def leer_json(ruta: Path) -> dict | None:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return None


def leer_texto(ruta: Path) -> str:
    try:
        return ruta.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def pedir(url: str, tiempo: int = 10) -> int | None:
    """HTTP status of a URL, or None if it could not be reached."""
    if not CONSULTAR_RED:
        return None
    peticion = urllib.request.Request(url, headers={"User-Agent": "auditar_npm"})
    try:
        with urllib.request.urlopen(peticion, timeout=tiempo) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


class Reporte:
    """Collects findings by section and prints them once, so the output reads as
    a report rather than as a log of the order the checks happened to run in."""

    def __init__(self) -> None:
        self.secciones: list[tuple[str, list[tuple[str, str, str]]]] = []

    def abrir(self, titulo: str) -> None:
        self.secciones.append((titulo, []))

    def add(self, estado: str, etiqueta: str, detalle: str = "") -> None:
        if not self.secciones:
            self.abrir("General")
        self.secciones[-1][1].append((estado, etiqueta, detalle))

    def imprimir(self) -> int:
        faltantes = 0
        for titulo, filas in self.secciones:
            if not filas:
                continue
            print(f"\n{titulo}")
            print("-" * len(titulo))
            for estado, etiqueta, detalle in filas:
                faltantes += estado == FALTA
                linea = f"[{SIMBOLO[estado]}] {etiqueta}"
                if detalle:
                    linea += f" — {detalle}"
                print(linea)
        print()
        return faltantes


# ---------------------------------------------------------------- checks


def revisar_npmrc(proyecto: Path, r: Reporte) -> None:
    """Credentials on disk, and whether the registry still accepts them.

    A token line is reported by its presence only. Reading or printing the value
    would put a live credential in a transcript, which is how a token becomes one
    that has to be revoked.
    """
    r.abrir("npm configuration")

    for etiqueta, ruta in (
        ("~/.npmrc", Path.home() / ".npmrc"),
        (".npmrc (project)", proyecto / ".npmrc"),
    ):
        if not ruta.exists():
            r.add(INFO, etiqueta, "not present")
            continue

        texto = leer_texto(ruta)
        if re.search(r"^\s*(//.*:)?_auth(Token)?\s*=", texto, re.M):
            r.add(
                REVISAR,
                f"{etiqueta}: token line",
                "an _authToken is present. Classic tokens were revoked in Dec 2025; "
                "if this predates that, it is dead weight producing 401s (npm logout)",
            )
        else:
            r.add(OK, f"{etiqueta}: no token line", "")

        if re.search(r"^\s*ignore-scripts\s*=\s*true", texto, re.M):
            r.add(
                INFO,
                f"{etiqueta}: ignore-scripts=true",
                "this machine already behaves like npm v12; CI probably does not",
            )

    if CONSULTAR_RED and existe("npm"):
        codigo, salida = correr(["npm", "whoami"])
        if codigo == 0 and salida:
            r.add(OK, "npm session", f"authenticated as {salida}")
        else:
            r.add(
                INFO,
                "npm session",
                "not authenticated (npm login opens a two-hour session; "
                "irrelevant if publishing happens from Actions)",
            )


def version_npm(r: Reporte) -> None:
    r.abrir("npm version")

    codigo, salida = correr(["npm", "--version"])
    if codigo != 0 or not salida:
        r.add(REVISAR, "npm", "not found on PATH")
        return

    try:
        mayor = int(salida.split(".")[0])
    except ValueError:
        r.add(INFO, "npm", salida)
        return

    if mayor >= NPM_V12:
        r.add(OK, "npm", f"{salida} — install-time defaults are on")
    else:
        r.add(
            INFO,
            "npm",
            f"{salida} — v12 defaults not applied yet; 11.16.0+ warns about them first",
        )


def repo_github(proyecto: Path) -> str | None:
    """owner/repo as GitHub spells it, read from the API rather than the folder name."""
    codigo, salida = correr(
        ["git", "-C", str(proyecto), "remote", "get-url", "origin"]
    )
    if codigo != 0 or not salida:
        return None

    m = re.search(r"github\.com[:/]+([^/]+)/(.+?)(?:\.git)?$", salida)
    if not m:
        return None
    local = f"{m.group(1)}/{m.group(2)}"

    if CONSULTAR_RED and existe("gh"):
        codigo, canonico = correr(["gh", "api", f"repos/{local}", "--jq", ".full_name"])
        if codigo == 0 and canonico:
            return canonico
    return local


def revisar_secretos(proyecto: Path, repo: str | None, r: Reporte) -> None:
    """Actions secrets that look like npm credentials, and whether anything uses them."""
    r.abrir("GitHub Actions secrets")

    if not repo:
        r.add(INFO, "repository", "no GitHub remote — skipping")
        return
    if not CONSULTAR_RED:
        r.add(INFO, "secrets", "skipped (--no-network)")
        return
    if not existe("gh"):
        r.add(INFO, "secrets", "gh is not installed — cannot list them")
        return

    codigo, salida = correr(["gh", "secret", "list", "--repo", repo])
    if codigo != 0:
        r.add(INFO, "secrets", f"could not read them for {repo}")
        return

    nombres = [l.split()[0] for l in salida.splitlines() if l.strip()]
    sospechosos = [n for n in nombres if PATRON_SECRETO_NPM.search(n)]

    if not sospechosos:
        r.add(OK, "no npm credentials stored", f"{len(nombres)} secret(s) in {repo}")
        return

    usados = leer_texto_workflows(proyecto)
    for nombre in sospechosos:
        if nombre in usados:
            r.add(
                REVISAR,
                f"secret {nombre}",
                "referenced by a workflow — token auth, replaceable by OIDC",
            )
        else:
            r.add(
                FALTA,
                f"secret {nombre} is orphaned",
                f"no workflow references it. gh secret delete {nombre} --repo {repo}",
            )


def leer_texto_workflows(proyecto: Path) -> str:
    carpeta = proyecto / ".github" / "workflows"
    if not carpeta.is_dir():
        return ""
    return "\n".join(sin_comentarios(leer_texto(f)) for f in sorted(carpeta.glob("*.y*ml")))


def sin_comentarios(texto: str) -> str:
    """YAML with its comments removed.

    A well-commented trusted-publishing workflow explains that it carries no
    NPM_TOKEN — and reading that sentence as a credential reference is exactly
    how a correct file gets reported as broken.
    """
    texto = re.sub(r"(?m)^\s*#.*$", "", texto)
    return re.sub(r"(?m)\s#.*$", "", texto)


def revisar_workflows(proyecto: Path, r: Reporte) -> None:
    """Which workflow publishes, and how it proves who it is."""
    r.abrir("Publishing workflow")

    carpeta = proyecto / ".github" / "workflows"
    archivos = sorted(carpeta.glob("*.y*ml")) if carpeta.is_dir() else []

    # A package.json marked private is an application or a toolchain, not
    # something that gets published — the absence of a publishing workflow is
    # the correct state, not a finding.
    pkg = leer_json(proyecto / "package.json") or {}
    if pkg.get("private") is True:
        r.add(INFO, "private package", "never published; nothing to automate")
        return

    if not archivos:
        r.add(
            FALTA,
            "no workflow publishes this package",
            "every release needs an interactive login (two-hour session). "
            "See references/trusted-publishing.md",
        )
        return

    publicadores = [f for f in archivos if "npm publish" in sin_comentarios(leer_texto(f))]
    if not publicadores:
        r.add(
            FALTA,
            "no workflow runs npm publish",
            f"{len(archivos)} workflow(s) present, none publishes",
        )
        return

    for archivo in publicadores:
        texto = sin_comentarios(leer_texto(archivo))
        nombre = archivo.name

        oidc = re.search(r"^\s*id-token:\s*write", texto, re.M)
        token = re.search(r"NODE_AUTH_TOKEN|NPM_TOKEN|secrets\.\w*NPM", texto)

        if oidc and not token:
            r.add(OK, f"{nombre}: OIDC", "trusted publishing, no stored secret")
        elif oidc and token:
            r.add(
                REVISAR,
                f"{nombre}: OIDC and a token",
                "a token reference puts the publish back on token auth and drops provenance",
            )
        elif token:
            r.add(
                FALTA,
                f"{nombre}: token auth",
                "long-lived credential; 2FA-bypass tokens lose direct publish ~Jan 2027",
            )
        else:
            r.add(REVISAR, f"{nombre}: no visible credential", "check how it authenticates")

        if re.search(r"tags:\s*$|-\s*['\"]?v\*", texto, re.M):
            r.add(OK, f"{nombre}: trigger", "runs on a pushed tag")
        else:
            r.add(REVISAR, f"{nombre}: trigger", "does not look tag-driven")

        if not re.search(r"GITHUB_REF_NAME|github\.ref_name", texto):
            r.add(
                REVISAR,
                f"{nombre}: no version guard",
                "nothing compares the tag against the version files before publishing",
            )


def revisar_paquete(proyecto: Path, r: Reporte) -> None:
    """The manifest itself: scope, and version files that must agree."""
    r.abrir("Package manifest")

    pkg = leer_json(proyecto / "package.json")
    if not pkg:
        r.add(INFO, "package.json", "not an npm project")
        return

    nombre = pkg.get("name", "")
    version = pkg.get("version", "")
    r.add(INFO, "package", f"{nombre}@{version}")

    if nombre.startswith("@"):
        r.add(
            INFO,
            "scoped package",
            "badges and registry URLs must carry the scope; the unscoped name is a different package",
        )

    plugin_path = proyecto / ".claude-plugin" / "plugin.json"
    if plugin_path.exists():
        plugin = leer_json(plugin_path) or {}
        if plugin.get("version") == version:
            r.add(OK, "plugin.json version", f"in sync at {version}")
        else:
            r.add(
                FALTA,
                "plugin.json is out of sync",
                f"package.json {version} vs plugin.json {plugin.get('version')} — "
                "marketplace users keep the cached old code",
            )


def revisar_badges(proyecto: Path, r: Reporte) -> None:
    """shields.io badges asking the registry for a package name that does not exist.

    The failure is silent: shields renders "package not found" instead of an error,
    so a broken badge survives for months and hides whatever it was reporting.
    """
    r.abrir("README badges")

    readme = proyecto / "README.md"
    if not readme.exists():
        r.add(INFO, "README.md", "not present")
        return

    texto = leer_texto(readme)
    nombres = set(re.findall(r"img\.shields\.io/npm/[a-z]+/([^)\s\]]+)", texto))
    if not nombres:
        r.add(INFO, "npm badges", "none")
        return

    pkg = leer_json(proyecto / "package.json") or {}
    esperado = pkg.get("name", "")

    for crudo in sorted(nombres):
        nombre = crudo.replace("%2F", "/").rstrip("?").split("?")[0]
        if esperado and nombre == esperado:
            r.add(OK, f"badge {nombre}", "matches package.json")
            continue

        estado = pedir(f"https://registry.npmjs.org/{nombre.replace('/', '%2F')}")
        if estado == 200:
            r.add(REVISAR, f"badge {nombre}", f"resolves, but package.json says {esperado}")
        elif estado is None:
            r.add(REVISAR, f"badge {nombre}", f"could not verify; package.json says {esperado}")
        else:
            r.add(
                FALTA,
                f"badge {nombre} points at nothing",
                f"registry answers {estado}; this package is {esperado}",
            )


def revisar_scripts_instalacion(proyecto: Path, r: Reporte) -> None:
    """What a user on npm v12 would be asked to approve when installing this tree."""
    r.abrir("Install-time scripts (npm v12)")

    modulos = proyecto / "node_modules"
    if not modulos.is_dir():
        r.add(INFO, "node_modules", "not installed — run npm install to measure this")
        return

    con_scripts: list[str] = []
    node_gyp: list[str] = []

    for manifiesto in modulos.glob("*/package.json"):
        datos = leer_json(manifiesto)
        if not datos:
            continue
        scripts = datos.get("scripts") or {}
        if any(k in scripts for k in ("preinstall", "install", "postinstall")):
            con_scripts.append(datos.get("name", manifiesto.parent.name))
        if "node-gyp" in json.dumps(datos.get("dependencies") or {}):
            node_gyp.append(datos.get("name", manifiesto.parent.name))

    # Scoped packages live one level deeper.
    for manifiesto in modulos.glob("@*/*/package.json"):
        datos = leer_json(manifiesto)
        if not datos:
            continue
        scripts = datos.get("scripts") or {}
        if any(k in scripts for k in ("preinstall", "install", "postinstall")):
            con_scripts.append(datos.get("name", manifiesto.parent.name))

    if not con_scripts and not node_gyp:
        r.add(OK, "no dependency runs install scripts", "npm v12 installs this cleanly")
        return

    for nombre in sorted(set(con_scripts)):
        r.add(REVISAR, f"{nombre} declares an install script", "needs approval on npm v12")
    for nombre in sorted(set(node_gyp) - set(con_scripts)):
        r.add(REVISAR, f"{nombre} pulls node-gyp", "implicit build, off by default on npm v12")

    r.add(
        INFO,
        "authoritative check",
        "npm approve-scripts --allow-scripts-pending, then commit the allowlist",
    )


def main() -> int:
    global CONSULTAR_RED

    p = argparse.ArgumentParser(
        description="Audit how a repository publishes to npm and what it installs from it."
    )
    p.add_argument("ruta", nargs="?", default=".", help="project directory (default: .)")
    p.add_argument(
        "--no-network",
        action="store_true",
        help="skip the registry, gh and npm whoami lookups",
    )
    args = p.parse_args()

    CONSULTAR_RED = not args.no_network

    proyecto = Path(os.path.expanduser(args.ruta)).resolve()
    if not proyecto.is_dir():
        p.error(f"{args.ruta} is not a directory")

    print(f"\nnpm supply-chain audit of {proyecto}")

    r = Reporte()
    version_npm(r)
    revisar_npmrc(proyecto, r)
    revisar_paquete(proyecto, r)
    revisar_workflows(proyecto, r)
    revisar_secretos(proyecto, repo_github(proyecto), r)
    revisar_badges(proyecto, r)
    revisar_scripts_instalacion(proyecto, r)

    faltan = r.imprimir()
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
