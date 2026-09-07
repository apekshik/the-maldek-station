"""Companion device-memory telemetry. Run alongside the same engine benchmark on both revisions."""
import subprocess,time,sys,csv
from pathlib import Path
base=Path(__file__).resolve().parents[1];name=sys.argv[1];assert name in ['baseline','final']
out=base/name/'device_telemetry.csv';deadline=time.monotonic()+190
with out.open('w',newline='') as f:
 while time.monotonic()<deadline:
  p=subprocess.run(['nvidia-smi','--query-gpu=timestamp,name,memory.used,memory.total,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
  f.write(p.stdout);f.flush();time.sleep(1)
