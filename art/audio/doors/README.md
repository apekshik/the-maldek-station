# Door and keypad recordings

The synthesized bank is retired. prepare.py now edits six downloaded CC0 field
recordings into ten 48 kHz mono effects. No synthesized tones, generated noise,
AI audio, or pitch shifts are used. Files under recorded/originals are the public
high-quality MP3 previews, not the uploaders' lossless masters. sources.json
records URLs, license links and SHA-256 hashes; manifest.json records every edit.

| Event | Recorded source |
| --- | --- |
| Digit / CLR | Mihacappy, real apartment intercom key presses, 828113 |
| Accepted password | Answer tone from the same intercom recording |
| Rejected password / entry limit | qubodup, recorded computer fault buzzer, 167848 |
| Handle release / door impact | giddster, metal access door, 336660 |
| Opening / closing movement | MathewHenry, close-miked steel fire door hinges, 700682 / 700705 |
| Unlock / re-lock | wlabarron, hotel keycard deadbolt, 494128 |

The fault buzzer and hotel bolt are explicitly sound-design proxies for this
station's reader and strike. Lock and unlock use different excerpts of the same
recorded bolt movement. Preparation uses trimming, mono conversion, resampling,
high-pass filtering, constant gain, and short fades/loop crossfades only.

Rebuild with Python + numpy/scipy/soundfile: `python art/audio/doors/prepare.py`.
Audition.wav orders key press, clear, acceptance, rejection, handle release,
opening movement, closing movement, closing impact, unlock, lock.

Native wiring separates keypad, mechanical event, fixed bolt, and motion audio.
Keypad voices can overlap so rapid clicks retain their tails. Opening/closing
loops follow actual motion, stop at obstruction/rest, and the impact occurs only
at fully closed. Accepted input plays confirmation plus a separate bolt release;
invalid/empty passwords and the eight-digit limit play rejection. Closing a
secured door re-locks it, with the bolt audible 180 ms after the impact. Standard
doors stay unlocked; locking an open door is rejected.

Target near-field gains are keypad 1.6, mechanical events 1.3, motion 1.2, with
150 cm full-volume radius and 13.5 m linear falloff. Keypad peaks are 11-14 dB
stronger than the previous bank; peak preparation preserves room for ambience.
These are initial mix settings, subject to the in-engine capture check.

Validation: final Win64 Development game and editor compilation passed. The live keyboard
sequences on all three installed keypads pass 183 checks; 18 additional checks
cover empty/overlong entries, an obstructed close, retry/re-lock and an inward
standard door. Mouse input shares the unchanged native button handler; direct
offscreen cursor automation was unsuitable and was not counted as a pass.

The 56.81-second gameplay mix, including normal station ambience, peaks at 0.611
(-4.28 dBFS), with RMS 0.099 and no near-full-scale samples. These are measured
results, not a subjective listening claim or a guarantee for every possible mix.
Save/reopen verification confirms all ten doors retain the recorded bank, with
three keypads locked and seven standard doors unlocked. Scripts and evidence are
in art/unreal_handoff/revision12/doors/recorded_audio and scripts/doors_recorded_*.
Temporary test launch overrides bypassed the separate unfinished startup menu and
allowed audio while unfocused; no persistent startup/audio config was changed.
