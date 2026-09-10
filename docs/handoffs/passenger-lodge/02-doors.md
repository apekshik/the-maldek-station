# Handoff 2 — public and staff lodge doors

Implement this package after reading [shared-contract.md](shared-contract.md).

Output: `art/blender/passenger_lodge_doors_01/`; asset collection prefix: `PLD_`.

Own three assemblies: arrival-court main door, gondola-facing public exit, and coffee-annex staff door. Bathroom entrance doors and stall doors belong exclusively to the restroom task.

Start by inspecting `art/blender/door_study_01/README.md`, `door_study_03/README.md` and `door_study_04/README.md`, plus applicable R12 door repair evidence in `art/MESH_AUTHORING.md`. Reuse the established frosted upper-glass and practical keyed-door design language where it fits; do not edit those studies or mechanically rescale hardware.

Confirm actual openings: public doors have nominal 1.2 × 2.3 m clearance, staff opening 1.0 × 2.2 m. Local layout public X=6.4–7.6 at depth 0 and 11.02; staff doorway lies in coffee east wall at local X=4.82, depth 14–15. Use the shared coordinate mapping and inspect the fitted source, including new exterior cladding.

Model leaf, glazing, frame/reveal, seals, hinges, handles, key cylinder and appropriate threshold. Separate moving components with correct hinge axes. Show closed, partly open and fully open poses. Choose swing directions from actual circulation: protect grating routes, coffee work space, queue and narrow arrival court. Record the rationale and clearance rather than assuming one swing direction for every door.

No digital keypad is requested for these new lodge doors. Control retains its independent existing keypad door. Preserve the future interaction separation: a leaf pivot and keyed hardware ready for later logic, not a newly implemented game mechanic.

Deliver both-side close-ups and source-fitted swing views, exact pivots/transforms, clearance evidence and opening-specific wall/cladding patches. Keep coffee staff-door dimensions fixed so the kitchen task can proceed independently.
