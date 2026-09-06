# Revision 04 — Windows starting point

The Windows baseline is verified. `millford_v2_detail_04.blend` is a separate starting copy of revision 03 configured for Cycles GPU rendering. **No geometry refinements have been made yet.** Revision 03 and the existing Unreal work are preserved.

## Baseline — September 6, 2026

- Blender 5.0.1; NVIDIA GeForce RTX 5070 Ti; driver 610.88; OptiX GPU only.
- Camera `CAM_R03_Platform_Rain`, view layer `02_Full_Shell`.
- 1400 × 930 pixels, 40 samples, denoising enabled, saved exposure −0.35.
- Render wall time: 6.274 seconds (one run, not a benchmark average).
- Peak sampled total GPU memory: 4290 MiB; includes other applications and is sampled once per second.
- No missing file-backed images. Render shows no pink materials.
- Visual comparison with revision 03's platform preview: framing, lighting, wet surfaces, forest and gondola appearance agree. Small sampling/denoising differences remain; this is not a pixel-identical comparison.
- Source SHA-256 verified unchanged after rendering.

Render: `audit/before/platform_rain_windows.png`. Settings, image checks and GPU memory samples: `audit/windows_baseline_report.json`. Console output: `audit-baseline.log`.

## Next modeling work

Follow `../WINDOWS_HANDOFF_AND_REFINEMENT_PLAN.md`: capture close-up neutral, grazing-light and night audit views before changing geometry. The baseline confirms the angular gondola, simple intersecting rail stock and broad unjointed platform surface remain the first subjects to refine. Start with one gondola corner/window, one railing span/base and a small platform patch; compare matching before/after views before propagating details.

The close-up audit, representative refinements, after-images and Unreal handoff are still pending.

To repeat only the baseline from the repository root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background art/blender/revision_03/millford_v2_night_03.blend --python art/blender/revision_04/scripts/windows_baseline.py
```
