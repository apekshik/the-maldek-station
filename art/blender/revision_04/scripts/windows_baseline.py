"""Render the revision 03 baseline on Windows without changing its source file."""
import bpy
import hashlib
import json
import subprocess
import threading
import time
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
AUDIT = OUT / 'audit' / 'before'
AUDIT.mkdir(parents=True, exist_ok=True)
source = Path(bpy.data.filepath)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
scene = bpy.context.scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.refresh_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX' and '5070 Ti' in device.name
assert any(d.use for d in prefs.devices), 'RTX OptiX device unavailable'
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.camera = bpy.data.objects['CAM_R03_Platform_Rain']
scene.render.resolution_x = 1400
scene.render.resolution_y = 930
scene.render.resolution_percentage = 100
scene.cycles.samples = 40
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(AUDIT / 'platform_rain_windows.png')
for layer in scene.view_layers:
    layer.use = layer.name == '02_Full_Shell'
bpy.context.window.view_layer = scene.view_layers['02_Full_Shell']
images = []
for im in bpy.data.images:
    if im.source != 'FILE':
        continue
    packed = bool(im.packed_file or im.packed_files)
    exists = Path(bpy.path.abspath(im.filepath)).is_file()
    images.append({'name': im.name, 'packed': packed, 'external_exists': exists,
                   'missing': not packed and not exists})
report = {
    'source': str(source), 'source_sha256': source_hash,
    'blender_version': bpy.app.version_string,
    'devices': [{'name': d.name, 'type': d.type, 'enabled': bool(d.use)} for d in prefs.devices],
    'camera': scene.camera.name, 'view_layer': '02_Full_Shell',
    'resolution': [1400, 930], 'samples': 40,
    'denoising': scene.cycles.use_denoising, 'exposure': scene.view_settings.exposure,
    'images': images, 'missing_images': [i['name'] for i in images if i['missing']],
    'objects': len(scene.objects),
    'mesh_objects': sum(o.type == 'MESH' for o in scene.objects),
    'gpu_memory_note': 'nvidia-smi total device memory usage sampled every second; includes other applications.',
}
(OUT / 'audit' / 'windows_baseline_report.json').write_text(json.dumps(report, indent=2))
assert not report['missing_images'], report['missing_images']
samples = []
stop = threading.Event()
def monitor():
    while not stop.is_set():
        try:
            raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu',
                '--format=csv,noheader,nounits'], text=True, creationflags=0x08000000)
            values = raw.strip().split(',')
            samples.append({'seconds': round(time.perf_counter()-start, 2),
                            'memory_mib': int(values[0]), 'utilization_percent': int(values[1])})
        except Exception as exc:
            report['monitor_error'] = str(exc)
        stop.wait(1)
start = time.perf_counter()
thread = threading.Thread(target=monitor, daemon=True)
thread.start()
try:
    bpy.ops.render.render(write_still=True, layer='02_Full_Shell')
    report['render_success'] = True
finally:
    report['render_wall_seconds'] = round(time.perf_counter()-start, 3)
    stop.set()
    thread.join(timeout=5)
    report['gpu_samples'] = samples
    report['peak_total_gpu_memory_mib'] = max((s['memory_mib'] for s in samples), default=None)
    report['source_unchanged'] = hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    (OUT / 'audit' / 'windows_baseline_report.json').write_text(json.dumps(report, indent=2))
print('WINDOWS_BASELINE_REPORT', json.dumps({k: v for k, v in report.items() if k not in ('images', 'gpu_samples')}), flush=True)
