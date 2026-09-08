# Scenic title captures

These are unmodified 1800x1000 Unreal captures copied from the working map:

- approach.png: art/unreal_handoff/revision12/forest_refine/final_confirmed/path.png
- parking.png: art/unreal_handoff/revision12/forest_refine/final_confirmed/parking.png
- cables.png: art/unreal_handoff/revision12/sensory_refine/views/bridge.png

The native Slate backdrop selects the left 66% of each capture to exclude the held flashlight, then crops to fill the window without stretching. It holds each view for 10 seconds and crossfades over 2 seconds. The controls remain stationary above a dark overlay. No live station scene is loaded for the menu.

DefaultGame.ini stages UI/Menu as NonUFS content on all targets. The game loads exactly these three relative filenames, retaining the transient textures through the game instance. Three BGRA8 frames require about 20.6 MiB before renderer overhead; their PNG files total about 7.3 MiB. Missing images fall back to the dark title background and produce a log warning.

These are development screenshots and can be replaced as the map evolves. Use matching framing or adjust the backdrop crop when replacing them. No Windows-specific texture cache is used.
