from pathlib import Path
s=Path('art/blender/pylon_study_02/scripts/verify_export.py').read_text().replace('SM_Maldek_Central_Pylon','SM_Maldek_Tapered_Pylon').replace('45.12','45.268')
s=s.replace("'sampled_cabin_positions':len(c['tested_cabin_travel_positions_m'])", "'sampled_cabin_poses':c['poses_checked'],'illustrative_swing_degrees':c['illustrative_body_swing_degrees']")
s=s.replace("assert abs(hi[2]-45.268)<.002", "assert abs(hi[2]-45.268)<.002\nassert abs(lo[2]+6)<.002")
Path('art/blender/pylon_study_03/scripts/verify_export.py').write_text(s)
p=Path('art/blender/pylon_study_03/README.md');s=p.read_text().replace('cabin in the central opening.','cabin in the central opening, with studio rope curves hidden to keep the foreground clear.');p.write_text(s)
