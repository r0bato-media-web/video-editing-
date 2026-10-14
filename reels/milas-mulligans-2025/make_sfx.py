"""Stand-in sounds for the hot dog reel, made from scratch (no samples, nothing licensed), because the approved kit
(R0BATO TOOLKIT/assets/sfx) is on the SSD. Rob, 14 Oct 2026: "you can make the sounds using whatever you can".
pop.wav: a short bubbly pop for each scoreboard change. boom.wav: a low hit for the FINAL reveal.
Both 48 kHz stereo, peak -1 dBFS; levels are set in the mix. Usage: python make_sfx.py <out_dir>"""
import sys, wave, numpy as np
SR = 48000
def save(path, x):
    x = x / np.max(np.abs(x)) * 10 ** (-1 / 20)
    s = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(s, 2).tobytes())
t = np.arange(int(SR * 0.16)) / SR
f = 380 + 1100 * (1 - np.exp(-t / 0.018))                     # pitch flicks up, like a cork
ph = 2 * np.pi * np.cumsum(f) / SR
env = (1 - np.exp(-t / 0.0015)) * np.exp(-t / 0.035)
pop = env * (np.sin(ph) + 0.25 * np.sin(2 * ph))
save(sys.argv[1] + '/pop.wav', pop)
t = np.arange(int(SR * 1.4)) / SR
f = 42 + 95 * np.exp(-t / 0.06)                               # drops fast to a 42 Hz rumble
ph = 2 * np.pi * np.cumsum(f) / SR
body = np.tanh(2.2 * np.sin(ph)) * np.exp(-t / 0.45)          # saturated so it reads on phone speakers
rng = np.random.default_rng(7)
click = rng.standard_normal(t.size) * np.exp(-t / 0.006) * 0.35
boom = (body + click) * (1 - np.exp(-t / 0.002))
boom[-int(SR * 0.05):] *= np.linspace(1, 0, int(SR * 0.05))
save(sys.argv[1] + '/boom.wav', boom)
