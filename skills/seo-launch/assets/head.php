<?php
/**
 * The full <head>, shared by every page of a static site.
 *
 * Include it once per page:  <?php $titulo = '…'; $descripcion = '…'; $ruta = ''; include '../partials/head.php'; ?>
 *
 * Variables it expects before the include:
 *   $titulo       (required) the <title>
 *   $descripcion  (required) the meta description
 *   $ruta         (required) path from the root, '' for the home page
 *   $og_titulo    (optional) defaults to $titulo — the card usually drops the brand,
 *                 because og:site_name already prints it right below
 *   $og_desc      (optional) defaults to $descripcion
 *   $og_img       (optional) absolute URL, overrides the site-wide card image
 *   $og_img_alt   (optional) alt text for the card image
 *   $twitter_desc (optional) X truncates earlier than Facebook; sometimes a
 *                 shorter version is worth writing
 *   $keywords     (optional) Google has ignored these since 2009
 *   $jsonld       (optional) an already-formatted structured data block
 *
 * The URLs are absolute on purpose: Facebook, WhatsApp and X discard images
 * with a relative path. The base lives here, in one place.
 */

const BASE = 'https://example.com/';
const OG_IMAGEN = BASE . 'images/og-image.jpg';
const OG_IMAGEN_ALT = 'Describe the card image in one sentence.';
const SITIO = 'Site Name';

$url = BASE . ($ruta ?? '');
$ogTitulo = $og_titulo ?? $titulo;
$ogDesc = $og_desc ?? $descripcion;
$ogImagen = $og_img ?? OG_IMAGEN;
$ogImgAlt = $og_img_alt ?? OG_IMAGEN_ALT;
$twitterDesc = $twitter_desc ?? $ogDesc;

function attr(string $valor): string
{
    return htmlspecialchars($valor, ENT_QUOTES, 'UTF-8');
}
?>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title><?= attr($titulo) ?></title>
<meta content="<?= attr($descripcion) ?>" name="description"/>
<link href="<?= attr($url) ?>" rel="canonical"/>
<meta content="index, follow" name="robots"/>
<meta content="#0f2d52" name="theme-color"/>
<?php if (! empty($keywords)): ?>
<meta content="<?= attr($keywords) ?>" name="keywords"/>
<?php endif; ?>
<!-- An SVG favicon has no intrinsic size, so it draws sharp in the tab, in the
     bookmarks bar and at any density. iOS ignores it for the home screen — that
     is what the PNG below is for. -->
<link href="<?= BASE ?>images/logo-symbol.svg" rel="icon" type="image/svg+xml"/>
<link href="<?= BASE ?>images/apple-touch-icon.png" rel="apple-touch-icon" sizes="180x180"/>
<!-- Without this, iOS puts the whole <title> under the icon and cuts it. -->
<meta content="<?= SITIO ?>" name="apple-mobile-web-app-title"/>
<!-- Open Graph: Facebook, WhatsApp, LinkedIn -->
<meta content="website" property="og:type"/>
<meta content="es_MX" property="og:locale"/>
<meta content="<?= SITIO ?>" property="og:site_name"/>
<meta content="<?= attr($url) ?>" property="og:url"/>
<meta content="<?= attr($ogTitulo) ?>" property="og:title"/>
<meta content="<?= attr($ogDesc) ?>" property="og:description"/>
<meta content="<?= attr($ogImagen) ?>" property="og:image"/>
<meta content="<?= attr($ogImagen) ?>" property="og:image:secure_url"/>
<meta content="image/jpeg" property="og:image:type"/>
<!-- These must match the real file. A wrong value renders a cropped card and
     nothing reports an error. -->
<meta content="1200" property="og:image:width"/>
<meta content="630" property="og:image:height"/>
<meta content="<?= attr($ogImgAlt) ?>" property="og:image:alt"/>
<!-- X. summary_large_image is the one that shows the photo full width. -->
<meta content="summary_large_image" name="twitter:card"/>
<meta content="<?= attr($ogTitulo) ?>" name="twitter:title"/>
<meta content="<?= attr($twitterDesc) ?>" name="twitter:description"/>
<meta content="<?= attr($ogImagen) ?>" name="twitter:image"/>
<meta content="<?= attr($ogImgAlt) ?>" name="twitter:image:alt"/>
<?php if (! empty($jsonld)): ?>
<script type="application/ld+json">
<?= $jsonld ?>
</script>
<?php endif; ?>
<link href="<?= BASE ?>css/app.css" rel="stylesheet"/>
