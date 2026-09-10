# Passenger lodge: four parallel modeling handoffs

These handoffs are ready to give to four separate Codex tasks. They authorize Blender modeling and review packages, not edits to the shared master scene or Unreal integration. Multiple Blender processes can run at once, each with its own output file. Stagger heavy renders if memory/GPU contention becomes a problem.

Read [the shared contract](shared-contract.md), then one work package:

1. [Windows](01-windows.md): the two large front window assemblies.
2. [Lodge doors](02-doors.md): public entrance, gondola-side exit and coffee staff door.
3. [Restrooms](03-restrooms.md): restroom entrance doors, stall partitions/doors, toilets, urinal, sinks and accessories.
4. [Kitchen](04-kitchen.md): enclosed service counter, preparation equipment, storage and everyday props.

The restroom task owns every bathroom door. The kitchen task reserves the staff doorway; the lodge-door task owns its door assembly. This avoids cross-task ownership of the same mesh.

## Integration after the four packages

One integration task should assemble the packages into a new `passenger_lodge_04` master. Each package supplies named collections, fitted transforms and an explicit replacement/patch manifest. Remove the corresponding proxies and apply only declared wall/opening patches. Check the combined door swings, work aisles, restroom approach and platform routes; render exterior and occupied interior views, then save/reopen. Do not merge competing copies of a `.blend` file.

Roof/drainage, finished hall furniture, posters/notices, lighting fixtures and Unreal interactions are later packages. Keep the current layout while these four areas gain detail.

## Short dispatch messages

Give each task its corresponding file, for example:

> Implement the windows handoff in `docs/handoffs/passenger-lodge/01-windows.md`. Read its shared contract first, then complete its standalone Blender package, fitted review renders and verification. Preserve the shared master and other tasks' outputs.

Use the same wording with `02-doors.md`, `03-restrooms.md` or `04-kitchen.md` for the other tasks.
