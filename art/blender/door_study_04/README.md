# Keyed station door study

Editable Blender design for the seven standard doors, built from the approved frosted-glass door. The digital keypad variant remains separate. Warm worn brass, a rounded pear-shaped service-key head, a real ring hole, five blade cuts, milled side grooves, stamped identity and a recessed rotating cylinder keep the design practical and period-appropriate.

Open `Maldek_Keyed_Door.blend` and play frames 1–120 at 24 fps: key ready, insertion, 90-degree turn, return, withdrawal, then door opening. The cylinder, key and latch have separate animation controls. No hand animation is included. The old cylinder/painted slot is removed; both opaque door layers have a real cylinder bore. This study does not change the current Unreal door meshes or add an inventory requirement.

Initial gameplay intent: make the matching key available automatically. Later, key possession can gate this same animation without redesigning the mechanism. Each door can receive a key identifier when integrated; that inventory system is not implemented in this Blender study.

Run `scripts/build_key_lock.py` with Blender to regenerate the editable source and five review renders, then `scripts/verify_key_lock.py` to reopen and verify the evaluated parts and animation timing. The existing game’s interaction prompt is updated separately to a shared warm brass/ink palette with sharp double rules in `StationInteractionStyle.h`.
