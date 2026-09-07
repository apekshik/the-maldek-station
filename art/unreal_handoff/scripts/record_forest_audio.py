import unreal,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';w=unreal.EditorLevelLibrary.get_game_world();assert w
unreal.AudioMixerLibrary.start_recording_output(w,12.)
record_end=time.monotonic()+10
record_busy=False
def record_audio_tick(dt):
 global record_busy
 if record_busy or time.monotonic()<record_end:return
 record_busy=True
 try:unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'footstep_mix',str(out))
 except Exception:(out/'audio_record_error.txt').write_text(traceback.format_exc())
 unreal.unregister_slate_post_tick_callback(record_audio_handle)
record_audio_handle=unreal.register_slate_post_tick_callback(record_audio_tick)

