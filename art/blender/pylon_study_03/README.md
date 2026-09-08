# Maldek pylon study 03 — wider taper and physical plausibility

This revision retains one central passenger lane and the weathered finish. The two legs have a wider stance and a stronger, continuous upward taper. It also repairs gaps in the previous study's visible mechanical load path.

## Shape

| Dimension | Study 02 | Study 03 |
|---|---:|---:|
| Foundation centre spacing | 9.2 m | 12.4 m |
| Crown leg centre spacing | 6.4 m | 8.5 m |
| Shaft base diameter | 2.10 m | 1.95 m |
| Shaft crown diameter | 1.42 m | 0.90 m |
| Head girder width | 7.7 m | 10.5 m |
| Working rope height at tower centre | 42.327 m | 42.327 m |

The base is slimmer than before but remains the thickest section. Triangular base fins replace rectangular blocks, making the foot transition less bulky while showing how it joins the anchor flange.

## Mechanical corrections

The main force path is now explicit:

**Rope → sheaves and axles → secondary equalizers → primary rocker/pin → central suspension member → overhead girder → tapered shafts → anchored base plates → buried foundations.**

- One central pinned suspension replaces the two ambiguous drop supports.
- Secondary pivot links and taller axle carriers connect the rollers to their equalizers.
- Maintenance deck hangers connect to actual outrigger brackets; the ladder transfer has a stringer and leg bracket.
- The upper hanger adapter uses a more substantial rectangular section. It remains a concept component on a copy of the approved cabin, not a production rig modification or specified grip.
- The passenger rope follows a gently curved roller bank and then sags between supports. The four return rollers now use the same 550 mm running diameter as the passenger rollers.
- Visible concrete pads are caps over modelled 6 m buried sockets, with additional anchor heads. Their depth is illustrative; no ground/rock capacity has been established.

## What was checked

`physics_review.json` and `scripts/physics_review.py` contain an order-of-magnitude statics calculation with explicit assumed values: 300 m level spans, 12 kg/m rope mass, 250 kN horizontal rope tension per run, an 1,800 kg loaded cabin, a 1.5 illustrative dynamic multiplier, and a 30 m/s wind case. These are not measured parameters of the current game route.

Under those assumptions, the shallow-sag approximation gives about 5.3 m unloaded midspan sag and 10.6 m with a stationary cabin at midspan. Two rope runs plus the illustrative dynamic cabin load yield about 97 kN of vertical load at a support before the tower's own weight. The visible rope sample uses the unloaded span profile; a cabin-dependent tension/sag solve is still required for a physically simulated moving route.

A first-order tapered-cantilever estimate includes steel self-weight, wind, an illustrative rope-force imbalance and a conservative gravity eccentricity term from the inclined legs. It omits frame action, second-order effects and connection flexibility. It is useful for scale and load-path decisions, **not a capacity check**.

The shallow-pad eccentricity screen fails: the visible slabs must not be interpreted as free-standing foundations for this tower. The buried sockets and anchor heads express the intended foundation type; their capacities remain unknown.

`clearance.json` records sampled mesh-intersection checks along the curved rope profile and with illustrative ±8° cabin body swing around its suspension pivot. This is a clearance study, not a certified operating swing limit or dynamic simulation.

## Remaining engineering inputs

Actual span lengths/elevations, rope construction/strength/fatigue properties, grip capacity, loaded carrier mass, operating/braking/wind cases, shell buckling, connections and soil/rock/anchor capacities are not established. Consequently, the result is a physically informed game asset, not a verified real-world ropeway design.

At Unreal integration, preserve the approved cabin body, fit the hanger and controller to the real route, survey footing elevations, recreate/bake the Blender weathering, and test passage under the actual motion rig. No live Unreal changes are included in this revision.

## Files

- `Maldek_Tapered_Central_Pylon.blend` — editable study with reference cabin and render cameras.
- `fbx/SM_Maldek_Tapered_Pylon.fbx` — tower only, including buried foundation geometry; origin at ground level between feet.
- `renders/01_full_pylon.png` — overall proportions.
- `renders/02_crosshead.png` — mechanical head and approaching cabin.
- `renders/03_base_detail.png` — tapered base and anchorage detail.
- `renders/04_front_clearance.png` — cabin in the central opening, with studio rope curves hidden to keep the foreground clear.
- `renders/05_hanger_detail.png` — upper hanger concept.
- `renders/06_night.png` — night study.
- `physics_review.json`, `clearance.json`, `validation.json` — assumptions, analytical screen and geometric verification.

## Sources

[LEITNER technical line brochure](https://www.leitner.com/fileadmin/userdaten/00-home/Ordner-Facelift/PDF_s_Logo_neu/Strecke/The_LEITNER_Line_.pdf): modular special towers, conical round-tube shafts and flange joints; manufacturer tube wall thickness examples informed the illustrative section range.

[University of Colorado structural analysis notes](https://ceae.colorado.edu/~saouma/files/Saouma-Structural-Analysis-Lecture-Notes.pdf): cable equilibrium and parabolic sag under load distributed over horizontal span. The actual material/rope parameters here remain assumptions.

[Doppelmayr mechanical course outline](https://service.doppelmayr.com/training/course-list/detail/mechanical-course-ropeways-with-dt-grips-76/): line structures, sheaves, rope, grips and their interaction are separate interacting systems. Our mesh clearance check does not validate those systems.
