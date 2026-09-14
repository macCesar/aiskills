# Laravel versions and where things live

The sweep supports Laravel 8 through 13. What changes across that range for security work is mostly *where* things are configured, not what a vulnerability looks like. Detect the structure from the files, not from the version number: a project upgraded from 10 to 11 may still carry the old `app/Http/Kernel.php` layout.

## Contents

- Detecting the structure
- Laravel 8–10: `app/Http/Kernel.php`
- Laravel 11–13: `bootstrap/app.php`
- Laravel 13 renames
- Laravel 3 and 4
- Things that are the same across 8–13

## Detecting the structure

| Evidence | Structure |
| --- | --- |
| `bootstrap/app.php` contains `->withMiddleware(` | 11+ layout |
| `app/Http/Kernel.php` exists | 8–10 layout (also 5–7) |
| `laravel/core.php` or `paths.php` in the root | Laravel 3 |
| `bootstrap/start.php` and `app/start/` | Laravel 4 |

The script prints this as `Estructura`. The version comes from `laravel/framework` in `composer.lock`, falling back to the constraint in `composer.json`.

## Laravel 8–10: `app/Http/Kernel.php`

- **Global and group middleware** are the `$middleware` and `$middlewareGroups` arrays; route middleware aliases are `$routeMiddleware` in 8–9 and `$middlewareAliases` in 10, where projects upgraded from 9 often still carry `$routeMiddleware`; search for both.
- **Trusted hosts:** the `\App\Http\Middleware\TrustHosts::class` line in `$middleware`. It ships commented out; commented means the Host header is not validated.
- **CSRF exclusions:** `protected $except` in `app/Http/Middleware/VerifyCsrfToken.php`.
- **Route groups for the admin area** are usually wired in `app/Providers/RouteServiceProvider.php`, so the middleware protecting `/admin` may be declared there rather than in `routes/web.php`.

## Laravel 11–13: `bootstrap/app.php`

- **Middleware** is configured inside `->withMiddleware(function (Middleware $middleware) { ... })`, including aliases (`$middleware->alias([...])`) and groups.
- **Trusted hosts** (verified against the 13.x docs):

  ```php
  ->withMiddleware(function (Middleware $middleware): void {
      $middleware->trustHosts(at: ['^example\.com$']);
  })
  ```

- **Route files** are registered in `->withRouting(...)`; there is no `RouteServiceProvider` by default, so look there for how `/admin` gets its middleware.

## Laravel 13 renames

- `VerifyCsrfToken` became `PreventRequestForgery` (`Illuminate\Foundation\Http\Middleware\PreventRequestForgery`). The old name remains as an alias, so both can appear in a project. Search for both when checking CSRF exclusions. [source: laravel.com/docs/13.x/upgrade]
- 13.x also documents origin-only verification: `$middleware->preventRequestForgery(originOnly: true)`. [source: laravel.com/docs/13.x/csrf]

## Laravel 3 and 4

Out of scope. Laravel 3 predates Composer-based structure entirely (`application/`, `laravel/`, `paths.php`); Laravel 4 uses `app/start/`, `app/filters.php` and `app/routes.php`. The patterns in this skill assume Eloquent, middleware and the 5+ request lifecycle, so running them on these projects would report little and imply much. Report the version, say the sweep does not apply, and recommend planning the migration.

## Things that are the same across 8–13

- **Reset link URL:** `ResetPassword::createUrlUsing(fn ($user, string $token) => ...)` in a service provider's `boot()` controls the URL in the default password-reset notification. Verified working on Laravel 10.
- **Encrypted casts:** `'secret_field' => 'encrypted:array'` (or `encrypted`, `encrypted:object`). In 8–10 casts are the `$casts` property; the 13.x docs declare them in a `casts()` method. The column must be `TEXT` or larger, the value cannot be searched in SQL, and existing plain-text rows must be migrated before switching the cast, or reading them throws a decryption error. [source: laravel.com/docs/13.x/eloquent-mutators]
- **Upload validation:** `mimes` and `mimetypes` guess the type from the file's contents and do not check the extension the client sent. The 13.x docs add an `extensions` rule for the client extension and say to pair it with `mimes`. [source: laravel.com/docs/13.x/validation] In versions where `extensions` is not available, compare `getClientOriginalExtension()` against an allowlist yourself.
- **Stored file names:** prefer `hashName()` and `extension()` (derived from the MIME type) over `getClientOriginalName()` and `getClientOriginalExtension()`. [source: laravel.com/docs/13.x/filesystem]
- **Named rate limiters:** `throttle:N,1` keys by user or IP without the route, so every route using that form shares one counter. A `RateLimiter::for('name', ...)` limiter keys on its name plus whatever `->by()` returns. Verified on Laravel 10.
