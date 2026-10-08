import sys, json, glob, os, wave
import numpy as np
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0; return a
from faster_whisper import WhisperModel
audio_dir, out_dir = sys.argv[1], sys.argv[2]
m = WhisperModel('small.en', device='cpu', compute_type='int8')
for wav in sorted(glob.glob(os.path.join(audio_dir, '*.wav'))):
    n = os.path.basename(wav)[:-4]
    if n.startswith('br_'): continue
    segs, _ = m.transcribe(load(wav), word_timestamps=True, vad_filter=True, beam_size=5)
    data = [{'start': s.start, 'end': s.end, 'text': s.text.strip(),
             'words': [{'w': w.word, 's': w.start, 'e': w.end, 'p': w.probability} for w in s.words]} for s in segs]
    json.dump(data, open(os.path.join(out_dir, n + '.json'), 'w'), indent=1)
    with open(os.path.join(out_dir, n + '.txt'), 'w') as f:
        for s in data: f.write(f"[{s['start']:6.1f}-{s['end']:6.1f}] {s['text']}\n")
    print('done', n, flush=True)
print('ALLDONE')
