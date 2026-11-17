"""A calm outdoor bed made from scratch (no recording): shaped noise for a light breeze, optional synthetic bird chirps.
Usage: python make_ambience.py <seconds> <out_breeze.wav> <out_breeze_birds.wav>"""
import sys, wave
import numpy as np
SR = 48000
def lp(x, fc):                      # one-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i, v in enumerate(x):
        z = (1 - a) * v + a * z; y[i] = z
    return y
def fft_band(x, lo, hi):            # brick-wall band-pass with soft edges
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))
def breeze(n, seed):
    """Steady open air, no swell. The first version rose and fell every 3 to 7 s and Rob heard the ocean (16 Nov 2026)."""
    r = np.random.default_rng(seed)
    w = fft_band(r.standard_normal(n), 500, 3500)                    # lighter and higher than before: air, not surf
    t = np.arange(n) / SR
    wob = 1.0 + 0.06 * np.sin(2 * np.pi * t / 1.7 + r.uniform(0, 6)) + 0.04 * np.sin(2 * np.pi * t / 0.9 + r.uniform(0, 6))
    return w * wob
def chirp(r):
    d = r.uniform(0.06, 0.13); t = np.arange(int(d * SR)) / SR
    f0 = r.uniform(2800, 4600); f1 = f0 * r.uniform(0.75, 1.35)
    ph = 2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * d))
    return np.sin(ph) * np.sin(np.pi * t / d) ** 2
def birds(n, seed):
    r = np.random.default_rng(seed); y = np.zeros(n); t = 1.5
    while t < n / SR - 1.5:
        k = r.integers(2, 6); gain = r.uniform(0.25, 1.0); pos = t
        for _ in range(k):                                           # a short phrase of chirps
            c = chirp(r) * gain; i = int(pos * SR)
            if i + len(c) < n: y[i:i + len(c)] += c
            pos += r.uniform(0.11, 0.22)
        t += r.uniform(2.2, 5.5)
    return y
def save(path, l, rgt):
    st = np.stack([l, rgt], 1); st = st / np.abs(st).max() * 0.5
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
n = int(float(sys.argv[1]) * SR)
bl, br = breeze(n, 1), breeze(n, 2)
bl = 0.7 * bl + 0.3 * br; br = 0.7 * br + 0.3 * breeze(n, 3)
bl /= np.abs(bl).max(); br /= np.abs(br).max()
save(sys.argv[2], bl, br)
b = birds(n, 7); b2 = birds(n, 11)
save(sys.argv[3], 0.5 * bl + 0.22 * b + 0.07 * b2, 0.5 * br + 0.07 * b + 0.22 * b2)   # birds lead, air sits under them
