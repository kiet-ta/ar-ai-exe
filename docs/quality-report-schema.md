# Quality Report Schema

`quality_report.json` summarizes whether a shoe scan is visually usable. It is not a measurement certificate.

```json
{
  "overallScore": 78,
  "status": "completed",
  "inputVideos": ["side_orbit", "top_orbit"],
  "framesExtracted": {
    "side_orbit": 120,
    "top_orbit": 118
  },
  "framesSelected": {
    "side_orbit": 55,
    "top_orbit": 48
  },
  "rejectedFramesByReason": {
    "invalid": 0,
    "dark": 4,
    "blurry": 22,
    "duplicate": 95,
    "over_limit": 0
  },
  "lightingScore": 82.5,
  "blurScore": 76.0,
  "coverageScore": 57.2,
  "textureConfidence": "medium",
  "geometryConfidence": "medium",
  "scaleConfidence": "medium",
  "warnings": [
    "Frame coverage is low; reconstruction may miss shoe areas."
  ],
  "recommendation": "Use for visual shoe similarity review; not for industrial measurement."
}
```

## Field Notes

- `overallScore`: 0-100 score weighted toward texture/coverage usefulness.
- `inputVideos`: expected to include `side_orbit` and `top_orbit`.
- `framesExtracted`: raw frames extracted by FFmpeg per pass.
- `framesSelected`: frames kept after blur, darkness, duplicate, and limit filtering.
- `rejectedFramesByReason`: aggregate rejected frame counts.
- `textureConfidence` and `geometryConfidence`: `low`, `medium`, or `high`.
- `scaleConfidence`: MVP defaults to `medium` because the system prioritizes visual similarity over industrial measurement accuracy.
