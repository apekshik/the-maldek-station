# Passenger lodge: seven parallel modeling handoffs

These handoffs are ready to give to seven separate Codex tasks. They authorize Blender modeling and review packages, not edits to the shared master scene or Unreal integration. Multiple Blender processes can run at once, each with its own output file. Stagger heavy renders if memory/GPU contention becomes a problem.

Read [the shared contract](shared-contract.md), then one work package:

1. [Windows](01-windows.md): the two large front window assemblies.
2. [Lodge doors](02-doors.md): public entrance, gondola-side exit and coffee staff door.
3. [Restrooms](03-restrooms.md): restroom entrance doors, stall partitions/doors, toilets, urinal, sinks and accessories.
4. [Kitchen](04-kitchen.md): enclosed service counter, preparation equipment, storage and everyday props.
5. [Tables and benches](05-benches.md): the six picnic tables and twelve matching benches, including realistic construction and wear.
6. [Lockers](06-lockers.md): the twelve-unit bank, moving doors, interiors and mechanical hardware.
7. [Wall displays and artwork](07-wall-details.md): posters, maps, timetable, notices, fixed-wall wayfinding, menu artwork and supporting wall details.
8. [Additional east-wall dressing](08-east-wall-dressing.md): an additive pass against the integrated lodge 04, furnishing the bare wall between the visitor map and lockers with period displays and practical fittings.

The restroom task owns every bathroom door. The kitchen task reserves the staff doorway; the lodge-door task owns its door assembly. This avoids cross-task ownership of the same mesh.

## Integration after the seven packages

One integration task should assemble the packages into a new `passenger_lodge_04` master. Each package supplies named collections, fitted transforms and an explicit replacement/patch manifest. Remove the corresponding proxies and apply only declared wall/opening patches. Check the combined door swings, work aisles, restroom approach and platform routes; render exterior and occupied interior views, then save/reopen. Do not merge competing copies of a `.blend` file.

Roof/drainage, other loose dressing, lighting fixtures and Unreal interactions are later packages. Keep the current layout while these seven areas gain detail. Seating owns only the picnic tables/benches; lockers owns the locker bank; kitchen retains its counter, shelves, cubby and physical menu frame. Wall details supplies menu artwork and fixed-wall signage, not locker numbers or bathroom hardware.

## Short dispatch messages

Give each task its corresponding file, for example:

> Implement the windows handoff in `docs/handoffs/passenger-lodge/01-windows.md`. Read its shared contract first, then complete its standalone Blender package, fitted review renders and verification. Preserve the shared master and other tasks' outputs.

Use the same wording with `02-doors.md`, `03-restrooms.md`, `04-kitchen.md`, `05-benches.md`, `06-lockers.md` or `07-wall-details.md` for the other tasks.
