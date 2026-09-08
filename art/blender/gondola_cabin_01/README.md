# Gondola cabin and sliding-door study

Editable Blender design for review. **Not installed in Unreal.** The station route, terminal machinery, live cabin materials and dimmed lamps are unchanged.

Open `Maldek_Gondola_Cabin.blend`. Press Space to play the 16-second review timeline with the packed recorded opening/closing sounds. The saved view shows the open cabin. Cameras provide an exterior view, door close-up, interior, uncovered track and inside view of the closed doors. The track close-up temporarily hides the removable guard to show the mechanism; the delivered model keeps it fitted.

The retained shell is derived from `visual_fidelity_07/Maldek_Station_Cleanup.blend`, with its world transforms flattened before moving to cabin-local coordinates. Floor top is Z=0; the entrance faces -Y. The original overall cabin envelope and 1.20 × 2.10 m structural entrance remain. Two glazed leaves slide 635 mm in opposite directions, outside the old jambs. The former handles and short decorative track are replaced with outboard handles, a supported guide, captive rollers, opposed racks, central pinion, guarded gearmotor, limit switches, soft meeting edges and threshold hardware.

The cabin pass adds shaped olive seat cushions and backrests, piping, under-seat heater grilles, ribbed floor finish, boarding poles, rail supports, assistance and emergency-release fittings, period service signage, conduit and guards around the existing lamp faces. These fittings are a visual design study, not mechanically certified passenger hardware.

## Timeline

| Frames | Action |
|---|---|
| 1–60 | Closed cabin approaches and stops |
| 60–78 | Settling pause |
| 78–162 | Recorded opening, 3.5-second slide |
| 162–264 | Boarding dwell (shortened for this review) |
| 264–306 | Recorded closing, 1.75-second slide |
| 306–348 | Closed/latch hold |
| 348–384 | Departure with doors shut |

`GC_CABIN_APPROACH_ROOT`, `GC_SLIDE_LEFT`, `GC_SLIDE_RIGHT` and `GC_DRIVE_PINION` separate cabin movement, leaf translation and drive rotation. Roller controls follow the leaves. Source objects, new fixed parts, moving leaves, interior fittings and review lights are organized into separate collections.

## Later integration

The current game controller lives in `GondolaSystem.cpp`. Installation must preserve its actual route and bridge states: stop first, deploy the Maldek landing, then open. Closing must detect doorway occupancy and reopen or hold; route movement and gangway retraction must wait for closed/latch confirmation. The Blender animation is a presentation sequence, not runtime logic or proof of capsule collision. Retain the existing lamp material instances and 12-lumen local lights. Test both terminals, interrupted departure, occupied doorway/bridge and the real player capsule before enabling travel.

The original shell contains legacy layered geometry. This pass cuts the old solid entry-wall cores behind both small front windows so the retained glazing is see-through. New leaves have real window openings and distinct frame/glass/seal surfaces. The removed handles, track and sill must not be left behind when installing replacements. Source validation and saved-file checks are recorded in `verification.json`.

The Blender studio includes separate warm interior inspection lights for reviewing the fittings; these are not a change to game lighting and should not be exported. The two retained lamp faces use a 0.6-strength diffuser in this study.

Rebuild with `scripts/build.py`; validate the saved file with `scripts/verify.py`. Audio provenance and reproducible edits are in `art/audio/gondola_doors`.

## References

- [LEITNER Symphony cabin brochure](https://www.leitner.com/fileadmin/userdaten/00-home/Ordner-Facelift/Brosch%C3%BCren_NEU/Symphony-10-EN.pdf): paired sliding-door layout and passenger access; interpreted in the existing older station style.
- [Tulsa Skyride history](https://www.tulsaskyride.org/history-of-the-tulsa-skyride/): older enclosed cabin interiors and bench arrangement.
- [Recorded train opening](https://freesound.org/people/iamaviolin/sounds/439499/) and [closing](https://freesound.org/people/iamaviolin/sounds/439494/) by iamaviolin, CC0.
- [Old door on a metal track](https://freesound.org/people/wlabarron/sounds/509114/) by wlabarron, CC0; alternative audition.
