from pathlib import Path
b=Path(__file__).resolve().parents[1]
source=(b/'scripts/r13_capture.py').read_text().replace("out=base.parent/'revision13/reviews'", "out=base/'parking_navigation'/JOB.get('folder','after')")
exec(compile(source,str(b/'scripts/r13_capture.py'),'exec'))
