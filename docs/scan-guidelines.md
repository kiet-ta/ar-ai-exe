# Shoe Scan Guidelines

## Goal

Capture enough visual coverage for the backend reconstruction pipeline to create a textured shoe model for visual customization.

## Required MVP Capture

- Pass 1: side orbit, 360 degrees around the shoe at side height.
- Pass 2: top-angle orbit, 360 degrees at roughly 30-45 degrees from above.
- Do not scan the bottom sole for the MVP.
- Keep the full shoe inside the overlay guide.
- Record each pass for 30 to 60 seconds.
- Move around the shoe slowly and avoid motion blur.
- Keep lighting bright and even.
- Use a plain background.
- Include a scale reference such as A4 paper, ruler, or printed marker.

## Metadata to Collect

```json
{
  "shoe": {
    "sizeSystem": "EU",
    "size": "42",
    "side": "left",
    "type": "sneaker",
    "material": "canvas",
    "condition": "used"
  },
  "measurements": {
    "lengthCm": 27.0,
    "widthCm": 9.5
  },
  "scanSetup": {
    "calibrationReference": "A4 paper",
    "lighting": "bright",
    "background": "plain"
  },
  "customizationGoal": [
    "change_color",
    "add_sticker",
    "add_text"
  ]
}
```

## MVP Limits

The mobile app should only capture and upload video plus metadata. Reconstruction happens on the backend. The MVP is shoe-only and should not be treated as a generic object scanner.
