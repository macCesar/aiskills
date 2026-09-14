# Pattern catalog

One section per ID the script prints. Each says what makes a match a real finding, what makes it a false positive, and how to fix it at the root. Read the section before judging its matches: most IDs are deliberately broad, because a missed vulnerability costs more than a match discarded in five seconds of reading.

These patterns come from vulnerabilities confirmed in production Laravel applications by a multi-agent scan and then fixed. The script was validated against the pre-fix snapshot of that application: it flagged every confirmed location, and the counts dropped when run against the fixed tree.

## Contents

Project-level checks: AUTHZ-MIDDLEWARE · SHARED-PROVIDER · HOST-HEADER · IMAGE-LIMIT · CORS-WILDCARD · APP-DEBUG

Line patterns: SQL-RAW · MASS-ASSIGN · ROLE-FROM-REQUEST · AUTH-ENTRY · RESET-ENUM · RESET-URL · SSRF · UPLOAD-NAME · PATH-FROM-INPUT · XSS-BLADE · EXEC · ENV-OUTSIDE-CONFIG · SECRET-FALLBACK · GET-DESTRUCTIVE · API-MUTATION · CSRF-EXCEPT · LOG-SECRETS

---

## AUTHZ-MIDDLEWARE — custom authorization middleware

**Flagged when** a file in `app/Http/Middleware/` reads the user and has two or more `return $next(...)` exits.

**Real when** any exit lets the request through without having established that the user may be there. The classic form looks up a permission record (a section, a module, a menu row) from the URL and, when the lookup finds nothing, calls `$next` "because it might be a special route". Every admin page that nobody registered then opens to every logged-in account. Also real: an unconditional bypass for one path (`if ($request->segment(2) === 'dropzone') return $next($request);`) placed before the role check.

**False positive when** each `$next` is reached only after a check that denies by default, or the extra exits are for super-admins identified by something the user cannot set.

**Fix.** Deny by default: when nothing matches, redirect or `abort(403)`, and let only the top role through. Put an explicit gate on the admin route group so accounts that are not staff never reach it, whatever else the middleware does. Before shipping, list the roles that actually use the panel in the database, so the change does not lock out the owner.

## SHARED-PROVIDER — several guards on one users table

**Flagged when** `config/auth.php` has more than one session/token guard pointing at the same provider.

**Real when** one of those guards is reachable by public self-registration (an API `register` endpoint, a mobile app sign-up) and another guards the admin panel. The public account then logs in to the panel with the same password. Check `AUTH-ENTRY` matches for `User::create` in API controllers.

**False positive when** every guard on that provider serves staff only, or registration is closed.

**Fix.** Keep public accounts in their own model and table with their own provider. When that is not possible now, reject non-staff roles in the panel login (`LoginRequest::authenticate()` after `Auth::attempt`) and in the admin middleware.

## HOST-HEADER — reset links built from the request host

**Flagged when** the project sends password resets, never calls `ResetPassword::createUrlUsing` or `URL::forceRootUrl`, and trusted hosts are not enabled.

**Real when** the web server passes arbitrary `Host` headers to Laravel (shared hosting and default vhosts usually do). An attacker requests a reset for the victim's email with `Host: attacker.example`; the genuine email then carries a link to the attacker's domain with a valid token, which leaks when the victim or a mail link scanner opens it.

**False positive when** the server pins the host upstream (a strict vhost that rejects unknown hosts) — say so as an assumption, since it is not visible in the code.

**Fix.** Build reset URLs from `config('app.url')`: `ResetPassword::createUrlUsing(...)` in `AuthServiceProvider::boot()`, and `rtrim(config('app.url'), '/') . route(..., absolute: false)` in custom notifications (see `RESET-URL`). Enabling trusted hosts also works but rejects every domain not listed, so check which domains the site serves first. Syntax per structure in `versions.md`.

## IMAGE-LIMIT — Glide without a size cap

**Flagged when** a file calls `ServerFactory::create` without `max_image_size`.

**Real when** the manipulation parameters come from the query string (`request()->all()`). `?w=30000&h=30000` makes GD try to allocate gigabytes per request; a handful in parallel exhausts PHP workers.

**Fix.** Set `max_image_size` to the largest legitimate output, and whitelist or clamp the parameters passed to Glide. Glide URL signatures remove the problem entirely where the URLs are generated server-side.

## CORS-WILDCARD — any origin with credentials

**Real when** `allowed_origins` is `['*']` and `supports_credentials` is true: any site can make authenticated requests with the user's cookies. **Fix:** list the real origins.

## APP-DEBUG — debug mode on

Flagged from the local `.env`, which is usually not production's. **Real** only if production has it; ask or check the server rather than assuming. With debug on, error pages expose code, queries and configuration.

---

## SQL-RAW — raw SQL with interpolated input

**Flagged when** `whereRaw`, `selectRaw`, `orderByRaw`, `DB::raw`, `DB::select` and similar receive a double-quoted string containing `$` or a string concatenated with `. $`.

**Real when** the variable carries anything a request can influence, however indirectly (a search term, a sort column, a model attribute an admin typed). `e()` and `htmlspecialchars()` are HTML escaping: they leave the backslash untouched, and in MySQL's default mode a trailing `\` escapes the closing quote.

**False positive when** the interpolated value is a constant or a value the code produced itself (an integer cast, a whitelisted column name).

**Fix.** Bind every value: `->whereRaw('MATCH(name) AGAINST(? IN BOOLEAN MODE)', [$term])`, `->selectRaw('..., MATCH(...) AGAINST(?) AS score', [$term])`. Column names cannot be bound — validate them against an allowlist. Fix every match of the same shape, not only the reported one. MySQL full-text in boolean mode rejects stray operators (`+ - < > ( ) ~ * " @`) with a parse error even when bound; strip them from text that is not a user's deliberate query. Test against MySQL or MariaDB, since SQLite has no `MATCH ... AGAINST`.

## MASS-ASSIGN — the whole request into a model

**Real when** `create($request->all())` / `update($request->all())` targets a model whose `$fillable` includes, or whose `$guarded = []` allows, a column that grants something: role, owner id, verified flag, price, balance.

**False positive when** `$fillable` lists only harmless fields, or the request was validated and `$request->validated()` would be the same set.

**Fix.** Use `$request->validated()` or an explicit `only([...])` of harmless fields; keep privilege columns out of `$fillable` and set them explicitly after an authorization check.

## ROLE-FROM-REQUEST — privilege taken from input

**Real when** a role, admin flag or permission list from the request is saved without checking that the acting user may grant it. An administrator who can create a webmaster, or edit their own role, is a privilege escalation even if the form hides the option — the server never re-checks what the dropdown filtered.

**Fix.** Validate the value server-side against the actor's level (`min:` on a numeric role, or an allowlist), refuse changes to one's own role, and protect the top account from edits by lower roles in `update()`, not only in `edit()`.

## AUTH-ENTRY — who can obtain a session

Not a vulnerability by itself: a map of the doors. For each match, answer two questions: who can reach it without an account (registration, social login, token creation), and what that account can then open. Pair with `SHARED-PROVIDER` and `AUTHZ-MIDDLEWARE`; the damaging finding is the combination.

Also check that login, registration and password-reset routes carry a throttle.

## RESET-ENUM — forgot-password tells whether the account exists

**Real when** the response differs (status versus validation error) for registered and unknown emails, on a route without throttling. It lets anyone confirm which emails have accounts, which feeds credential stuffing and the `HOST-HEADER` attack.

**Fix.** Return the same message whatever the broker status, and add a throttle to the route.

## RESET-URL — token links in notifications and mail

**Real when** `route()` or `url()` builds an absolute URL containing a token inside a notification or mailable that is sent during the request, and nothing pins the root URL (see `HOST-HEADER`).

**Fix.** `rtrim(config('app.url'), '/') . route('name', [...], false)`.

## SSRF — the server fetches a URL it was given

**Flagged when** `file_get_contents`, `fopen`, `curl_init`, `getimagesize`, `Http::get/post`, or a Guzzle-style `->get($url)` receives a variable.

**Real when** the URL or path comes from a request, or from a record a low-privilege user can edit (a monitored-site URL, a webhook, an avatar URL, an Open Graph preview). The server then reaches the cloud metadata endpoint, localhost-only services and the internal network; even a blind fetch leaks through status, timing, or a content-match flag. `file_get_contents` also reads local files when given a path.

**False positive when** the URL is a constant, built from configuration, or a model's own public asset path.

**Fix.** Before fetching: require `http`/`https` via `parse_url` (not a substring test), reject credentials in the URL, resolve the host and reject private, loopback, link-local and reserved IPs (`filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)` over every A and AAAA record). Validate redirects too: with Laravel's HTTP client pass `withOptions(['allow_redirects' => ['max' => 5, 'on_redirect' => fn ($req, $res, $uri) => ...]])` and throw when the target fails the same check; with streams, set `follow_location` to 0. Put the check in one helper and call it from every match. Verify the helper with both an internal URL and a public one — a check that rejects everything also passes a negative test.

## UPLOAD-NAME — the client decides the file name or directory

**Real when** `getClientOriginalName()` or `getClientOriginalExtension()` becomes the stored name, or the storage directory comes from the request. Combined with no authorization on the upload route, an attacker writes `x.php` or `x.html` under the public disk (stored XSS on the site's origin, or code execution if PHP runs there) or overwrites existing files another feature serves.

**False positive when** the name is only displayed or logged, or the directory is built server-side from a validated model.

**Fix.** Validate the directory against an allowlist or derive it from the validated record; validate type with `mimes` and the client extension separately (see `versions.md` — `mimes` alone does not check the extension that `storeAs` will use); prefer `hashName()`. When the original name must be kept (numbered assets, for instance), keep only `[A-Za-z0-9._-]`, drop the client extension and append the validated one.

## PATH-FROM-INPUT — a filesystem path built from input

**Real when** a request value or route parameter reaches `storage_path("...{$param}")`, `Storage::delete`, `response()->download`, `unlink` or a recursive delete without validation. A `..` segment escapes the intended directory; on a delete that is data loss.

**False positive when** the value is a model attribute produced by the application (a slug generated by `Str::slug`), or validated against a strict pattern first. The script already skips `{$model->attribute}` interpolation.

**Fix.** Validate the parameter against a strict pattern (`/^[a-z0-9-]+$/`) or resolve it to a record first and use the record's own path.

## XSS-BLADE — unescaped output

**Flagged when** `{!! ... !!}` appears in a view (common framework helpers are skipped).

**Real when** the value can contain HTML from someone other than a trusted editor: user profiles, comments, form submissions, data synced from third parties, query-string echoes. Rich text that only staff edit is lower risk but still worth sanitizing on save if staff accounts are many or loosely controlled.

**False positive when** the value is generated by the application (a rendered component, `json_encode` into a script with the correct flags, a trusted translation string).

**Fix.** Use `{{ }}`; when HTML is required, sanitize it on save with an allowlist sanitizer rather than escaping on output selectively.

Expect many matches in content-heavy sites. Triage by where the variable comes from, report the ones fed by untrusted input, and summarize the rest in one line.

## EXEC — commands, eval, unserialize

**Real when** the variable carries any input. `unserialize()` on user data enables object injection through the framework's own classes. **Fix:** remove it; for commands use `Symfony\Component\Process\Process` with an argument array, for data use JSON.

## ENV-OUTSIDE-CONFIG — `env()` read from application code

**Real when** the project runs `php artisan config:cache` in production (check the deploy notes or `bootstrap/cache/config.php` on the server): cached configuration makes `env()` return `null` outside `config/`, silently. Combined with a default value (`SECRET-FALLBACK`) the code then runs with the hard-coded default.

**Fix.** Move the value into a `config/*.php` file (`'key' => env('X')`) and read `config('file.key')`.

## SECRET-FALLBACK — a secret with a literal default

**Real** almost always. `env('DOWNLOAD_SECRET', 'change-me')` means that whenever the variable is missing — a new server, a cached config — every signature, token or encryption made with it uses a value published in the repository.

**Fix.** No default. Read it through `config()` and fail loudly (`abort(500)` or an exception at boot) when it is empty. Keep the same variable name so existing signed values stay valid.

## GET-DESTRUCTIVE — state changes on GET

**Real when** the route deletes or changes data. GET is not CSRF-protected, and link prefetchers, crawlers and `<img src>` on another site can trigger it for a logged-in user. **Fix:** `DELETE`/`POST` with the form's CSRF token.

## API-MUTATION — writing routes in `routes/api.php`

A map, like `AUTH-ENTRY`. For each writing route, confirm it sits inside an authentication middleware or has a reason to be public, and that public ones have a throttle and do nothing destructive. Unauthenticated cache-clearing, file-deleting or configuration endpoints left over from debugging are the usual real findings here.

`throttle:N,1` keys by user or IP without the route, so all routes using it share one counter (see `versions.md`). A tight limit on one route can then block another; prefer named limiters for account endpoints.

## CSRF-EXCEPT — routes excluded from CSRF

**Real when** an excluded route is used by browsers with a session cookie. Webhooks called server-to-server are the legitimate case; check that those verify a signature instead.

## LOG-SECRETS — logs that dump headers or the whole request

**Real when** it logs `Authorization`, `Cookie`, session or API tokens, or passwords from `$request->all()`. Log files are read by more people and systems than the database. **Fix:** log only the specific, non-secret fields needed.
