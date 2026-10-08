"""Cross-correlate each cut's audio in a render against its source clip. Usage: sync_check.py video timeline.json m25"""
import json, subprocess, sys, numpy as np
V, T, M = sys.argv[1:4]
def pcm(path, a, d):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', path, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.int16).astype(float)
out = []
for s in json.load(open(T)):
    d = min(s['out'] - s['in'], 1.2) - 0.1
    if d < 0.25: out.append(None); continue
    x = pcm(V, s['t0'] + 0.05, d); y = pcm(f"{M}/raw/{s['clip']}.mp4", s['in'] + 0.05 - 0.1, d + 0.2)
    x = x - x.mean(); best = max(range(0, len(y) - len(x)), key=lambda k: np.dot(x, y[k:k + len(x)] - y[k:k + len(x)].mean()))
    out.append(round((best / 8000 - 0.1) * 1000))
print('offset ms per cut:', out)
