# Recorded platform and docking cues

CC0 field recordings supply distinct ARRIVING, BOARD, DEPART and AWAY chimes, plus a short compressed-air docking release. Source URLs, authors, hashes and editing recipes are retained alongside the original downloads.

The fixed sign announces only a change of its actual interlocked status. Startup, unchanged states and lost gondola references remain silent. BOARD waits for the landing and open doors; DEPART precedes movement. The separate cabin-mounted whoosh fires at OnReachedDestination at either terminal, before opening. Existing machinery, brakes and doors continue independently.

Native hard references include all five assets in cooked builds without a map resave. Both gains default to 1.5 and remain editable. Platform full-volume radius is 6.5m with 45m falloff; docking is 5.5m with 30m falloff. Files retain peak headroom and use gentle compression for presence.

Regenerate with prepare.py using NumPy, SciPy and soundfile, import with gondola_arrival_import.py, then run gondola_arrival_runtime.py in the R12 editor dispatcher. The test accelerates travel in PIE only and records the real mixed audio around stops.
