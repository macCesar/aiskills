#!/usr/bin/env python3
"""
Barrido de seguridad por patrones para proyectos Laravel.

Hace, sin gastar tokens, la parte mecánica de una revisión de seguridad:
detecta la versión y la estructura del proyecto, corre `composer audit` y
busca en el código los patrones que producen vulnerabilidades reales. Cada
coincidencia es un sitio que el agente debe leer para confirmar o descartar,
no un hallazgo: el script encuentra dónde mirar, el agente decide.

Uso:
    python3 barrido_laravel.py /ruta/al/proyecto
    python3 barrido_laravel.py /ruta/al/proyecto --json
    python3 barrido_laravel.py /ruta/al/proyecto --sin-composer --max 10

Sólo usa la biblioteca estándar. No ejecuta el código del proyecto y no lee
valores de `.env`: de ese archivo sólo mira si APP_DEBUG está en true.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

DIRECTORIOS = ['app', 'routes', 'config', 'resources/views', 'bootstrap']
EXCLUIDOS = {'vendor', 'node_modules', 'storage', 'cache', '.git', 'build'}


@dataclass
class Patron:
    id: str
    titulo: str
    regex: str
    # Prefijos de ruta donde aplica; vacío significa todos los directorios barridos.
    en: list = field(default_factory=list)
    # Prefijos de ruta excluidos.
    fuera: list = field(default_factory=list)
    flags: int = 0


RAW_SQL = r'(?:whereRaw|orWhereRaw|selectRaw|orderByRaw|havingRaw|groupByRaw|DB::raw|DB::select|DB::statement|DB::unprepared|DB::update|DB::delete|DB::insert)\s*\('

PATRONES = [
    Patron('SQL-RAW', 'SQL crudo con variables interpoladas o concatenadas',
           RAW_SQL + r'(?:\s*"[^"]*\$|[^;]*?[\'"]\s*\.\s*\$)'),
    Patron('MASS-ASSIGN', 'Asignación masiva con toda la petición o sin $fillable',
           r'->(?:create|update|fill|forceFill|insert|updateOrCreate|firstOrCreate)\(\s*\$request->(?:all|input|post)\(\s*\)|\$guarded\s*=\s*\[\s*\]'),
    Patron('ROLE-FROM-REQUEST', 'Rol o privilegio tomado de la petición',
           r'\$request->(?:only|input|get|validated|post)\([^)]*[\'"](?:rol_id|role_id|role|roles|is_admin|admin|permissions?|nivel|level)[\'"]|[\'"](?:rol_id|role_id|is_admin)[\'"]\s*=>\s*\$request'),
    Patron('AUTH-ENTRY', 'Punto de entrada de sesión o registro (revisar quién puede entrar)',
           r'Auth::attempt\(|Auth::login\(|auth\(\)->attempt\(|User::(?:create|forceCreate)\(|->createToken\('),
    Patron('RESET-ENUM', 'Respuesta de recuperación de contraseña que distingue si la cuenta existe',
           r'RESET_LINK_SENT\s*\?|==\s*Password::RESET_LINK_SENT|===\s*Password::RESET_LINK_SENT'),
    Patron('RESET-URL', 'Enlace con token armado dentro de una notificación o correo',
           r'(?:route|url|URL::(?:route|to|signedRoute|temporarySignedRoute))\([^;]*token',
           en=['app/Notifications', 'app/Mail']),
    Patron('SSRF', 'Petición del servidor a una URL o ruta que llega en una variable',
           r'\b(?:file_get_contents|fopen|curl_init|get_headers|getimagesize|simplexml_load_file|readfile|copy)\s*\(\s*\$'
           r'|Http::(?:[A-Za-z]+\([^)]*\)->)*(?:get|post|put|patch|head|delete|send)\s*\(\s*\$'
           r'|->(?:get|post|request)\(\s*\$(?:url|uri|link|endpoint|href)\b'),
    Patron('UPLOAD-NAME', 'Nombre o directorio de archivo subido que decide el cliente',
           r'getClientOriginalName\(\)|getClientOriginalExtension\(\)|->(?:store|storeAs|storePublicly|storePubliclyAs|move)\(\s*\$request->'),
    Patron('PATH-FROM-INPUT', 'Ruta de archivo construida con datos de la petición o de la URL',
           r'(?:storage_path|public_path|base_path|Storage::(?:get|delete|download|put|exists|path|deleteDirectory)|response\(\)->(?:download|file)|File::(?:delete|deleteDirectory|get)|unlink|rmdir)\s*\([^;]*\$request'
           # {$theme->slug} es un atributo de modelo; {$nombre} suele venir de la URL.
           r'|(?:storage_path|public_path|base_path)\(\s*"[^"]*\{?\$(?!\w+->)'),
    Patron('XSS-BLADE', 'Salida sin escapar en Blade',
           r'\{!!(?!\s*(?:csrf_field|method_field|\$__env|Vite::|vite\(|json_encode|\$slot\b|\$attributes\b))',
           en=['resources/views']),
    Patron('EXEC', 'Ejecución de comandos, eval o unserialize con una variable',
           r'\b(?:eval|exec|shell_exec|system|passthru|popen|proc_open|unserialize)\s*\(\s*\$'),
    Patron('ENV-OUTSIDE-CONFIG', 'env() fuera de config/: devuelve null con la configuración cacheada',
           r'\benv\(', fuera=['config']),
    Patron('SECRET-FALLBACK', 'Secreto con un valor por defecto escrito en el código',
           r'env\(\s*[\'"][A-Z0-9_]*(?:SECRET|KEY|TOKEN|PASS|PASSWORD|SALT)[A-Z0-9_]*[\'"]\s*,\s*[\'"][^\'"]+[\'"]'),
    Patron('GET-DESTRUCTIVE', 'Ruta GET que cambia datos (sin protección CSRF)',
           r'Route::get\(\s*[\'"][^\'"]*(?:delete|destroy|borrar|eliminar|remove|quitar)[^\'"]*[\'"]',
           en=['routes'], flags=re.IGNORECASE),
    Patron('API-MUTATION', 'Ruta de API que escribe (confirmar autenticación y límite de peticiones)',
           r'Route::(?:post|put|patch|delete|any|match)\(', en=['routes/api.php']),
    Patron('CSRF-EXCEPT', 'Rutas excluidas de la protección CSRF',
           r'protected\s+\$except\s*=\s*\[\s*[\'"]|(?:validateCsrfTokens|preventRequestForgery)\([^)]*except'),
    Patron('LOG-SECRETS', 'Log que vuelca cabeceras o la petición completa',
           # El array del contexto suele ir en otra línea que la llamada a Log::.
           r'(?:Log::|logger\(|->log\().*(?:headers->all\(\)|\$request->all\(\))|=>\s*\$request->headers->all\(\)'),
]


def es_de(ruta, prefijos):
    return any(ruta == p or ruta.startswith(p.rstrip('/') + '/') for p in prefijos)


def archivos_php(raiz):
    for base in DIRECTORIOS:
        inicio = os.path.join(raiz, base)
        if not os.path.exists(inicio):
            continue
        for actual, dirs, nombres in os.walk(inicio):
            dirs[:] = [d for d in dirs if d not in EXCLUIDOS]
            for nombre in nombres:
                if nombre.endswith('.php'):
                    completo = os.path.join(actual, nombre)
                    yield os.path.relpath(completo, raiz).replace(os.sep, '/'), completo


def leer(ruta):
    try:
        with open(ruta, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def detectar_version(raiz):
    """Devuelve (versión o None, mayor o None, de dónde salió)."""
    lock = os.path.join(raiz, 'composer.lock')
    if os.path.exists(lock):
        try:
            with open(lock, encoding='utf-8') as f:
                datos = json.load(f)
            for paquete in datos.get('packages', []):
                if paquete.get('name') == 'laravel/framework':
                    version = paquete.get('version', '').lstrip('v')
                    mayor = re.match(r'(\d+)', version)
                    return version, int(mayor.group(1)) if mayor else None, 'composer.lock'
        except (OSError, ValueError):
            pass

    composer = os.path.join(raiz, 'composer.json')
    if os.path.exists(composer):
        try:
            with open(composer, encoding='utf-8') as f:
                requerido = json.load(f).get('require', {}).get('laravel/framework')
            if requerido:
                mayor = re.search(r'(\d+)', requerido)
                return requerido, int(mayor.group(1)) if mayor else None, 'composer.json'
        except (OSError, ValueError):
            pass

    # Laravel 3 y 4 no siempre traen composer.lock; se reconocen por su estructura.
    if os.path.exists(os.path.join(raiz, 'laravel', 'core.php')) or os.path.exists(os.path.join(raiz, 'paths.php')):
        return '3.x', 3, 'estructura (laravel/core.php o paths.php)'
    if os.path.exists(os.path.join(raiz, 'bootstrap', 'start.php')) and os.path.isdir(os.path.join(raiz, 'app', 'start')):
        return '4.x', 4, 'estructura (bootstrap/start.php)'

    return None, None, 'no encontrada'


def detectar_estructura(raiz):
    app = leer(os.path.join(raiz, 'bootstrap', 'app.php'))
    if '->withMiddleware(' in app:
        return 'bootstrap/app.php'
    if os.path.exists(os.path.join(raiz, 'app', 'Http', 'Kernel.php')):
        return 'app/Http/Kernel.php'
    return 'desconocida'


def correr_composer_audit(raiz):
    if not os.path.exists(os.path.join(raiz, 'composer.lock')):
        return {'estado': 'omitido', 'motivo': 'no hay composer.lock'}
    composer = shutil.which('composer')
    if not composer:
        return {'estado': 'omitido', 'motivo': 'composer no está en el PATH'}
    try:
        # --no-plugins: la auditoría no los necesita, evita que un composer.lock
        # anterior a allow-plugins aborte el comando y no ejecuta código del proyecto.
        proceso = subprocess.run(
            [composer, 'audit', '--locked', '--no-plugins', '--format=json', '--no-interaction'],
            cwd=raiz, capture_output=True, text=True, timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {'estado': 'error', 'motivo': 'composer audit tardó más de 180 s'}

    # composer audit sale con código distinto de 0 cuando encuentra avisos, así
    # que el código no distingue un fallo. Lo que lo distingue es la salida: sin
    # un JSON con la clave "advisories" no hubo auditoría, y reportar "sin
    # avisos" en ese caso es un falso negativo.
    try:
        datos = json.loads(proceso.stdout)
    except ValueError:
        datos = None
    if not isinstance(datos, dict) or 'advisories' not in datos:
        detalle = ' '.join((proceso.stderr or proceso.stdout or 'sin salida').split())
        return {'estado': 'error', 'motivo': f'composer audit no produjo un resultado (código {proceso.returncode}): {detalle[:300]}'}

    avisos = datos.get('advisories') or {}
    paquetes = []
    for nombre, lista in (avisos.items() if isinstance(avisos, dict) else []):
        for aviso in (lista if isinstance(lista, list) else list(lista.values())):
            paquetes.append({
                'paquete': nombre,
                'titulo': aviso.get('title'),
                'cve': aviso.get('cve'),
                'versiones_afectadas': aviso.get('affectedVersions'),
                'enlace': aviso.get('link'),
            })
    return {'estado': 'ok', 'avisos': paquetes, 'abandonados': datos.get('abandoned') or {}}


def revisiones_de_archivo(raiz, estructura, contenidos):
    """Chequeos que miran el proyecto entero, no una línea."""
    notas = []

    usa_reset = any(re.search(r'sendResetLink|Password::broker|ResetPassword|sendPasswordResetNotification', c)
                    for c in contenidos.values())
    fija_url = any('createUrlUsing' in c or 'forceRootUrl' in c for c in contenidos.values())
    if estructura == 'bootstrap/app.php':
        confia_hosts = 'trustHosts(' in contenidos.get('bootstrap/app.php', '')
    else:
        kernel = contenidos.get('app/Http/Kernel.php', '')
        confia_hosts = bool(re.search(r'^\s*\\?App\\Http\\Middleware\\TrustHosts::class', kernel, re.MULTILINE))
    if usa_reset and not fija_url and not confia_hosts:
        notas.append({
            'id': 'HOST-HEADER',
            'titulo': 'Restablecimiento de contraseña sin raíz de URL fija ni hosts de confianza',
            'detalle': 'Los enlaces con token se arman con la cabecera Host de la petición.',
        })

    for ruta, contenido in contenidos.items():
        if 'ServerFactory::create' in contenido and 'max_image_size' not in contenido:
            notas.append({
                'id': 'IMAGE-LIMIT',
                'titulo': 'Servidor de Glide sin max_image_size',
                'detalle': ruta,
            })

    cors = contenidos.get('config/cors.php', '')
    if re.search(r"'allowed_origins'\s*=>\s*\[\s*'\*'", cors) and re.search(r"'supports_credentials'\s*=>\s*true", cors):
        notas.append({
            'id': 'CORS-WILDCARD',
            'titulo': 'CORS con cualquier origen y credenciales',
            'detalle': 'config/cors.php',
        })

    middleware = [r for r in contenidos if r.startswith('app/Http/Middleware/')]
    for ruta in middleware:
        contenido = contenidos[ruta]
        if re.search(r'->user\(\)|auth\(\)|Auth::', contenido) and len(re.findall(r'return\s+\$next\(', contenido)) >= 2:
            notas.append({
                'id': 'AUTHZ-MIDDLEWARE',
                'titulo': 'Middleware de autorización propio con varias salidas que dejan pasar',
                'detalle': ruta,
            })

    guards = contenidos.get('config/auth.php', '')
    proveedores = re.findall(r"'driver'\s*=>\s*'(?:session|sanctum|token|passport)'\s*,\s*'provider'\s*=>\s*'(\w+)'", guards)
    if len(proveedores) > len(set(proveedores)):
        notas.append({
            'id': 'SHARED-PROVIDER',
            'titulo': 'Varios guards comparten la misma tabla de usuarios',
            'detalle': 'config/auth.php: ' + ', '.join(sorted(set(p for p in proveedores if proveedores.count(p) > 1))),
        })

    env = os.path.join(raiz, '.env')
    if os.path.exists(env):
        for linea in leer(env).splitlines():
            if re.match(r'\s*APP_DEBUG\s*=\s*"?true"?\s*$', linea, re.IGNORECASE):
                notas.append({
                    'id': 'APP-DEBUG',
                    'titulo': 'APP_DEBUG=true en .env',
                    'detalle': 'Si es el .env de producción, los errores muestran código y configuración.',
                })
                break

    return notas


def barrer(raiz, maximo):
    contenidos = {ruta: leer(completo) for ruta, completo in archivos_php(raiz)}
    compilados = [(p, re.compile(p.regex, p.flags)) for p in PATRONES]
    resultados = []

    for patron, regex in compilados:
        coincidencias = []
        for ruta, contenido in contenidos.items():
            if patron.en and not es_de(ruta, patron.en):
                continue
            if patron.fuera and es_de(ruta, patron.fuera):
                continue
            for numero, linea in enumerate(contenido.splitlines(), 1):
                if regex.search(linea):
                    coincidencias.append({'archivo': ruta, 'linea': numero, 'codigo': linea.strip()[:180]})
        if coincidencias:
            resultados.append({
                'id': patron.id,
                'titulo': patron.titulo,
                'total': len(coincidencias),
                'coincidencias': coincidencias[:maximo],
            })

    return contenidos, resultados


def imprimir(informe):
    print(f"# Barrido de seguridad Laravel — {informe['raiz']}\n")
    print(f"- Versión: {informe['version'] or 'desconocida'} ({informe['origen_version']})")
    print(f"- Estructura: {informe['estructura']}")
    print(f"- Archivos PHP barridos: {informe['archivos']}\n")

    audit = informe['composer_audit']
    print('## composer audit\n')
    if audit['estado'] != 'ok':
        print(f"- {audit['estado']}: {audit.get('motivo', '')}\n")
    elif not audit['avisos']:
        print('- Sin avisos de seguridad en las dependencias.\n')
    else:
        por_paquete = {}
        for aviso in audit['avisos']:
            por_paquete.setdefault(aviso['paquete'], []).append(aviso)
        print(f"- {len(audit['avisos'])} avisos en {len(por_paquete)} paquetes\n")
        for paquete, lista in sorted(por_paquete.items(), key=lambda par: -len(par[1])):
            ids = [a['cve'] for a in lista if a['cve']]
            cves = ', '.join(ids[:4]) + (f' y {len(ids) - 4} más' if len(ids) > 4 else '') if ids else 'sin CVE'
            print(f"- {paquete}: {len(lista)} — {lista[0]['titulo']} ({cves})")
        print()
    if audit.get('abandonados'):
        print('Paquetes abandonados: ' + ', '.join(audit['abandonados']) + '\n')

    print('## Chequeos de proyecto\n')
    if not informe['proyecto']:
        print('- Ninguno disparado.\n')
    for nota in informe['proyecto']:
        print(f"- **{nota['id']}** — {nota['titulo']}: {nota['detalle']}")
    print()

    print('## Coincidencias por patrón\n')
    if not informe['patrones']:
        print('- Ninguna.\n')
    for grupo in informe['patrones']:
        mostradas = len(grupo['coincidencias'])
        extra = f" (se muestran {mostradas})" if mostradas < grupo['total'] else ''
        print(f"### {grupo['id']} — {grupo['titulo']}: {grupo['total']}{extra}\n")
        for c in grupo['coincidencias']:
            print(f"- `{c['archivo']}:{c['linea']}` {c['codigo']}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Barrido de seguridad por patrones para proyectos Laravel.')
    parser.add_argument('raiz', help='Carpeta del proyecto Laravel')
    parser.add_argument('--json', action='store_true', help='Salida en JSON')
    parser.add_argument('--sin-composer', action='store_true', help='No correr composer audit (evita la red)')
    parser.add_argument('--max', type=int, default=25, help='Máximo de coincidencias listadas por patrón (25)')
    args = parser.parse_args()

    raiz = os.path.abspath(args.raiz)
    if not os.path.isdir(raiz):
        print(f'No existe la carpeta: {raiz}', file=sys.stderr)
        return 2
    if not (os.path.exists(os.path.join(raiz, 'artisan')) or os.path.exists(os.path.join(raiz, 'composer.json'))):
        print(f'No parece un proyecto Laravel (no hay artisan ni composer.json): {raiz}', file=sys.stderr)
        return 2

    version, mayor, origen = detectar_version(raiz)
    estructura = detectar_estructura(raiz)

    if mayor is not None and mayor < 5:
        informe = {
            'raiz': raiz, 'version': version, 'mayor': mayor, 'origen_version': origen, 'estructura': estructura,
            'fuera_de_alcance': True,
            'motivo': 'Laravel 3 y 4 tienen otra estructura y otras APIs; los patrones de este barrido no aplican.',
        }
        if args.json:
            print(json.dumps(informe, ensure_ascii=False, indent=2))
        else:
            print(f"# Barrido de seguridad Laravel — {raiz}\n")
            print(f"- Versión: {version} ({origen})")
            print(f"- Fuera de alcance: {informe['motivo']}")
        return 0

    contenidos, patrones = barrer(raiz, max(1, args.max))
    informe = {
        'raiz': raiz,
        'version': version,
        'mayor': mayor,
        'origen_version': origen,
        'estructura': estructura,
        'archivos': len(contenidos),
        'composer_audit': {'estado': 'omitido', 'motivo': '--sin-composer'} if args.sin_composer else correr_composer_audit(raiz),
        'proyecto': revisiones_de_archivo(raiz, estructura, contenidos),
        'patrones': patrones,
    }

    if args.json:
        print(json.dumps(informe, ensure_ascii=False, indent=2))
    else:
        imprimir(informe)
    return 0


if __name__ == '__main__':
    sys.exit(main())
