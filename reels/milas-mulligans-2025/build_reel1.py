"""Reel 1 v16: 'Is a hot dog a sandwich?' punched up. v4 starts cut 4 on 'disagree' (Rob OK, 7 Oct 2026).


Usage: python build_reel1_v2.py <m25_dir> <916|169>
"""
import json, os, subprocess, sys

M, SHAPE = sys.argv[1], sys.argv[2]
RAW, TR, OUT = (os.path.join(M, d) for d in ('raw', 'transcripts', 'reel1'))
W, H = (1080, 1920) if SHAPE == '916' else (1920, 1080)

# clip, in, out, 9:16 centre x, zoom, unused, hook?
# v8 (Rob, 8 Oct 2026: "video froze at 5 seconds"): no frozen frames anywhere. The sunglasses answer is cut (it needed a
# hold to hide a camera pan); the ending plays the driver's shot on live under FINAL with the interviewer's next words muted.
CUTS = [
    ('int_darryl',      15.00, 17.85, 1360, 1.0, None, True),        # Ava: is a hot dog a sandwich or not? (steady, facing camera)
    ('int_ant',         16.00, 16.56, 560, 1.0, None, False),        # Yes. (pink shirt, white cap: mic on him, mouth open on the word)
    ('int_ant',         16.96, 17.50, 780, 1.0, None, False),        # No. (navy shirt, mic on him)
    ('int_ant',         17.50, 17.93, 1060, 1.0, None, False),       # No. (floral shirt: his mouth on the word, a higher voice than navy's)
    ('int_ant',         17.93, 18.40, 1390, 1.0, None, False),       # Yes. (white shirt, far right: his mouth on the word, a third voice)
    ('int_darryl',      35.29, 37.59, 860, 1.0, None, False),        # A hot dog in my book is
    ('int_darryl',      37.59, 39.22, 820, 1.15, None, False),       # NOT a sandwich. It's a hot dog. (punch-in)
    ('int_hotdog',      43.60, 44.06, 1000, 1.0, None, False),       # No, (black-cap friend: her voice, ~188 Hz)
    ('int_hotdog',      44.06, 45.16, 760, 1.0, None, False),        # not a sandwich (trucker cap, first cart: a lower voice)
    ('int_hotdog',      56.64, 57.16, 660, 1.0, None, False),        # No, (trucker cap; her mouth, mic on her)
    ('int_hotdog',      57.16, 57.72, 980, 1.0, None, False),        # it's (driver: mic moves to her, her mouth moves)
    ('int_hotdog',      57.72, 60.45, 980, 1.15, None, False),       # DEFINITELY not a sandwich (driver punch-in), plays on live under FINAL, sound faded
]
MUTE = {('int_hotdog', 57.72): 58.95}  # fade after the driver's closing "No" (her mouth, her voice); the interviewer's "all right" (58.98) is never heard
HOLD = 0.0


def mute_for(seg):
    for (c, i), m in MUTE.items():
        if c == seg['clip'] and abs(i - seg['in']) < 0.05:
            return m
    return None
# One vote per person, keyed to the word that casts it: (clip, word start, side)
VOTES = [
    ('int_ant', 16.18, 'S'),   # pink shirt
    ('int_ant', 17.08, 'N'),   # navy shirt
    ('int_ant', 17.60, 'N'),   # floral shirt
    ('int_ant', 18.10, 'S'),   # white shirt (four golfers, four answers: "split answers")
    ('int_darryl', 37.61, 'N'),
    ('int_hotdog', 43.64, 'N'),   # black-cap friend, first cart
    ('int_hotdog', 44.12, 'N'),   # trucker cap, first cart
    ('int_hotdog', 56.68, 'N'),   # trucker cap, second cart: "No,"
    ('int_hotdog', 57.98, 'N'),   # driver: "definitely NOT a sandwich"
]
# Caption groups start fresh on these words so each group reads as a phrase
BREAK_BEFORE = {('int_darryl', 36.19), ('int_hotdog', 57.98)}
# Vertical crop centre (fraction of frame height) where the speaker sits low; default 0.42
YFRAC = {}


def words_for(clip, a, b):
    return [w for s in json.load(open(os.path.join(TR, clip + '.json'))) for w in s['words']
            if w['s'] >= a - 0.02 and w['s'] < b - 0.05]  # any word that starts inside the cut


def ts(t):
    t = int(t * 100 + 1e-6) / 100  # round down to the centisecond, so nothing hangs onto the next shot's first frame
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def src_to_out(timeline, clip, t):
    for seg in timeline:
        if seg['clip'] == clip and seg['in'] <= t < seg['out']:
            return seg['t0'] + t - seg['in']
    return None


YEL, NAVY = r"&H3FD2FF&", r"&H753304&"   # accent yellow #FFD23F, Mila's navy #043375 (flyer)


def rrect(w, h, r):
    """ASS vector path for a w x h rounded rectangle, top-left at 0,0."""
    k = r * 0.45
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def build_ass(timeline, total):
    v = SHAPE == '916'
    k = 1.0 if v else 0.8          # type scale for 16:9
    cap_fs, cap_mv = (92, 610) if v else (70, 120)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Black,{cap_fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,{round(7 * k)},{round(4 * k)},2,70,70,{cap_mv},1
Style: Hook,Inter Display Black,{round(124 * k)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,{round(9 * k)},{round(5 * k)},8,60,60,{330 if v else 110},1
Style: Tag,Inter Display Bold,{round(34 * k)},&H00FFFFFF,&H00FFFFFF,&H66000000,&H66000000,0,0,0,0,100,100,4,0,3,{round(14 * k)},0,8,80,80,{290 if v else 70},1
Style: Box,Inter Display Black,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,{round(6 * k)},7,0,0,0,1
Style: Lbl,Inter Display Bold,{round(30 * k)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,8,0,0,0,1
Style: Num,Inter Display Black,{round(84 * k)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,0,1
Style: Final,Inter Display Black,{round(60 * k)},{'&H00753304'},&H00753304,&H003FD2FF,&H003FD2FF,0,0,0,0,100,100,4,0,3,{round(12 * k)},0,8,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    L = [f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,120)}}IS A HOT DOG\\N{{\\c{YEL}}}A SANDWICH?",
         f"Dialogue: 1,{ts(0.15)},{ts(hook_end)},Tag,,0,0,0,,{{\\fad(150,120)}}THROWBACK · MILA'S MULLIGANS 2025"]
    # scoreboard: a hot dog. Golden bun, the score on the sausage, a mustard squiggle down its length.
    # The number that changes flashes mustard and settles to white; FINAL turns the winner mustard and dims the loser.
    last = timeline[-1]; mute = mute_for(last)
    final_t = last['t0'] + (mute - last['in']) if mute else total - HOLD
    events = sorted((src_to_out(timeline, c, t), side) for c, t, side in VOTES if src_to_out(timeline, c, t) is not None)
    BUN, BUN_DK, BUN_HI = r"&H5FB3E9&", r"&H3A83C2&", r"&H8ED0F6&"      # #E9B35F, #C2833A, #F6D08E
    DOG, DOG_HI, DOG_DK, BROWN = r"&H2C43B8&", r"&H5A70E0&", r"&H1A2370&", r"&H10346B&"  # #B8432C, #E0705A, #70231A, #6B3410
    bw, bh, sw, sh = round(780 * k), round(190 * k), round(880 * k), round(100 * k)
    py = 225 if v else 30
    bx, sx, sy = (W - bw) // 2, (W - sw) // 2, py + round(48 * k)
    cy = sy + sh // 2
    cxs, cxn = W // 2 - round(sw * 0.24), W // 2 + round(sw * 0.24)
    t_on = hook_end  # the hot dog is up from the first answer's first frame, at 0-0
    box = lambda layer, x, y, tags, path, end=None: L.append(
        f"Dialogue: {layer},{ts(t_on)},{ts(end or total)},Box,,0,0,0,,{{\\pos({x},{y}){tags}\\p1}}{path}")
    box(3, bx, py + round(9 * k), rf"\1c{BUN_DK}\shad0", rrect(bw, bh, bh // 2))                       # bun underside
    box(3, bx, py, rf"\1c{BUN}\shad{round(6 * k)}", rrect(bw, bh, bh // 2))                              # bun
    box(3, bx + round(40 * k), py + round(12 * k), rf"\1c{BUN_HI}\1a&H40&\shad0", rrect(bw - round(80 * k), round(16 * k), round(8 * k)))
    box(4, sx, sy, rf"\1c{DOG}\shad{round(3 * k)}", rrect(sw, sh, sh // 2))                              # sausage
    box(4, sx + round(60 * k), sy + round(12 * k), rf"\1c{DOG_HI}\1a&H50&\shad0", rrect(sw - round(120 * k), round(14 * k), round(7 * k)))
    import math
    amp, per, x0, x1 = 16 * k, 64 * k, sx + 70 * k, sx + sw - 70 * k
    pts = [(x0 + i * (x1 - x0) / 120, cy + amp * math.sin((x0 + i * (x1 - x0) / 120) / per * 2 * math.pi)) for i in range(121)]
    gap = 78 * k  # the mustard breaks around each number so the score reads clean
    segs, cur = [], []
    for x, y in pts:
        if min(abs(x - cxs), abs(x - cxn)) < gap:
            if len(cur) > 1: segs.append(cur)
            cur = []
        else:
            cur.append((x, y))
    if len(cur) > 1: segs.append(cur)
    sq = " ".join("m " + " l ".join(f"{x - sx:.1f} {y - sy:.1f}" for x, y in sg + sg[::-1]) for sg in segs)
    box(5, sx, sy, rf"\1a&HFF&\3c{YEL}\bord{round(6 * k)}\shad0", sq)                                    # mustard
    for cx, lbl in ((cxs, "SANDWICH"), (cxn, "NOT A SANDWICH")):
        L.append(f"Dialogue: 6,{ts(t_on)},{ts(total)},Lbl,,0,0,0,,{{\\an8\\pos({cx},{py + round(13 * k)})\\1c{BROWN}\\fs{round(30 * k)}\\fsp3\\fnInter Display Black}}{lbl}")
    num = lambda t0, t1, cx, tags, val: L.append(
        f"Dialogue: 7,{ts(t0)},{ts(t1)},Num,,0,0,0,,{{\\an5\\pos({cx},{cy})\\3c{DOG_DK}\\bord{round(5 * k)}\\fs{round(96 * k)}{tags}}}{val}")
    s = n = 0
    for cx in (cxs, cxn):
        num(t_on, events[0][0], cx, "", 0)
    for i, (t, side) in enumerate(events):
        s += side == 'S'; n += side == 'N'
        nxt = events[i + 1][0] if i + 1 < len(events) else final_t
        bump = rf"\1c{YEL}\fscx155\fscy155\frz-8\t(0,170,\fscx100\fscy100\frz0)\t(280,560,\1c&HFFFFFF&)"
        for cx, val, sd in ((cxs, s, 'S'), (cxn, n, 'N')):
            num(t, nxt, cx, bump if side == sd else "", val)
    # FINAL (Rob, 8 Oct 2026: "the final should pop up at the end BEFORE the end card"): the picture dims and a big
    # result card pops in the middle, one line after another, held on the driver's live shot until the dissolve.
    # The hot dog stays up top with the winner's number in mustard and the loser's dimmed.
    win = (cxn, n) if n >= s else (cxs, s); lose = (cxs, s) if n >= s else (cxn, n)
    num(final_t, total, win[0], rf"\1c{YEL}\t(0,140,\fscx130\fscy130)\t(140,260,\fscx100\fscy100)", win[1])
    num(final_t, total, lose[0], r"\1a&H90&\3a&H90&", lose[1])
    hc = round(H * 0.58)  # below the end card's cap, so the two never overlap in the dissolve
    L.append(f"Dialogue: 9,{ts(final_t)},{ts(total)},Box,,0,0,0,,{{\\pos(0,0)\\1c&H000000&\\1a&H68&\\shad0\\fad(150,0)\\p1}}m 0 0 l {W} 0 l {W} {H} l 0 {H}")
    def pop(delay):
        return rf"\fscx0\fscy0\t({delay},{delay + 150},\fscx112\fscy112)\t({delay + 150},{delay + 250},\fscx100\fscy100)"
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Final,,0,0,0,,{{\\an5\\pos({W // 2},{hc - round(240 * k)})\\fs{round(104 * k)}{pop(0)}}}FINAL")
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Cap,,0,0,0,,{{\\an5\\pos({W // 2},{hc - round(60 * k)})\\fs{round(100 * k)}\\bord{round(8 * k)}{pop(120)}}}"
             + ("NOT A SANDWICH" if n >= s else "SANDWICH"))
    L.append(f"Dialogue: 10,{ts(final_t)},{ts(total)},Num,,0,0,0,,{{\\an5\\pos({W // 2},{hc + round(160 * k)})\\fs{round(250 * k)}\\1c{YEL}\\3c{DOG_DK}\\bord{round(12 * k)}\\shad{round(6 * k)}{pop(240)}}}{max(n, s)}–{min(n, s)}")
    # word-timed captions: whole phrases, up to four words / 15 letters, the spoken word in yellow, each new pair pops in
    for seg in timeline:
        m = mute_for(seg)
        ws = [w for w in seg['words'] if not m or w['s'] < m]; chunks, cur = [], []
        for w in ws:
            wl = len(w['w'].strip().rstrip('.,?!'))
            if cur and (len(cur) == 4 or sum(len(x['w'].strip().rstrip('.,?!')) + 1 for x in cur) + wl > 15
                        or (seg['clip'], round(w['s'], 2)) in BREAK_BEFORE):
                chunks.append(cur); cur = []
            cur.append(w)
            if w['w'].strip().endswith(('.', '?', '!', ',')):
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        for ci, ch in enumerate(chunks):
            c_end = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else (m or seg['out'])
            for wi, w in enumerate(ch):
                st = seg['t0'] + max(w['s'], seg['in']) - seg['in']
                en = seg['t0'] + min(ch[wi + 1]['s'] if wi + 1 < len(ch) else c_end, seg['out']) - seg['in']
                en = min(en, seg['t0'] + seg['out'] - seg['in'] - 1 / 30)  # never spill into the next shot
                if seg['hook'] or en <= st:
                    continue  # the hook carries the question
                parts = [(rf"{{\c{YEL}}}" + x['w'].strip().upper().rstrip('.,') + r"{\c&HFFFFFF&}") if j == wi
                         else x['w'].strip().upper().rstrip('.,') for j, x in enumerate(ch)]
                pre = r"{\fscx82\fscy82\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{pre}{' '.join(parts)}")
    return head + "\n".join(L) + "\n"


def main():
    timeline, t = [], 0.0
    prev = None
    for clip, a, b, cx, z, vout, hook in CUTS:
        if prev and prev[0] == clip and abs(a - prev[1]) < 0.05:
            a = prev[1]  # back-to-back cuts from one clip: start exactly where the last one ended (no repeated frame)
        b = a + round((b - a) * 30) / 30  # whole frames, so picture, captions and tally stay in sync
        prev = (clip, b)
        timeline.append({'clip': clip, 'in': a, 'out': b, 'cx': cx, 'zoom': z, 'vout': vout, 'hook': hook, 't0': t,
                         'words': words_for(clip, a, b)})
        t += b - a
    total = t + HOLD
    json.dump(timeline, open(os.path.join(OUT, 'timeline_v16.json'), 'w'), indent=1)
    inputs, fl = [], []
    for i, seg in enumerate(timeline):
        inputs += ['-ss', f"{seg['in']:.3f}", '-to', f"{seg['out']:.3f}", '-i', os.path.join(RAW, seg['clip'] + '.mp4')]
        z = seg['zoom']
        if SHAPE == '916':
            cw, ch = round(608 / z), round(1080 / z)
            x = min(max(seg['cx'] - cw // 2, 0), 1920 - cw)
            y = min(max(round(1080 * YFRAC.get((seg['clip'], seg['in']), 0.42)) - ch // 2, 0), 1080 - ch)
        else:
            z16 = 1.3 * z  # 16:9 also leans in on whoever holds the mic
            cw, ch = round(1920 / z16), round(1080 / z16)
            x = min(max(seg['cx'] - cw // 2, 0), 1920 - cw)
            y = min(max(round(1080 * YFRAC.get((seg['clip'], seg['in']), 0.42)) - ch // 2, 0), 1080 - ch)
        nf = round((seg['out'] - seg['in']) * 30)
        held = 0
        if seg['vout']:  # freeze the last sharp frame; the sound keeps playing to `out`
            held = nf - round((seg['vout'] - seg['in']) * 30); nf -= held
        chain = f"[{i}:v:0]crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,fps=30,setsar=1,trim=end_frame={nf},setpts=PTS-STARTPTS"
        if held:
            chain += f",tpad=stop_mode=clone:stop_duration={held / 30:.4f}"
        fl.append(chain + f",format=yuv420p[v{i}]")
        d = seg['out'] - seg['in']
        fl.append(f"[{i}:a:0]aresample=48000,aformat=channel_layouts=stereo,atrim=end={d:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.025:.3f}:d=0.025" + (f",afade=t=out:st={mute_for(seg) - seg['in'] - 0.03:.3f}:d=0.04" if mute_for(seg) else "") + f"[a{i}]")
    n = len(timeline)
    fl.append(''.join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    ass = os.path.join(OUT, f'captions_v16_{SHAPE}.ass')
    open(ass, 'w').write(build_ass(timeline, total))
    fl.append(f"[vc]subtitles={ass}[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_v16_{SHAPE}.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
    print(out, f"{total:.2f}s")


main()
