"""Download licensed audition candidates; never changes Unreal assets."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
TRACKS = [
    ('A', 'Dark Cavern Ambient', 'Paul Wortmann', 'https://opengameart.org/content/dark-cavern-ambient', 'https://opengameart.org/sites/default/files/dark_cavern_ambient_001.ogg', 'CC0-1.0', 0),
    ('B', 'Dark Ambient Drone #2', 'Tsorthan Grove', 'https://opengameart.org/content/dark-ambient-drone-2', 'https://opengameart.org/sites/default/files/dark_ambient_drone_2.flac', 'CC-BY-4.0', 15),
    ('C', 'The Long Dark', 'Scott Buckley', 'https://www.scottbuckley.com.au/library/the-long-dark/', 'https://www.scottbuckley.com.au/library/wp-content/uploads/2023/01/TheLongDark.mp3', 'CC-BY-4.0', 30),
    ('D', 'Memories Of Stone', 'Scott Buckley', 'https://www.scottbuckley.com.au/library/memories-of-stone/', 'https://www.scottbuckley.com.au/library/wp-content/uploads/2026/02/MemoriesOfStone.mp3', 'CC-BY-4.0', 60),
    ('E', 'Aphelion', 'Scott Buckley', 'https://www.scottbuckley.com.au/library/aphelion/', 'https://www.scottbuckley.com.au/library/wp-content/uploads/2026/04/Aphelion.mp3', 'CC-BY-4.0', 90),
    ('F', 'The Encounter', 'Scott Buckley', 'https://www.scottbuckley.com.au/library/the-encounter/', 'https://www.scottbuckley.com.au/library/wp-content/uploads/2019/07/sb_monomyth_7_theencounter.mp3', 'CC-BY-4.0', 60),
]

def fetch(url, path):
    if not path.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
        path.write_bytes(data)

def prepare(track):
    label, title, author, page, url, license_id, start = track
    original = ROOT / 'originals' / (label + '_' + url.rsplit('/', 1)[-1])
    fetch(url, original)
    fetch(page, ROOT / 'source_pages' / (label + '.html'))
    data, rate = sf.read(original, always_2d=True, dtype='float32')
    end = min(start + 45, len(data) / rate)
    clip = data[int(start * rate):int(end * rate)].copy()
    rms = float(np.sqrt(np.mean(clip.astype('float64') ** 2)))
    peak = float(np.max(np.abs(clip)))
    gain = min(10 ** (-23 / 20) / max(rms, 1e-9), .89 / max(peak, 1e-9), 4)
    clip *= gain
    fade = min(int(rate * 1.5), len(clip) // 2)
    clip[:fade] *= np.linspace(0, 1, fade)[:, None]
    clip[-fade:] *= np.linspace(1, 0, fade)[:, None]
    preview = ROOT / 'previews' / (label + '_preview.wav')
    sf.write(preview, clip, rate, subtype='PCM_16')
    checked, checked_rate = sf.read(preview, always_2d=True)
    assert len(checked) > checked_rate * 10 and np.max(np.abs(checked)) < 1
    result = dict(id=label, title=title, author=author, source_page=page, download_url=url,
        license=license_id, license_url=('https://creativecommons.org/publicdomain/zero/1.0/' if label == 'A' else 'https://creativecommons.org/licenses/by/4.0/'),
        attribution=f"'{title}' by {author} - {license_id}. {page}",
        original=str(original), original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
        original_duration_seconds=round(len(data)/rate, 3), preview=str(preview),
        excerpt_start_seconds=start, excerpt_end_seconds=end, preview_gain_db=round(20*np.log10(gain), 2),
        modifications='45-second excerpt (or available duration), constant gain, 1.5-second endpoint fades; original retained unchanged.',
        sample_rate=rate, channels=data.shape[1], verified_peak=float(np.max(np.abs(checked))))
    print(f'{label}: {title}, original {len(data)/rate:.1f}s, preview {start}-{end}s; verified', flush=True)
    return result

if __name__ == '__main__':
    for folder in ('originals', 'previews', 'source_pages'):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(prepare, TRACKS))
    (ROOT / 'sources.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    credits = ['# Maldek Station audio auditions', '', 'Downloaded 2026-09-07. Preview candidates only; not imported into the game.',
        'Originals are unchanged. Previews apply only excerpts, constant gain, and endpoint fades.',
        'Source descriptions informed the shortlist; excerpt selection has not been auditioned in the game.', '']
    for item in results:
        credits += [f"## {item['id']} - {item['title']}", '', item['attribution'], item['license_url'],
            f"Excerpt: {item['excerpt_start_seconds']}-{item['excerpt_end_seconds']} seconds. Full original retained in originals/.", '']
    (ROOT / 'README.md').write_text('\n'.join(credits), encoding='utf-8')
