"""Camera speed in source px/s over a source range, every 0.2 s, by phase correlation on the top 45% of the frame
(background, mostly free of the people talking). Usage: python camera_speed.py <m25> <clip> <a> <b>"""
import subprocess, sys, os, numpy as np
M, clip, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
W, H, S = 384, 216, 5.0
BAND = (float(sys.argv[5]), float(sys.argv[6])) if len(sys.argv) > 6 else (0.0, 0.45)
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', os.path.join(M, 'raw', clip + '.mp4'),
                               '-vf', f'fps=30,scale={W}:{H},format=gray', '-f', 'rawvideo', '-'])
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)[:, int(H * BAND[0]):int(H * BAND[1]), :]
h = fr.shape[1]; win = np.outer(np.hanning(h), np.hanning(W))
def shift(f0, f1):
    F0, F1 = np.fft.fft2((f0 - f0.mean()) * win), np.fft.fft2((f1 - f1.mean()) * win)
    R = F0 * np.conj(F1); r = np.fft.ifft2(R / (np.abs(R) + 1e-9)).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    if y > h // 2: y -= h
    if x > W // 2: x -= W
    return x * S, y * S
d = [shift(fr[i], fr[i + 6]) for i in range(0, len(fr) - 6, 6)]  # 0.2 s steps
out = []
for k, (dx, dy) in enumerate(d):
    sp = (dx * dx + dy * dy) ** 0.5 / 0.2
    out.append(f"{a + k * 0.2:6.2f}:{sp:5.0f}{'*' if sp > 150 else ' '}")
print(clip, ' '.join(out))
