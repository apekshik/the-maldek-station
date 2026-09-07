# Revision 04 — working-station details and water tower

Open `Maldek_Architecture_Redesign.blend`. Revision 03 and the Unreal level remain unchanged.

## Added

Electrical enclosures with gasketed covers, warning plates and fasteners; clipped conduit; weather louvres; guarded light housings; gutters and downpipes; hose reels; building identifiers; maintenance cabinets; extinguisher; waste bins; exterior bench; boot scraper; battery enclosure; spare-parts crate. Details sit against building edges rather than in the middle of the main promenade.

The water tower follows the supplied reference's blue/galvanized tank, horizontal bands, braced steel legs, connection plates and access cage. It has a closed roof, inspection hatch, top guard with ladder opening, outlet valve wheel and overflow pipe. Tank vessel diameter is approximately 2.96 m; bottom is at 3.03 m and lid at approximately 6.3 m. It is an editable visual asset, not a complete engineered water system. The supply pipe is a connection stub; buried distribution and treatment are not designed here.

Matching generator/workshop and relay aprons use the same inner grating, broad solid steel and outer grating bands. Gate openings connect them to the main deck. The water tower sits on a solid service pad connected to the relay apron. Connecting passages and all service-building positions are still design-study placements; reconcile them with the actual terrain and station layout before integration.

## Review

Seven PNGs are in `renders/`. `01_Control_Quarters.png` shows facade details; `06_Water_Tower.png` shows the tower; `07_Service_Detail.png` shows the material/detail treatment on the generator building.

`verification.json` records 513 passing inherited samples for main circulation, stairs, roof junction and deck bands. `utility_verification.json` records 28 additional passing samples for gateway clearance, relay connector floor, closed tank lid, ladder exit and column bearing. These are sampled Blender geometry checks, not collision sweeps, ladder gameplay tests, or structural certification.

Suggested next environment details: weather instruments, emergency call point, spare cable drums and a small maintenance trolley. These have not been modeled in this pass.

## Reproduction and limitations

Run `scripts/build_detail_pass.py` in factory-startup background Blender. It derives from the preceding scripts without overwriting their outputs. Run `scripts/verify_detail_pass.py` against the saved file. Materials and the inherited concrete scan are packed/editable in Blender. No external assets were purchased. Unreal import, complete plumbing, full game-platform replacement and performance optimization remain pending.
