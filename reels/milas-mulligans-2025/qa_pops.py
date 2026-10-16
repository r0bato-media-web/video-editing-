"""Measure every sound effect against the voice it lands on, in the real mix.
build_reel2.py writes mix_dry_<v>.wav (voices only) and mix_wet_<v>.wav (voices + effects) before loudness; wet minus
dry is the effects alone. For each hit in sfx_<v>.json: loudest 50 ms of the effect vs loudest 50 ms of the voice in
the 0.4 s from the hit. Usage: python qa_pops.py <reel2_dir> <version>"""
import json, os, subprocess, sys
import numpy as np
D, V = sys.argv[1], sys.argv[2]


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def loud(a, sr=48000, win=0.05):
    k = int(sr * win)
    if len(a) < k:
        return -120.0
    c = np.convolve(a.astype(np.float64) ** 2, np.ones(k) / k, mode='valid')
    return float(10 * np.log10(c.max() + 1e-12))


dry, wet = load(os.path.join(D, f'mix_dry_{V}.wav')), load(os.path.join(D, f'mix_wet_{V}.wav'))
fx = wet[:len(dry)] - dry[:len(wet)]
print(f"{'t':>7} {'sound':6} {'fx dB':>7} {'voice dB':>9} {'fx-voice':>9}")
for h in json.load(open(os.path.join(D, f'sfx_{V}.json'))):
    a, b = int(h['t'] * 48000), int((h['t'] + 0.4) * 48000)
    f_, v_ = loud(fx[a:b]), loud(dry[a:b])
    print(f"{h['t']:7.2f} {h['sound']:6} {f_:7.1f} {v_:9.1f} {f_ - v_:9.1f}")
