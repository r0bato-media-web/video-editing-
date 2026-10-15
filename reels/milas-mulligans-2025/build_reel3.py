"""Reel 3: 'Guess the 50-50'. Twelve golfers from Mila's Mulligans 2025 guess what the 50-50 will reach, lowest to
highest. A raffle ticket at the top shows each guess as it's said, and a number line under it keeps a pin for every
guess. The real 2025 total isn't on file, so the reel doesn't reveal one: it ends on "What did it hit?" and asks
for guesses in the comments (Rob, 15 Oct 2026: "Make a third video now").

Built on build_reel2.py (whole-frame cuts, one static crop per cut on whoever holds the mic, word-timed captions,
the question over the last live shot with its sound muted, pops 6 dB under the voice they land on).

Who said what was checked by where the mic is and whose mouth moves on the number (contact sheets and full-res
zooms, 15 Oct 2026), and by voice pitch where two people stand close (jasmin_dad: 198 Hz blue cap, 142 Hz backwards
cap, 198 Hz teal glasses but a different face and glasses from the blue cap, interviewer 262 Hz).
Left out on purpose:
- jasmin_dad 18.88 "21-50" (bandana): the camera pans through the whole answer (up to 226 px/s); vidstab tripod
  mode left 146 to 827 px/s. Rule: if the camera swings through an answer, drop it.
- jasmin_dad 23.56 "I say 1,500" (backwards cap): the camera moves at 125-150 px/s on the word; two tries at
  stabilizing it each jumped 200+ px/s on "500". Dropped after the second try.
- The interviewer's repeats: interview2 17.40 "675.", jasmin_dad 21.74 "21-50", interview3 10.84 "Two, 3,000.",
  angel 87.18 "Last person said 675...", evan_darien_int 47.60 "Show me the money." Not guesses, and the piece
  never ends on the interviewer.
- angel 74.17 "There's about 80 golfers": a guess at the field size with no source.
Out points (v2, Rob, 15 Oct 2026: "you cut off people's answers too early"): each answer runs to the end of
that person's turn, the rest of the sentence, a sign-off ("Book it.", "That's my guess.") or a laugh, and stops
just before the interviewer's next word. v1 cut at the first dip in level after the number, which dropped
"That's my guess." and the $2,000 golfer's "And that's a great prize today for anybody who's involved in the 50-50."

Usage: python build_reel3.py <m25_dir> [version]        (9:16 only)
"""
import json, math, os, subprocess, sys, wave
import numpy as np

M = sys.argv[1]
V = sys.argv[2] if len(sys.argv) > 2 else 'v1'
RAW, TR, SFX = (os.path.join(M, d) for d in ('raw', 'transcripts', 'sfx'))
OUT = os.path.join(M, 'reel3'); os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920

# clip, in, out, 9:16 crop centre x (source px), hook?, guess (value for the number line, text on the ticket,
# a time inside the spoken number) or None. The ticket, its pin and its pop land on the first word of the number,
# the same frame its caption appears (v1 popped on the last word, up to 2 s after the caption).
CUTS = [
    ('random_guy',       1.70,  4.50, 1560, True,  None),                      # interviewer: how much do you think the 50-50 is going to get up to today?
    ('frankie',         32.58, 36.98, 1010, False, (575, '$575', 34.50)),      # navy polo, cap: 50-50 is going to be 5-75.
    ('interview2',      15.40, 16.76,  870, False, (675, '$675', 15.54)),      # navy polo, green cap: 675 dollars.
    ('frankie',         20.05, 23.05, 1080, False, (700, '$700', 21.72)),      # blue polo, pointing: I think the 50-50 is going to hit 700 bucks.
    ('frankie',         25.00, 30.30,  940, False, (725, '$725', 29.42)),      # black polo, beard: a little bit north of that just to be safe. 7.25.
    ('jasmin_bf',       18.55, 24.38,  650, False, (855, '$855', 21.08)),      # grey polo: My guess is the 50-50 is going to get up to $855.
    ('random_guy',       5.40, 10.16,  590, False, (1150, '$1,150', 8.54)),    # floral shirt, grey cap: I would say 1,150.
    ('jasmin_dad',       8.05, 10.96,  470, False, (2000, '$2,000', 9.32)),    # blue cap, dark glasses: I think it's going to be a split of $2,000, $1,000 each.
    ('jasmin_dad',      10.96, 15.40,  340, False, None),                      # same golfer: And that's a great prize today for anybody who's involved in the 50-50. (v2: steps left to x 120 on "involved" and back while the tree behind holds still; own static crop from the sentence break)
    ('jasmin_dad',      26.18, 27.40,  900, False, (2300, '$2,300', 26.56)),   # light-blue cap, teal glasses: 2,300.
    ('interview3',       8.95, 10.72,  530, False, (2500, '$2–3K', 9.94)),     # floral shirt, glasses: Couple, two, 3,000.
    ('angel',           83.25, 87.05, 1410, False, (5000, '$5,000', 84.84)),   # pink floral shirt: maybe five grand, hopefully.
    ('evan_darien_int', 38.40, 42.64, 1000, False, (7000, '$7,000', 41.52)),   # white top, sunglasses: I hope it gets up to, I don't know, $7,000.
    ('evan_darien_int', 43.55, 49.40,  700, False, (11000, '$11,000', 45.90)), # navy jacket: And I'm going to go with $11,000.
]
# The last shot plays on live under the question; its sound fades after the laugh, before the interviewer's "Show me the money."
MUTE = {('evan_darien_int', 43.55): 47.30}
# caption text for numbers as whisper wrote them, so the caption reads like the ticket
SAY = {'5-75.': '575', '7.25.': '725'}
YFRAC = 0.42
POP_UNDER_VOICE = 6.0
AUDIO_DIRS = ('audio', 'audio2')

YEL, NAVY, INK, WHITE = r"&H3FD2FF&", r"&H753304&", r"&H51311E&", r"&HFFFFFF&"   # #FFD23F, Mila's navy #043375, ink #1E3151
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'

# ticket and number line geometry (output px)
TK_W, TK_H, TK_X, TK_Y = 760, 250, 160, 150     # ticket box, top-left
STUB = 170                                       # stub width on the left of the ticket
TK_CX = TK_X + STUB + (TK_W - STUB) // 2         # centre of the ticket's main area
NL_X0, NL_X1, NL_Y = 120, 960, 470               # number line ends and centre line
NL_LO, NL_HI = 400, 14000                        # log scale range, dollars
TICKS = [(500, '$500'), (1000, '$1K'), (2000, '$2K'), (5000, '$5K'), (10000, '$10K')]


def nl_x(v):
    return round(NL_X0 + (math.log(v) - math.log(NL_LO)) / (math.log(NL_HI) - math.log(NL_LO)) * (NL_X1 - NL_X0))


def mute_for(seg):
    for (c, i), m in MUTE.items():
        if c == seg['clip'] and abs(i - seg['in']) < 0.05:
            return m
    return None


def all_words(clip):
    """Transcript words with whisper's split numbers joined back up ("5" + "-75." -> "5-75.", "$11" + ",000." -> "$11,000.")."""
    out = []
    for s in json.load(open(os.path.join(TR, clip + '.json'))):
        for w in s['words']:
            t = w['w'].strip()
            if out and t[:1] in '-,.' and t[1:2].isdigit() and out[-1]['w'].strip()[-1:].isdigit():
                out[-1] = {'w': out[-1]['w'] + t, 's': out[-1]['s'], 'e': w['e'], 'last': w['s']}
            else:
                out.append({'w': w['w'], 's': w['s'], 'e': w['e'], 'last': w['s']})
    return out


def words_for(clip, a, b):
    return [w for w in all_words(clip) if w['s'] >= a - 0.02 and w['s'] < b - 0.05]


def num_start(clip, t):
    """Start of the (joined) number word that t falls in."""
    return next(x for x in all_words(clip) if x['s'] - 0.02 <= t < x['e'])['s']


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
    k = max(1, int(sr * win))
    if len(a) < k:
        return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)
    c = np.convolve(a ** 2, np.ones(k) / k, mode='valid')
    return 10 * np.log10(c.max() + 1e-12)


def voice_db(clip, t):
    """Loudest 50 ms of the voice in the 0.4 s from t, in dBFS: the stretch the pop lands on (the same window
    qa_pops.py measures). Measuring the whole joined number put three pops level with or over the voice in v1."""
    path = next(p for p in (os.path.join(M, d, clip + '.wav') for d in AUDIO_DIRS) if os.path.exists(p))
    a, sr = wav(path)
    return float(loudest_db(a[int(t * sr):int((t + 0.4) * sr)], sr))


def make_ticket(out_dir, s=4):
    """A raffle ticket TK_W x TK_H: yellow, a navy stub with 50-50 on it, a perforation, round notches at both ends,
    an ink outline and a soft shadow. Drawn here; no clip art, no brand."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    pad = 24
    size = ((TK_W + 2 * pad) * s, (TK_H + 2 * pad) * s)
    P = lambda *v: [round((c + pad) * s) for c in v]
    ink, navy, yel, cream = (30, 49, 81, 255), (4, 51, 117, 255), (255, 210, 63, 255), (255, 243, 196, 255)
    tk = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(tk)
    d.rounded_rectangle(P(0, 0, TK_W, TK_H), radius=22 * s, fill=yel)
    d.rounded_rectangle(P(0, 0, STUB, TK_H), radius=22 * s, fill=navy)
    d.rectangle(P(STUB - 30, 0, STUB, TK_H), fill=navy)
    d.rounded_rectangle(P(STUB + 18, 16, TK_W - 16, TK_H - 16), radius=12 * s, outline=navy, width=round(4 * s))  # inner frame
    for y in range(10, TK_H - 6, 18):
        d.ellipse(P(STUB - 4, y, STUB + 4, y + 8), fill=(0, 0, 0, 0))                           # perforation holes
    for cx in (0, TK_W):
        d.ellipse(P(cx - 20, TK_H / 2 - 20, cx + 20, TK_H / 2 + 20), fill=(0, 0, 0, 0))          # notches
    f = ImageFont.truetype(FONT, round(58 * s))
    lab = Image.new('RGBA', (round(TK_H * s), round(STUB * s)), (0, 0, 0, 0))
    ImageDraw.Draw(lab).text((lab.size[0] / 2, lab.size[1] / 2), '50-50', font=f, fill=cream, anchor='mm')
    lab = lab.rotate(90, expand=True)
    tk.alpha_composite(lab, (pad * s, pad * s))
    a = tk.split()[3]
    ring = a.filter(ImageFilter.MaxFilter(2 * round(3.5 * s / 2) + 1))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    sh = Image.new('RGBA', size, (0, 0, 0, 0)); sh.putalpha(ring.point(lambda v: v * 0.45))
    sh = sh.filter(ImageFilter.GaussianBlur(4 * s)).transform(size, Image.AFFINE, (1, 0, -3 * s, 0, 1, -6 * s))
    out.alpha_composite(sh)
    ol = Image.new('RGBA', size, ink); ol.putalpha(ring); out.alpha_composite(ol)
    out.alpha_composite(tk)
    out = out.resize((size[0] // s, size[1] // s), Image.LANCZOS)
    p = os.path.join(out_dir, 'ticket.png'); out.save(p)
    return p, pad


def circle(r):
    k = r * 0.5523
    return (f"m 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} b {-k} {r} {-r} {k} {-r} 0 "
            f"b {-r} {-k} {-k} {-r} 0 {-r}")


def rrect(w, h, r):
    k = r * 0.45
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def build_ass(timeline, total, final_t, guesses):
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
Style: Lbl,Inter Display Black,34,{INK},{INK},&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,5,0,0,0,1
Style: Amt,Inter Display Black,118,{NAVY},{NAVY},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Tick,Inter Display Black,36,&H00FFFFFF,&H00FFFFFF,{NAVY},&H66000000,0,0,0,0,100,100,1,0,1,4,2,8,0,0,0,1
Style: Final,Inter Display Black,96,&H00753304,&H00753304,&H003FD2FF,&H003FD2FF,0,0,0,0,100,100,4,0,3,12,0,5,0,0,0,1
Style: Big,Inter Display Black,132,{YEL},{YEL},{NAVY},&H99000000,0,0,0,0,100,100,0,0,1,11,6,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    L = [f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,120)}}GUESS THE\\N{{\\c{YEL}}}50-50",
         f"Dialogue: 1,{ts(0.15)},{ts(hook_end)},Tag,,0,0,0,,{{\\fad(150,120)}}THROWBACK · MILA'S MULLIGANS 2025"]
    t_on = hook_end
    # number line: a navy bar with a white edge, a tick and a label at $500 / $1K / $2K / $5K / $10K
    L.append(f"Dialogue: 3,{ts(t_on)},{ts(total)},Box,,0,0,0,,{{\\pos({NL_X0 - 18},{NL_Y - 9})\\1c{NAVY}\\3c{WHITE}\\bord4\\shad4\\fad(150,0)\\p1}}{rrect(NL_X1 - NL_X0 + 36, 18, 9)}")
    for v, lab in TICKS:
        x = nl_x(v)
        L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Box,,0,0,0,,{{\\pos({x - 2},{NL_Y - 6})\\1c{WHITE}\\shad0\\fad(150,0)\\p1}}m 0 0 l 4 0 l 4 12 l 0 12")
        L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Tick,,0,0,0,,{{\\an8\\pos({x},{NL_Y + 22})\\fad(150,0)}}{lab}")
    # one pin per guess: pops in yellow and big on the word, then stays as a smaller white pin
    for i, (t, v, txt) in enumerate(guesses):
        x = nl_x(v)
        nxt = guesses[i + 1][0] if i + 1 < len(guesses) else final_t
        L.append(f"Dialogue: 6,{ts(t)},{ts(nxt)},Box,,0,0,0,,{{\\pos({x},{NL_Y})\\1c{YEL}\\3c{NAVY}\\bord5\\shad3"
                 rf"\fscx0\fscy0\t(0,150,\fscx130\fscy130)\t(150,260,\fscx100\fscy100)\p1}}{circle(22)}")
        L.append(f"Dialogue: 5,{ts(nxt)},{ts(total)},Box,,0,0,0,,{{\\pos({x},{NL_Y})\\1c{WHITE}\\3c{NAVY}\\bord4\\shad2\\p1}}{circle(13)}")
    # ticket text: "GUESS #n" and "$ ?" until the number is said, then the number pops in
    ty = TK_Y + TK_H // 2
    bump = r"\fscx0\fscy0\t(0,150,\fscx118\fscy118)\t(150,260,\fscx100\fscy100)"
    starts = [s['t0'] for s in timeline if s['guess']]
    for i, (t, v, txt) in enumerate(guesses):
        c0 = starts[i]
        nxt = starts[i + 1] if i + 1 < len(starts) else final_t
        L.append(f"Dialogue: 7,{ts(c0)},{ts(nxt)},Lbl,,0,0,0,,{{\\pos({TK_CX},{TK_Y + 52})}}GUESS #{i + 1}")
        if t - c0 > 0.05:
            L.append(f"Dialogue: 7,{ts(c0)},{ts(t)},Amt,,0,0,0,,{{\\pos({TK_CX},{ty + 22})\\1a&H70&}}$ ?")
        fs = 118 if len(txt) <= 6 else 104
        L.append(f"Dialogue: 7,{ts(t)},{ts(nxt)},Amt,,0,0,0,,{{\\pos({TK_CX},{ty + 22})\\fs{fs}{bump}}}{txt}")
    L.append(f"Dialogue: 7,{ts(final_t)},{ts(total)},Lbl,,0,0,0,,{{\\pos({TK_CX},{TK_Y + 52})}}THE REAL TOTAL")
    L.append(f"Dialogue: 7,{ts(final_t)},{ts(total)},Amt,,0,0,0,,{{\\pos({TK_CX},{ty + 22}){bump}}}$ ???")
    # the question over the last live shot: dim, then the lines pop in one after another
    L.append(f"Dialogue: 9,{ts(final_t)},{ts(total)},Box,,0,0,0,,{{\\pos(0,0)\\1c&H000000&\\1a&H68&\\shad0\\fad(150,0)\\p1}}m 0 0 l {W} 0 l {W} {H} l 0 {H}")

    def pop(delay):
        return rf"\fscx0\fscy0\t({delay},{delay + 150},\fscx112\fscy112)\t({delay + 150},{delay + 250},\fscx100\fscy100)"
    lo, hi = guesses[0][2], guesses[-1][2]
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Final,,0,0,0,,{{\\an5\\pos({W // 2},780){pop(0)}}}{len(guesses)} GUESSES")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Cap,,0,0,0,,{{\\an5\\pos({W // 2},930)\\fs88\\bord8{pop(120)}}}{lo} TO {hi}")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Big,,0,0,0,,{{\\an5\\pos({W // 2},1140){pop(260)}}}WHAT DID\\NIT HIT?")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Tag,,0,0,0,,{{\\an5\\pos({W // 2},1350)\\fs46{pop(420)}}}COMMENT YOUR GUESS")
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
                say = lambda x: SAY.get(x['w'].strip(), x['w'].strip()).upper().rstrip('.,')
                parts = [(rf"{{\c{YEL}}}" + say(x) + r"{\c&HFFFFFF&}") if j == wi else say(x) for j, x in enumerate(ch)]
                pre = r"{\fscx82\fscy82\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{pre}{' '.join(parts)}")
    return head + "\n".join(L) + "\n"


def main():
    timeline, t, prev = [], 0.0, None
    for clip, a, b, cx, hook, guess in CUTS:
        if prev and prev[0] == clip and abs(a - prev[1]) < 0.05:
            a = prev[1]   # a reframe within one answer continues from the frame the last cut ended on
        b = a + round((b - a) * 30) / 30
        prev = (clip, b)
        timeline.append({'clip': clip, 'in': a, 'out': b, 'cx': cx, 'hook': hook, 'guess': guess, 't0': t, 'words': words_for(clip, a, b)})
        t += b - a
    total = t
    last = timeline[-1]; mu = mute_for(last)
    final_t = last['t0'] + (mu - last['in']) if mu else total
    for s in timeline:
        if s['guess']:
            s['at'] = num_start(s['clip'], s['guess'][2])
    guesses = [(src_to_out(timeline, s['clip'], s['at']), s['guess'][0], s['guess'][1]) for s in timeline if s['guess']]
    json.dump(timeline, open(os.path.join(OUT, f'timeline_{V}.json'), 'w'), indent=1)
    inputs, fl, k = [], [], 0
    for i, seg in enumerate(timeline):
        d = seg['out'] - seg['in']
        inputs += ['-ss', f"{seg['in']:.3f}", '-to', f"{seg['out']:.3f}", '-i', os.path.join(RAW, seg['clip'] + '.mp4')]
        cw, ch = 608, 1080
        x = min(max(seg['cx'] - cw // 2, 0), 1920 - cw)
        nf = round(d * 30)
        fl.append(f"[{k}:v:0]crop={cw}:{ch}:{x}:0,scale={W}:{H}:flags=lanczos,fps=30,setsar=1,trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
        fl.append(f"[{k}:a:0]aresample=48000,aformat=channel_layouts=stereo,atrim=end={d:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.025:.3f}:d=0.025"
                  + (f",afade=t=out:st={mute_for(seg) - seg['in'] - 0.03:.3f}:d=0.04" if mute_for(seg) else "") + f"[a{i}]")
        k += 1
    n = len(timeline)
    fl.append(''.join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][dry0]")
    fl.append("[dry0]asplit=2[dry][dryw]")
    # Sound (stand-ins until the kit's cute_pop.wav / vine_boom.wav are reachable): a pop on every guess as the ticket
    # shows it, 6 dB under the voice it lands on; a boom 0.15 s ahead of the question at the loudest guess's level,
    # plus a pop 6 dB under it.
    pa, psr = wav(os.path.join(SFX, 'pop.wav')); pop_db = float(loudest_db(pa, psr))
    ba, bsr = wav(os.path.join(SFX, 'boom.wav')); boom_db = float(loudest_db(ba, bsr))
    hits, vdb = [], []
    for seg in timeline:
        if seg['guess']:
            v = voice_db(seg['clip'], seg['at']); vdb.append(v)
            hits.append((src_to_out(timeline, seg['clip'], seg['at']), 'pop', round(v - POP_UNDER_VOICE - pop_db, 1), round(v, 1)))
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
    # the ticket sits under the subtitles, so its text draws on top of it
    tpng, pad = make_ticket(OUT)
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    inputs += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', tpng]
    fl.append(f"[{k}:v]format=rgba,fade=t=in:st={hook_end:.3f}:d=0.15:alpha=1[tk]"); k += 1
    fl.append(f"[vc][tk]overlay=x={TK_X - pad}:y={TK_Y - pad}:enable='gte(t,{hook_end:.3f})'[vt]")
    ass = os.path.join(OUT, f'captions_{V}_916.ass')
    open(ass, 'w').write(build_ass(timeline, total, final_t, guesses))
    fl.append(f"[vt]subtitles={ass},format=yuv420p[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_{V}_916.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out,
                    '-map', '[dryw]', '-c:a', 'pcm_f32le', os.path.join(OUT, f'mix_dry_{V}.wav'),
                    '-map', '[acw]', '-c:a', 'pcm_f32le', os.path.join(OUT, f'mix_wet_{V}.wav')], check=True)
    print(out, f"{total:.2f}s", f"question at {final_t:.2f}s", f"{len(guesses)} guesses")


main()
