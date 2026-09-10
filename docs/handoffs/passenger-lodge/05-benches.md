# Handoff 5 — picnic tables and matching benches

Implement this package after reading [shared-contract.md](shared-contract.md).

Output: `art/blender/passenger_lodge_seating_01/`; asset collection prefix: `PLS_`.

Own the six picnic-style tables and twelve matching benches as one coherent furniture kit. Include the tables so their construction, finish and proportions match the benches. Do not own the kitchen counter, shelving, lost-property cubby or locker bank.

Inspect the actual source pieces before replacement. Lodge 03 replaces original table tops and bench seats with individual planks in `PL03_Furniture_Details`, while the leg/support proxies remain in `PL02_Fitted_Lodge_Geometry`. Names begin `FIT_Table_` and `FIT_Bench_`; enumerate exact objects rather than assuming each assembly is in one collection. Remove every replaced component in the fitted review copy, including the material-pass planks, without affecting unrelated furniture details.

Preserve six table positions and two benches per table. Nominal table top: 1.8 × 0.8 m, upper surface 0.81 m above the lodge floor. Bench seat: 1.8 × 0.35 m, upper surface 0.51 m above the floor. These are existing mockup dimensions, not ergonomic certification: check seat height, table clearance and knee space, and document any modest proposed correction. Preserve the overall seating-group footprints and public circulation; do not move the six groups to make a larger design fit.

Build credible timber construction: individual planks with finished edges, end grain, slight board variation, supporting rails, legs, cross-bracing and appropriate bolts/washers or joinery. Replace the current solid rectangular support blocks with a believable picnic-furniture structure. Use warm aged pine with restrained metal hardware; painted steel support details may echo the station where appropriate. Avoid sharp splinters, arbitrary damage and excessive decorative hardware.

Create a reusable base table and bench with a few subtle material/wear variations. Use linked mesh instances where suitable, while keeping the six fitted groups identifiable. Add restrained rounded wear on seat edges, small scratches and occasional repair details. Leave surfaces mostly clear: narrative props, cups and clues belong to later dressing. Do not build a different bespoke mesh for every board merely to add randomness.

Verify seated proportions using a temporary human-scale reference, useful knee/foot space, stability of the support arrangement, and walking clearance around all six groups. The seated figure is review context, not a shipped character asset. Preserve the central entrance-to-platform route and access to the service counter, lockers and restroom hallway.

Deliver an isolated table/bench assembly view, underside construction close-up, a player-height seating view, and a fitted overview showing all six groups. Include exact replacement names, group transforms, dimensions, material slots, mesh/instance counts and saved/reopened topology checks. No sitting animation or Unreal interaction implementation is required.
