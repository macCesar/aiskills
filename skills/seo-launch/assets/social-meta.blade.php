{{--
  Every tag a page needs to be indexed and to render a card when its link is shared.

  Put it in the layout's <head>, after the charset and viewport:

      <x-social-meta
          title="Freight and warehousing in Reynosa | Acme"
          description="…"
          :image="$nota?->imagen_url"
          type="article" />

  Per-page values arrive as props; the site-wide ones come from config. The
  fallbacks are what make it safe to drop into a layout: a page that passes
  nothing still emits a complete, valid block.

  Add to config/app.php (or a dedicated config file):

      'site_name'  => env('APP_NAME'),
      'og_image'   => env('APP_URL') . '/images/og-image.jpg',
      'og_locale'  => 'es_MX',
      'theme_color' => '#0f2d52',
--}}

@props([
    'title' => null,
    'description' => null,
    'url' => null,
    'image' => null,
    'imageAlt' => null,
    'type' => 'website',
    'locale' => null,
    'robots' => 'index, follow',
    'publishedAt' => null,
    'modifiedAt' => null,
])

@php
    $siteName = config('app.site_name', config('app.name'));
    // url()->current() drops the query string, which is what a canonical wants:
    // ?page=2&utm_source=… would otherwise mint a distinct URL per visit.
    $canonical = $url ?? url()->current();
    $metaTitle = $title ?? $siteName;
    $metaDescription = $description ?? config('app.description', '');
    // Absolute URL on purpose: Facebook, WhatsApp and X discard a relative
    // image path — no error, no thumbnail.
    $metaImage = $image ? (str_starts_with($image, 'http') ? $image : url($image)) : config('app.og_image');
    $metaImageAlt = $imageAlt ?? $metaTitle;
@endphp

<title>{{ $metaTitle }}</title>
<meta name="description" content="{{ $metaDescription }}">
<link rel="canonical" href="{{ $canonical }}">
<meta name="robots" content="{{ $robots }}">
<meta name="theme-color" content="{{ config('app.theme_color', '#0f2d52') }}">

{{-- An SVG favicon has no intrinsic size and draws sharp at every size iOS,
     Safari and Chrome ask for. iOS still needs the PNG for the home screen. --}}
<link rel="icon" type="image/svg+xml" href="{{ asset('images/logo-symbol.svg') }}">
<link rel="apple-touch-icon" sizes="180x180" href="{{ asset('images/apple-touch-icon.png') }}">
<meta name="apple-mobile-web-app-title" content="{{ $siteName }}">

{{-- Open Graph: Facebook, WhatsApp, LinkedIn --}}
<meta property="og:type" content="{{ $type }}">
<meta property="og:locale" content="{{ $locale ?? config('app.og_locale', 'es_MX') }}">
<meta property="og:site_name" content="{{ $siteName }}">
<meta property="og:url" content="{{ $canonical }}">
<meta property="og:title" content="{{ $metaTitle }}">
<meta property="og:description" content="{{ $metaDescription }}">
<meta property="og:image" content="{{ $metaImage }}">
<meta property="og:image:secure_url" content="{{ $metaImage }}">
<meta property="og:image:type" content="image/jpeg">
{{-- These must match the real file: they exist so the client can lay out the
     card before downloading it. --}}
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{{ $metaImageAlt }}">

@if ($type === 'article' && $publishedAt)
    <meta property="article:published_time" content="{{ $publishedAt->toIso8601String() }}">
    @if ($modifiedAt)
        <meta property="article:modified_time" content="{{ $modifiedAt->toIso8601String() }}">
    @endif
@endif

{{-- X. summary_large_image is the one that shows the photo full width. --}}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ $metaTitle }}">
<meta name="twitter:description" content="{{ $metaDescription }}">
<meta name="twitter:image" content="{{ $metaImage }}">
<meta name="twitter:image:alt" content="{{ $metaImageAlt }}">
