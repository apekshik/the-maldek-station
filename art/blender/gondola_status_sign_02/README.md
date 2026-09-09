# Wide gondola roof indicator

Blender-authored revision of the approved petrol-enamel and brass neon sign.
The 2.60 m × 1.30 m cabinet uses a two-by-two grid: BOARD / ARRIVING above
DEPART / AWAY. Two short bolted shoes replace the pedestal. The rain hood,
double brass border, porcelain electrodes, service enclosure and rear conduit
remain physical geometry. Overall height including mounts and hood is 1.473 m.

`scripts/build.py` rebuilds the model and six review renders. `scripts/verify.py`
checks closed evaluated meshes, unique electrode surfaces, landscape proportions,
absence of a pole and exactly one active circuit at each timeline marker.
Frames 1 / 49 / 97 / 145 select BOARD / ARRIVING / DEPART / AWAY.

The original revision remains in `gondola_status_sign_01`. The review roof coupon
and hidden cabin reference are excluded from export. The Unreal handoff reuses
the existing four-circuit controller, with a new cabinet and two shoe collision
boxes, and retains the right-hand roof placement facing the incoming platform.
