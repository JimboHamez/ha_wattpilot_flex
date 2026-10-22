# Brand assets

These icon and logo images are the Home Assistant brand assets for the
`wattpilot_flex` integration. Since Home Assistant 2026.3, a custom integration can
ship its own images in a `brand/` directory, and Home Assistant serves them in
preference to its brands CDN. Older releases ignore this directory and take the
images from the
[home-assistant/brands](https://github.com/home-assistant/brands/tree/master/custom_integrations)
repository. That repository no longer takes new custom integrations, and it
holds these files only under `custom_integrations/wattpilot`, the domain before
the rename, so releases before 2026.3 show no icon for `wattpilot_flex`.

| File          | Dimensions | Purpose            |
|---------------|------------|--------------------|
| `icon.png`    | 256×256    | Square icon        |
| `icon@2x.png` | 512×512    | Square icon (hDPI) |
| `logo.png`    | 924×256    | Wide logo          |
| `logo@2x.png` | 1847×512   | Wide logo (hDPI)   |

To change the branding, update the images here; this directory is the only
copy that applies to the `wattpilot_flex` domain.
