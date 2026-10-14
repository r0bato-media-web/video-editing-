"""Reel 2: 'Mayo or sand?' Ten golfers from Mila's Mulligans 2025 answer "would you rather eat a jar full of
mayonnaise or a handful of sand?", a two-jar scoreboard counts the votes, and the FINAL card calls it: a 5-5 tie.

Built on build_reel1.py (cuts snapped to whole frames, static crops on whoever holds the mic, word-timed captions,
FINAL over the last live shot). Differences: the scoreboard is two pills (MAYO, SAND), and each pop's level is
computed from the voice it lands on (6 dB under), not typed in by hand.

v2 (Rob, 14 Oct 2026: "you can stabilize them", "add jar of mayo or sand or sand castle, dress this up"):
the three shaky cuts are stabilized (vidstab, tripod mode, locked to the cut's first frame, 6% punch-in), and a
mayo jar and a sand castle (drawn here, see make_icons) sit in the scoreboard, beside the hook and beside FINAL.

Usage: python build_reel2.py <m25_dir> [version]        (9:16 only, like reel 1)
Clip names are the list.tsv names: ant, darryl, frankie, interview3, jasmin_bf.
"""
import json, os, subprocess, sys, wave
import numpy as np

M = sys.argv[1]
V = sys.argv[2] if len(sys.argv) > 2 else 'v1'
RAW, TR, AUD, SFX = (os.path.join(M, d) for d in ('raw', 'transcripts', 'audio', 'sfx'))
OUT = os.path.join(M, 'reel2'); os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920

# clip, in, out, 9:16 crop centre x (source px), hook?
# Who said what was checked by where the mic is and whose mouth moves on the word (contact sheets, 14 Oct 2026).
CUTS = [
    ('darryl',     3.70,  6.62, 1330, True,  False),   # interviewer: would you rather eat a jar full of mayonnaise or a handful of sand?
    ('frankie',   41.62, 43.50, 1020, False, False),   # blue polo: Oh, jar of mayonnaise. All day. I love mayonnaise. (camera starts to swing at 43.4; stabilizing made it worse, 120 vs 100 px/s)
    ('interview3', 17.80, 19.40, 520, False, True),    # floral shirt, glasses: Oh, man, definitely a handful of sand. (handheld wobble: stabilized)
    ('frankie',   11.70, 15.86, 940, False, False),    # black shirt: I love elotes, so I'm going to go with a jar full of mayonnaise.
    ('frankie',   17.14, 19.66, 1200, False, False),   # blue shirt, beard: handful of sand because mayonnaise is disgusting.
    ('ant',        7.50,  8.30, 720, False, False),    # pink shirt: Mayonnaise. (mic at his mouth)
    ('ant',        8.30,  9.35, 880, False, False),    # navy shirt: Handful of sand.
    ('ant',        9.35, 10.00, 1150, False, True),    # floral shirt: Mayonnaise. (camera starts to pan: stabilized)
    ('ant',       10.00, 10.55, 1400, False, True),    # white shirt: And sand. (mic moves to him, his mouth opens; pan: stabilized)
    ('jasmin_bf', 35.96, 37.30, 740, False, False),    # grey polo: A jar full of mayonnaise all day.
    ('darryl',     7.30, 12.20, 1000, False, False),   # Darryl: I've done a handful of sand already when I was younger, so handful of sand all day every day
]
STAB_ZOOM = 1.06   # punch-in on stabilized cuts, so the locked frame never shows an edge
# Darryl's shot plays on live under FINAL; the sound fades after "every day", so "wash it out with more booze" is never heard.
MUTE = {('darryl', 7.30): 10.86}
# One vote per person, on the word that casts it: (clip, word start, side). Count: MAYO 5, SAND 5.
# Not counted: interview3 20.12 "Mayo all the way" (the interviewer teasing; the golfer answers "No, I can't slug mayo
# like that") and interview3 31.22 "Mayo." (-47 dB, off the mic, nobody on camera says it, camera swinging).
VOTES = [
    ('frankie', 42.22, 'M'),
    ('interview3', 19.10, 'S'),
    ('frankie', 15.28, 'M'),
    ('frankie', 18.30, 'S'),
    ('ant', 7.64, 'M'),
    ('ant', 8.84, 'S'),
    ('ant', 9.48, 'M'),
    ('ant', 10.12, 'S'),
    ('jasmin_bf', 36.48, 'M'),
    ('darryl', 8.12, 'S'),
]
YFRAC = 0.42
POP_UNDER_VOICE = 6.0


def mute_for(seg):
    for (c, i), m in MUTE.items():
        if c == seg['clip'] and abs(i - seg['in']) < 0.05:
            return m
    return None


def words_for(clip, a, b):
    return [w for s in json.load(open(os.path.join(TR, clip + '.json'))) for w in s['words']
            if w['s'] >= a - 0.02 and w['s'] < b - 0.05]


def word_at(clip, t):
    """The word that starts at t; if two do (whisper gives "And" zero length at ant 10.12), the longer one."""
    ws = [w for s in json.load(open(os.path.join(TR, clip + '.json'))) for w in s['words'] if abs(w['s'] - t) < 0.02]
    if not ws:
        raise KeyError((clip, t))
    return max(ws, key=lambda w: w['e'] - w['s'])


def ts(t):
    t = int(t * 100 + 1e-6) / 100
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def src_to_out(timeline, clip, t):
    for seg in timeline:
        if seg['clip'] == clip and seg['in'] <= t < seg['out']:
            return seg['t0'] + t - seg['in']
    return None


def wav(path):
    w = wave.open(path); n = w.getnchannels()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return a.reshape(-1, n).mean(axis=1), w.getframerate()


def loudest_db(a, sr, win=0.05):
    """RMS of the loudest 50 ms window, in dBFS."""
    k = max(1, int(sr * win))
    if len(a) < k:
        return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)
    c = np.convolve(a ** 2, np.ones(k) / k, mode='valid')
    return 10 * np.log10(c.max() + 1e-12)


def voice_db(clip, w):
    a, sr = wav(os.path.join(AUD, clip + '.wav'))
    return float(loudest_db(a[int(w['s'] * sr):int(max(w['e'], w['s'] + 0.15) * sr)], sr))


YEL, NAVY, INK = r"&H3FD2FF&", r"&H753304&", r"&H51311E&"   # #FFD23F accent, Mila's navy #043375, ink #1E3151 (flyer)
MAYO, SAND = r"&HC4F3FF&", r"&H7AB4D8&"                     # mayo cream #FFF3C4, sand #D8B47A

# scoreboard geometry, shared by the ASS pills and the icon overlays
PW, PH, GAP, PY = 380, 200, 36, 225
XS = {'M': W // 2 - GAP // 2 - PW, 'S': W // 2 + GAP // 2}
NUM_DX, ICON_DX, ICON_DY, ICON_H = 268, 96, 108, 160   # count centre, icon centre (from the pill's top-left), icon height
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'


def make_icons(out_dir, s=4):
    """Draw the mayo jar and the sand castle (140 x 156 units, drawn at s px per unit), each with an ink outline and a
    soft shadow, and save them as transparent PNGs. Flat shapes in the reel's own colours; no clip art, no brand."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    U = lambda *v: [round(c * s) for c in v]
    ink, navy, yel = (30, 49, 81, 255), (4, 51, 117, 255), (255, 210, 63, 255)

    def finish(art, name):
        a = art.split()[3]
        ring = a.filter(ImageFilter.MaxFilter(2 * round(3.5 * s / 2) + 1))          # ~3.5-unit ink outline
        out = Image.new('RGBA', art.size, (0, 0, 0, 0))
        sh = Image.new('RGBA', art.size, (0, 0, 0, 0)); sh.putalpha(ring.point(lambda v: v * 0.45))
        sh = sh.filter(ImageFilter.GaussianBlur(3 * s)).transform(art.size, Image.AFFINE, (1, 0, -2 * s, 0, 1, -4 * s))
        out.alpha_composite(sh)
        ol = Image.new('RGBA', art.size, ink); ol.putalpha(ring); out.alpha_composite(ol)
        out.alpha_composite(art)
        out.save(os.path.join(out_dir, name))

    pad = 10  # units of margin round the 140 x 156 drawing, so the outline and shadow have room
    size = (round((140 + 2 * pad) * s), round((156 + 2 * pad) * s))
    P = lambda *v: [round((c + pad) * s) for c in v]

    jar = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(jar)
    d.rounded_rectangle(P(10, 32, 130, 154), radius=26 * s, fill=(255, 246, 216, 255))           # mayo in the jar
    d.rectangle(P(20, 27, 120, 36), fill=(234, 219, 168, 255))                                   # neck
    d.rounded_rectangle(P(14, 0, 126, 30), radius=9 * s, fill=navy)                               # lid
    for x in (30, 48, 66, 84, 102):
        d.rectangle(P(x, 5, x + 5, 25), fill=(46, 90, 160, 255))                                  # lid ridges
    d.rectangle(P(10, 80, 130, 122), fill=yel)                                                    # label
    d.rectangle(P(10, 80, 130, 85), fill=navy); d.rectangle(P(10, 117, 130, 122), fill=navy)
    f = ImageFont.truetype(FONT, round(25 * s))
    tw = d.textlength('MAYO', font=f)
    d.text(((pad + 70) * s - tw / 2, (pad + 101) * s), 'MAYO', font=f, fill=navy, anchor='lm')
    hl = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle(P(20, 44, 30, 142), radius=5 * s, fill=(255, 255, 255, 110))  # glass shine
    jar.alpha_composite(hl)
    finish(jar, 'icon_jar.png')

    cas = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(cas)
    tower, keep, mound, dark = (210, 174, 108, 255), (232, 204, 148, 255), (196, 154, 92, 255), (107, 74, 42, 255)
    crenel = lambda x0, x1, top, bot, n: [(x0, bot), (x0, top)] + sum(
        ([(x0 + (x1 - x0) * k / n, top + (8 if k % 2 else 0)), (x0 + (x1 - x0) * (k + 1) / n, top + (8 if k % 2 else 0))]
         for k in range(n)), []) + [(x1, top), (x1, bot)]
    for x0, x1 in ((6, 42), (98, 134)):
        d.polygon([tuple(P(*pt)) for pt in crenel(x0, x1, 54, 140, 3)], fill=tower)               # side towers
    d.polygon([tuple(P(*pt)) for pt in crenel(36, 104, 28, 144, 5)], fill=keep)                   # keep
    d.rectangle(P(69, 2, 72, 30), fill=dark)                                                      # flag pole
    d.polygon([tuple(P(72, 3)), tuple(P(96, 10)), tuple(P(72, 17))], fill=yel)                    # flag
    d.rectangle(P(60, 108, 80, 140), fill=dark); d.ellipse(P(60, 98, 80, 118), fill=dark)        # door
    for box in ((20, 80, 28, 92), (112, 80, 120, 92), (66, 54, 74, 68)):
        d.rounded_rectangle(P(*box), radius=3 * s, fill=dark)                                     # windows
    d.ellipse(P(-8, 128, 148, 186), fill=mound)                                                   # sand it sits in
    for x, y in ((24, 140), (52, 134), (98, 138), (118, 144), (76, 146), (40, 148)):
        d.ellipse(P(x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=(170, 128, 70, 255))               # grains
    cas = cas.crop((0, 0, size[0], round((156 + pad) * s)))                                       # flat bottom on the sand line
    full = Image.new('RGBA', size, (0, 0, 0, 0)); full.alpha_composite(cas)
    finish(full, 'icon_castle.png')
    return {k: os.path.join(out_dir, f'icon_{k}.png') for k in ('jar', 'castle')}


def stabilize(clip, a, b):
    """Lock a shaky cut to its own first frame (vidstab tripod mode), so a static 9:16 crop stays on the speaker.
    Two passes over exactly the cut's range; the result replaces the cut's picture, the sound still comes from the clip."""
    sd = os.path.join(OUT, 'stab'); os.makedirs(sd, exist_ok=True)
    out = os.path.join(sd, f'{clip}_{a:.2f}.mp4'); trf = os.path.join(sd, f'{clip}_{a:.2f}.trf')
    rng = ['-ss', f'{a:.3f}', '-to', f'{b + 0.1:.3f}', '-i', os.path.join(RAW, clip + '.mp4')]
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + rng + ['-vf', f'vidstabdetect=shakiness=8:accuracy=15:tripod=1:result={trf}',
                    '-f', 'null', '-'], check=True)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + rng + ['-vf', f'vidstabtransform=input={trf}:tripod=1:crop=keep:interpol=bicubic:optzoom=0:zoom=0',
                    '-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', out], check=True)
    return out


def icon_overlays(timeline, final_t, total, events, icons, first_input):
    """ffmpeg overlay chains for the icons. Scoreboard icons pop (scale 1 -> 1.3 -> 1 over 0.3 s) on every vote for their
    side and fade out under the FINAL dim; the hook pair pops in beside MAYO / OR SAND?; the FINAL pair beside the count."""
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    t_on = hook_end
    pop = lambda times, amp=0.3, d=0.3: '+'.join([f"{amp}*sin(PI*(t-{ti:.3f})/{d})*between(t,{ti:.3f},{ti + d:.3f})" for ti in times]) or '0'
    places = []  # (icon, height, centre x, centre y, start, end, pop times, fade in, fade out)
    for side, ic in (('M', 'jar'), ('S', 'castle')):
        hits_t = [t for t, sd in events if sd == side]
        places.append((ic, ICON_H, XS[side] + ICON_DX, PY + ICON_DY, t_on, final_t + 0.15, hits_t, None, final_t))
    places.append(('jar', 220, 400, 705, 0.10, hook_end, [0.10], 0.10, hook_end - 0.12))       # under the hook, left
    places.append(('castle', 220, 680, 705, 0.30, hook_end, [0.30], 0.30, hook_end - 0.12))    # under the hook, right
    places.append(('jar', 250, 170, 1280, final_t + 0.36, total, [final_t + 0.36], final_t + 0.36, None))
    places.append(('castle', 250, 910, 1280, final_t + 0.48, total, [final_t + 0.48], final_t + 0.48, None))
    inputs, chains = [], []
    for k, (ic, hgt, x, y, t0, t1, pts, fi, fo) in enumerate(places):
        inputs += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', icons[ic]]
        fx = f",fade=t=in:st={fi:.3f}:d=0.15:alpha=1" if fi is not None else ""
        fx += f",fade=t=out:st={fo:.3f}:d=0.15:alpha=1" if fo is not None else ""
        chains.append((f"[{first_input + k}:v]format=rgba,scale=w=-2:h='{hgt}*(1+{pop(pts)})':eval=frame:flags=lanczos{fx}[ic{k}]",
                       f"overlay=x='{x}-w/2':y='{y}-h/2':eval=frame:enable='between(t,{t0:.3f},{t1:.3f})'", k))
    return inputs, chains


def rrect(w, h, r):
    k = r * 0.45
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def build_ass(timeline, total, final_t):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,7,4,2,70,70,610,1
Style: Hook,Inter Display Black,124,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,9,5,8,60,60,330,1
Style: Tag,Inter Display Bold,34,&H00FFFFFF,&H00FFFFFF,&H66000000,&H66000000,0,0,0,0,100,100,4,0,3,14,0,8,80,80,290,1
Style: Box,Inter Display Black,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,6,7,0,0,0,1
Style: Lbl,Inter Display Black,34,{INK},{INK},&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,8,0,0,0,1
Style: Num,Inter Display Black,96,&H00FFFFFF,&H00FFFFFF,{NAVY},&H00000000,0,0,0,0,100,100,0,0,1,6,0,5,0,0,0,1
Style: Final,Inter Display Black,104,&H00753304,&H00753304,&H003FD2FF,&H003FD2FF,0,0,0,0,100,100,4,0,3,12,0,8,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    L = [f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,120)}}MAYO\\N{{\\c{YEL}}}OR SAND?",
         f"Dialogue: 1,{ts(0.15)},{ts(hook_end)},Tag,,0,0,0,,{{\\fad(150,120)}}THROWBACK · MILA'S MULLIGANS 2025"]
    # scoreboard (v2): two navy pills with a white edge, the label in its own colour (mayo cream, sand), the icon on the
    # left (an ffmpeg overlay, see icon_overlays) and the count on the right; up from the first answer's first frame at 0-0
    pw, ph, py, xs = PW, PH, PY, XS
    t_on = hook_end
    for side, lc, lbl in (('M', MAYO, 'MAYO'), ('S', SAND, 'SAND')):
        x = xs[side]
        L.append(f"Dialogue: 3,{ts(t_on)},{ts(total)},Box,,0,0,0,,{{\\pos({x},{py})\\1c{NAVY}\\3c&HFFFFFF&\\bord5\\shad6\\p1}}{rrect(pw, ph, 36)}")
        L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Lbl,,0,0,0,,{{\\an8\\pos({x + NUM_DX},{py + 18})\\1c{lc}}}{lbl}")
    cx = {s: xs[s] + NUM_DX for s in xs}
    cy = py + 122
    num = lambda t0, t1, side, tags, val: L.append(
        f"Dialogue: 5,{ts(t0)},{ts(t1)},Num,,0,0,0,,{{\\an5\\pos({cx[side]},{cy}){tags}}}{val}")
    events = sorted((src_to_out(timeline, c, t), side) for c, t, side in VOTES)
    sc = {'M': 0, 'S': 0}
    for s in 'MS':
        num(t_on, events[0][0], s, "", 0)
    bump = rf"\1c{YEL}\fscx155\fscy155\frz-8\t(0,170,\fscx100\fscy100\frz0)\t(280,560,\1c&HFFFFFF&)"
    for i, (t, side) in enumerate(events):
        sc[side] += 1
        nxt = events[i + 1][0] if i + 1 < len(events) else final_t
        for s in 'MS':
            num(t, nxt, s, bump if s == side else "", sc[s])
    m, s_ = sc['M'], sc['S']
    tie = m == s_
    for s in 'MS':  # at FINAL: both numbers mustard on a tie, otherwise the winner mustard and the loser dimmed
        win = tie or sc[s] == max(m, s_)
        num(final_t, total, s, rf"\1c{YEL}\t(0,140,\fscx130\fscy130)\t(140,260,\fscx100\fscy100)" if win else r"\1a&H90&\3a&H90&", sc[s])
    hc = round(H * 0.58)
    L.append(f"Dialogue: 9,{ts(final_t)},{ts(total)},Box,,0,0,0,,{{\\pos(0,0)\\1c&H000000&\\1a&H68&\\shad0\\fad(150,0)\\p1}}m 0 0 l {W} 0 l {W} {H} l 0 {H}")

    def pop(delay):
        return rf"\fscx0\fscy0\t({delay},{delay + 150},\fscx112\fscy112)\t({delay + 150},{delay + 250},\fscx100\fscy100)"
    verdict = "IT'S A TIE" if tie else ("MAYO" if m > s_ else "SAND")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Final,,0,0,0,,{{\\an5\\pos({W // 2},{hc - 240}){pop(0)}}}FINAL")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Cap,,0,0,0,,{{\\an5\\pos({W // 2},{hc - 60})\\fs100\\bord8{pop(120)}}}{verdict}")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Num,,0,0,0,,{{\\an5\\pos({W // 2},{hc + 160})\\fs250\\1c{YEL}\\3c{NAVY}\\bord12\\shad6{pop(240)}}}{max(m, s_)}–{min(m, s_)}")
    # word-timed captions: whole phrases of up to four words / 15 letters, the spoken word in yellow, each phrase pops in
    for seg in timeline:
        mu = mute_for(seg)
        ws = [w for w in seg['words'] if not mu or w['s'] < mu]; chunks, cur = [], []
        for w in ws:
            wl = len(w['w'].strip().rstrip('.,?!'))
            if cur and (len(cur) == 4 or sum(len(x['w'].strip().rstrip('.,?!')) + 1 for x in cur) + wl > 15):
                chunks.append(cur); cur = []
            cur.append(w)
            if w['w'].strip().endswith(('.', '?', '!', ',')):
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        for ci, ch in enumerate(chunks):
            c_end = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else (mu or seg['out'])
            for wi, w in enumerate(ch):
                st = seg['t0'] + max(w['s'], seg['in']) - seg['in']
                en = seg['t0'] + min(ch[wi + 1]['s'] if wi + 1 < len(ch) else c_end, seg['out']) - seg['in']
                en = min(en, seg['t0'] + seg['out'] - seg['in'] - 1 / 30)
                if seg['hook'] or en <= st:
                    continue
                parts = [(rf"{{\c{YEL}}}" + x['w'].strip().upper().rstrip('.,') + r"{\c&HFFFFFF&}") if j == wi
                         else x['w'].strip().upper().rstrip('.,') for j, x in enumerate(ch)]
                pre = r"{\fscx82\fscy82\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{pre}{' '.join(parts)}")
    return head + "\n".join(L) + "\n"


def main():
    timeline, t, prev = [], 0.0, None
    for clip, a, b, cx, hook, stab in CUTS:
        if prev and prev[0] == clip and abs(a - prev[1]) < 0.05:
            a = prev[1]
        b = a + round((b - a) * 30) / 30
        prev = (clip, b)
        timeline.append({'clip': clip, 'in': a, 'out': b, 'cx': cx, 'hook': hook, 'stab': stab, 't0': t, 'words': words_for(clip, a, b)})
        t += b - a
    total = t
    last = timeline[-1]; mu = mute_for(last)
    final_t = last['t0'] + (mu - last['in']) if mu else total
    json.dump(timeline, open(os.path.join(OUT, f'timeline_{V}.json'), 'w'), indent=1)
    inputs, fl, k = [], [], 0
    for i, seg in enumerate(timeline):
        d = seg['out'] - seg['in']
        src = ['-ss', f"{seg['in']:.3f}", '-to', f"{seg['out']:.3f}", '-i', os.path.join(RAW, seg['clip'] + '.mp4')]
        if seg['stab']:
            inputs += ['-t', f'{d:.3f}', '-i', stabilize(seg['clip'], seg['in'], seg['out'])] + src
            vi, ai, z = k, k + 1, STAB_ZOOM; k += 2
        else:
            inputs += src
            vi = ai = k; z = 1.0; k += 1
        cw, ch = round(608 / z), round(1080 / z)
        x = min(max(seg['cx'] - cw // 2, 0), 1920 - cw)
        y = min(max(round(1080 * YFRAC) - ch // 2, 0), 1080 - ch)
        nf = round(d * 30)
        fl.append(f"[{vi}:v:0]crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,fps=30,setsar=1,trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
        fl.append(f"[{ai}:a:0]aresample=48000,aformat=channel_layouts=stereo,atrim=end={d:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.025:.3f}:d=0.025"
                  + (f",afade=t=out:st={mute_for(seg) - seg['in'] - 0.03:.3f}:d=0.04" if mute_for(seg) else "") + f"[a{i}]")
    n = len(timeline)
    fl.append(''.join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][dry0]")
    fl.append("[dry0]asplit=2[dry][dryw]")
    # Sound (stand-ins until the kit's cute_pop.wav / vine_boom.wav are reachable): a pop on every scoreboard change,
    # 6 dB under the voice it lands on; a boom 0.15 s ahead of FINAL at the reel's loudest answer level, plus a pop 6 dB under it.
    pa, psr = wav(os.path.join(SFX, 'pop.wav')); pop_db = float(loudest_db(pa, psr))
    ba, bsr = wav(os.path.join(SFX, 'boom.wav')); boom_db = float(loudest_db(ba, bsr))
    hits, vdb = [], []
    for c, tt, side in VOTES:
        v = voice_db(c, word_at(c, tt)); vdb.append(v)
        hits.append((src_to_out(timeline, c, tt), 'pop', round(v - POP_UNDER_VOICE - pop_db, 1), round(v, 1)))
    loud = max(vdb)
    hits += [(final_t - 0.15, 'boom', round(loud - boom_db, 1), round(loud, 1)),
             (final_t, 'pop', round(loud - POP_UNDER_VOICE - pop_db, 1), round(loud, 1))]
    for j, (at, snd, db, _) in enumerate(hits):
        inputs += ['-i', os.path.join(SFX, snd + '.wav')]
        ms = round(at * 1000)
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB,adelay={ms}|{ms}[s{j}]"); k += 1
    fl.append('[dry]' + ''.join(f'[s{j}]' for j in range(len(hits))) + f"amix=inputs={len(hits) + 1}:normalize=0:duration=first[ac0]")
    fl.append("[ac0]asplit=2[ac][acw]")
    json.dump([{'t': round(a, 3), 'sound': s_, 'gain_dB': d, 'voice_dBFS': vv} for a, s_, d, vv in hits],
              open(os.path.join(OUT, f'sfx_{V}.json'), 'w'), indent=1)
    ass = os.path.join(OUT, f'captions_{V}_916.ass')
    open(ass, 'w').write(build_ass(timeline, total, final_t))
    fl.append(f"[vc]subtitles={ass}[vs0]")
    events = sorted((src_to_out(timeline, c, tt), side) for c, tt, side in VOTES)
    ic_in, chains = icon_overlays(timeline, final_t, total, events, make_icons(OUT), k)
    inputs += ic_in
    last_v = 'vs0'
    for pre, ov, j in chains:
        fl.append(pre)
        fl.append(f"[{last_v}][ic{j}]{ov}[vs{j + 1}]"); last_v = f'vs{j + 1}'
    fl.append(f"[{last_v}]format=yuv420p[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_{V}_916.mp4')
    # dry and wet mixes as WAV too, before loudness: wet minus dry is the sound effects alone, for qa_pops.py
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out,
                    '-map', '[dryw]', '-c:a', 'pcm_f32le', os.path.join(OUT, f'mix_dry_{V}.wav'),
                    '-map', '[acw]', '-c:a', 'pcm_f32le', os.path.join(OUT, f'mix_wet_{V}.wav')], check=True)
    print(out, f"{total:.2f}s", f"FINAL at {final_t:.2f}s")


main()
