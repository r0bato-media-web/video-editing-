"""Apparent camera motion in a rendered file, in output px/s, per cut (max over 0.2 s steps) and the hook band.
Usage: python output_motion.py <video> <timeline.json>"""
import subprocess, sys, json, numpy as np
vid, tl = sys.argv[1], json.load(open(sys.argv[2]))
w, h = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', vid]).decode().strip().split(','))
sc = 4; W, H = w // sc, h // sc
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', vid, '-vf', f'fps=30,scale={W}:{H},format=gray', '-f', 'rawvideo', '-'])
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
band = fr[:, int(H * 0.30):int(H * 0.75), :]  # below the tally/hook text, above the captions
hb = band.shape[1]; win = np.outer(np.hanning(hb), np.hanning(W))
def sh(a, b):
    A, B = np.fft.fft2((a - a.mean()) * win), np.fft.fft2((b - b.mean()) * win); R = A * np.conj(B)
    r = np.fft.ifft2(R / (abs(R) + 1e-9)).real; y, x = np.unravel_index(np.argmax(r), r.shape)
    y -= hb if y > hb // 2 else 0; x -= W if x > W // 2 else 0; return x * sc, y * sc
for i, s in enumerate(tl):
    d = s['out'] - s['in']; f0 = int(round(s['t0'] * 30)) + 1; f1 = int(round((s['t0'] + d) * 30)) - 1
    sp = [((lambda v: (v[0] ** 2 + v[1] ** 2) ** .5)(sh(band[k], band[min(k + 6, f1)]))) / ((min(k + 6, f1) - k) / 30) for k in range(f0, f1 - 1, 6)]
    print(f"cut {i + 1:2d} {s['clip']:16s} {s['in']:6.2f}  max {max(sp) if sp else 0:5.0f} px/s  mean {np.mean(sp) if sp else 0:5.0f}")
