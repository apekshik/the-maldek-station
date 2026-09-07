# Maldek → H3 Max

Station-specific adaptation of the [H3-Max-Blender](https://github.com/gokayfem/H3-Max-Blender) reference-conditioning workflow. Upstream is cloned at `C:/Users/apek-anna/Developer/H3-Max-Blender`, inspected at commit `27d4962136019010b9a66b0552d1ae891ea5167b`. This directory is GPL-3.0-or-later; see `LICENSE`. The existing game and art files are not imported into upstream's ship/railway demo.

## Pipeline

**Latest mood pass: `refined-exterior-dark-fog-04`.** The shared mood now requests low-exposure night, denser drifting valley mist, indistinct forest/cliff detail and small warm light pools. The generated five-second review is darker than realism-03, with deeper lower-level shadows and more veiling mist. The original H3 response and silent review are both retained. This uses the same refined source and linework camera guide.

**Current preset: photographic reinterpretation.** `conditioning: motion_only` sends the Eevee video alone as a camera/layout guide, omitting the rendered stills to avoid anchoring their synthetic look. It requests quality prompt expansion and 768P output. Text defines the rainy blue-hour photographic treatment, natural materials, foliage and practical lighting. Set `conditioning` to `images_and_video` to restore the earlier three-reference pilot described below. The new test is stored in `refined-exterior-realism-02`.

**Best realism experiment so far: `refined-exterior-realism-03`.** Sending a simplified animated edge guide instead of the colored Eevee clip produced substantially more convincing cliff texture, moss, wet decking, glazing and practical lighting. The broad station arrangement and camera drift remain recognizable, but some cabin/window and construction details are reinterpreted. This is a visual concept variant, not a verified exact mesh render. The previous full-color-motion test (`realism-02`) stayed too close to the CG look.

To reproduce the linework conditioning for a new capture:

```powershell
python tools/h3max/lineguide.py --captures <eevee-capture-folder> --output <new-lineguide-folder>
python tools/h3max/pipeline.py generate --captures <new-lineguide-folder> --job <new-job-folder>
```

The prepared exterior line guide is `art/blender/h3max/outputs/refined-exterior-lineguide-01`. Use `--captures` explicitly to select it. `lineguide.py` removes source color/shading using a blurred grayscale edge pass while retaining camera timing. It saves fresh input hashes and preprocessing metadata. No new Cycles frames are required.

The configured source is now `art/blender/revision_04_refinement/millford_v2_refinement_04.blend`, with its matching refined night references. The initial `exterior-h3-01` result used revision 03 and is retained only as a connection test; use the `refined-` outputs for review.

1. Open the configured source file in a separate background Blender process.
2. Capture a material-bearing Eevee still and a five-second, 640 × 360 / 24 fps Eevee camera sweep. The pilot uses the accepted exterior camera path from the Cycles demo, slowed from 2.5 to 5 seconds. The source `.blend` is never saved.
3. Send **Image 1: geometry**, **Image 2: established night mood**, and **Video 1: camera-motion reference** to `minimax/h3-max/reference-to-video`.
4. Receive a five-second H3 video. Review architectural consistency and motion against the Eevee guide before generating other shots.

The pilot is one 480P request. `maldek.json` holds a shared mood, seed and four shot definitions; 768P is supported. Each command generates only its selected shot, with no watcher, automatic batch or automatic retry. H3 is a generative interpretation: prompts and reference video guide camera motion and geometry, but do not guarantee pixel-exact reproduction or cross-shot consistency.

The still and video capture use temporary daylight world/sun settings and suppress the source fog volume so the model can read the structure. The night image carries the intended atmosphere. Existing Cycles stills are reusable mood references; new Cycles frames are not required for this path.

## Local key

Fill in `FAL_KEY=` in **`tools/h3max/.env.local`**. This file is git-ignored. Do not paste the key into chat, commit it, or put it in Blender scene properties. A process environment variable named `FAL_KEY` takes precedence. The key is read only for the `generate` command, and is never included in plans or job metadata.

## Commands

Use Python with `imageio-ffmpeg` installed for capture; API submission uses the standard library. Blender 5.0.1 is supported locally without installing the upstream 5.1 UI extension.

From the station repository root:

```powershell
# Substitute your Python executable for python if it is not on PATH.
python tools/h3max/pipeline.py capture --captures art/blender/h3max/outputs/refined-exterior-eevee-01 --shot exterior
python tools/h3max/pipeline.py plan --captures art/blender/h3max/outputs/refined-exterior-eevee-01 --shot exterior
# Sends ONE paid generation request, after the key is configured:
python tools/h3max/pipeline.py generate --captures art/blender/h3max/outputs/refined-exterior-eevee-01 --shot exterior --job art/blender/h3max/outputs/refined-exterior-h3-01
```

The local bundled Python is `C:/Users/apek-anna/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. `--config` accepts a different scene configuration. Change `source_blend`, camera endpoints and mood references there as work progresses. `--env` supports a different local credential-file path.

Use a fresh capture folder and job folder each time. Capture writes image/video hashes; plan and generate reject modified input files. Generated outputs, server result metadata and rendered guide frames live under the git-ignored `art/blender/h3max/outputs/`.

If a request times out, inspect its `job.json` and the fal dashboard before doing anything else: it may have completed and incurred usage. The tool will not retry it. If `result.json` exists but downloading failed, use `download --job <same folder>` to recover the video without another inference request. Runs are not submitted until the key is present and `generate` is invoked.

## Validation

The refined exterior pilot completed successfully: 16.629 seconds for the API call, returning 124 frames at 24 fps (about 5.16 seconds), with nominal 480P output at 832 × 480. The original response is retained as `video.mp4`; `h3_review.mp4` is a silent five-second review copy. `eevee_vs_h3.mp4` shows Eevee on the left and H3 on the right, preserving each aspect ratio. Sampled frames retain the refined station/gondola layout; the output still follows the Eevee appearance quite closely, so stronger mood transfer remains an art-direction task. No claim of exact camera or mesh reconstruction is made.

Two requests were made in this setup: one revision 03 connection test already submitted before the source correction, and one refined revision 04 pilot. No automatic batches were submitted.

`python -m unittest discover -s tools/h3max -p test_pipeline.py` tests missing credentials, duplicate submission prevention, uncertain HTTP outcomes, MP4 payloads, and the prepared image/video reference roles. A real H3 generation still requires the local API key.

API schema verified against [fal reference-to-video documentation](https://fal.ai/models/minimax/h3-max/reference-to-video/api): image and video references are supported; reference clips must be 2–15 seconds, with combined video duration at most 15 seconds. Our pilot provides one five-second clip.

## Blender look-development panel

Installed locally as **Maldek H3 Look Development**. Open `art/blender/h3max/outputs/Maldek_H3_Workspace.blend`, a separate workspace based on the refined revision 04 model and its `02_Full_Shell` view layer. In any 3D View, press N and choose **Maldek H3**.

1. Adjust your view, then click **Use Current View**. This sets a 16:9 camera frame. If already looking through a camera, it keeps that camera. Check composition within the frame.
2. Start with **Current view · fast**, **Linework**, and **480p**. For camera movement choose **Subtle slide**, **Subtle approach**, or **Existing animation** and its source frame range.
3. Adjust Fog, Darkness, Warm / cool balance, Wetness, Interpretation, and Art direction. These become H3 prompt directions on the next generation; they are not live Blender atmosphere controls. Local viewport exposure is separate.
4. **Check Guide** captures locally without contacting fal. **Generate Preview** captures an isolated copy and submits one paid five-second H3 request. Capturing the scene copy briefly pauses Blender; the render and API request then run in a background process while you keep editing.
5. Select a result and click **Compare Previous / Selected**: selected above, previous below. Clips loop in Blender. After reopening the file, click Compare to restart playback. **Restore Selected Settings** restores that result's mood and generation controls, leaving the camera unchanged. Older imported clips have no panel settings.
6. **Save Look / Load Look** use the preset name field. **Refresh History** discovers completed runs after reopening Blender. Each run retains its scene snapshot, settings, guide, logs, and result in the ignored interactive output directory.

The camera and animation provide composition guidance, not guaranteed exact geometry or movement reproduction. Linework intentionally removes source shading so H3 can reinterpret the scene photographically. The current-view option supplies a still reference and requests a hold; use a motion mode for video guidance.

Credentials remain in the local ignored key file. Paths can be changed in Edit > Preferences > Add-ons > Maldek H3 Look Development. The add-on never automatically generates on slider edits or file load. If a request has an uncertain outcome, inspect the run's API job metadata before generating again.

Source: `tools/h3max/blender_addon/maldek_h3/`. Reinstall after source edits with Blender's background Python runner and `tools/h3max/install_addon.py`, then restart the dedicated workspace. The package includes its GPL license and uses the existing fal transport.

Validation: local still/linework capture and preset round-trip passed on the refined model; the original source filepath remained unchanged and no API job was created. The comparison layout and looping clips were checked in Blender 5.0.1. No new paid request was made while implementing this panel; the new panel's complete paid-generation path has not yet been exercised end to end.
