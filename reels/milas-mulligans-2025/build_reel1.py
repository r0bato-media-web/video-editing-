"""Reel 1 v13: 'Is a hot dog a sandwich?' Cuts, static crops, hook, scoreboard tally and captions for the body.

Usage: python build_reel1.py <m25_dir> <916|169>
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
    ('int_hotdog',      43.60, 45.16, 820, 1.0, None, False),        # No, not a sandwich (trucker cap says all of it; friend in frame)
    ('int_hotdog',      56.64, 57.16, 660, 1.0, None, False),        # No, (trucker cap; her mouth, mic on her)
    ('int_hotdog',      57.16, 57.72, 980, 1.0, None, False),        # it's (driver: mic moves to her, her mouth moves)
    ('int_hotdog',      57.72, 59.70, 980, 1.15, None, False),       # DEFINITELY not a sandwich (driver punch-in), plays on live under FINAL, sound faded
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
    # scoreboard: navy panel, two columns, the number that changes pops in yellow and settles to white
    last = timeline[-1]; mute = mute_for(last)
    final_t = last['t0'] + (mute - last['in']) if mute else total - HOLD
    events = sorted((src_to_out(timeline, c, t), side) for c, t, side in VOTES if src_to_out(timeline, c, t) is not None)
    pw, ph = (round(760 * k), round(156 * k)); px, py = (W - pw) // 2, (225 if v else 36)
    cxs, cxn = px + pw // 4, px + 3 * pw // 4
    t_on = hook_end  # the board is up from the first answer's first frame, at 0-0
    L.append(f"Dialogue: 3,{ts(t_on)},{ts(total)},Box,,0,0,0,,{{\\pos({px},{py})\\1c{NAVY}\\1a&H18&\\p1}}{rrect(pw, ph, round(26 * k))}")
    L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Box,,0,0,0,,{{\\pos({W // 2 - 1},{py + round(22 * k)})\\1c&HFFFFFF&\\1a&H90&\\shad0\\p1}}m 0 0 l 3 0 l 3 {ph - round(44 * k)} l 0 {ph - round(44 * k)}")
    L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Lbl,,0,0,0,,{{\\pos({cxs},{py + round(20 * k)})\\1a&H30&}}SANDWICH")
    L.append(f"Dialogue: 4,{ts(t_on)},{ts(total)},Lbl,,0,0,0,,{{\\pos({cxn},{py + round(20 * k)})\\1a&H30&}}NOT A SANDWICH")
    s = n = 0
    for cx in (cxs, cxn):
        L.append(f"Dialogue: 5,{ts(t_on)},{ts(events[0][0])},Num,,0,0,0,,{{\\pos({cx},{py + ph - round(6 * k)})}}0")
    for i, (t, side) in enumerate(events):
        s += side == 'S'; n += side == 'N'
        nxt = events[i + 1][0] if i + 1 < len(events) else total
        bump = rf"\1c{YEL}\fscx150\fscy150\t(0,160,\fscx100\fscy100)\t(260,520,\1c&HFFFFFF&)"
        for cx, val, sd in ((cxs, s, 'S'), (cxn, n, 'N')):
            L.append(f"Dialogue: 5,{ts(t)},{ts(nxt)},Num,,0,0,0,,{{\\pos({cx},{py + ph - round(6 * k)})" + (bump if side == sd else '') + f"}}{val}")
    # FINAL: yellow tag under the board, the winning number turns yellow, the losing side dims
    win_x = cxn if n >= s else cxs; lose_x = cxs if n >= s else cxn
    L.append(f"Dialogue: 6,{ts(final_t)},{ts(total)},Final,,0,0,0,,{{\\pos({W // 2},{py + ph + round(22 * k)})\\fscx60\\fscy60\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}}FINAL")
    L.append(f"Dialogue: 6,{ts(final_t)},{ts(total)},Num,,0,0,0,,{{\\pos({win_x},{py + ph - round(6 * k)})\\1c{YEL}\\t(0,140,\\fscx125\\fscy125)\\t(140,260,\\fscx100\\fscy100)}}{max(n, s)}")
    L.append(f"Dialogue: 6,{ts(final_t)},{ts(total)},Box,,0,0,0,,{{\\pos({px if lose_x == cxs else W // 2 + 2},{py})\\1c{NAVY}\\1a&H50&\\shad0\\p1}}{rrect(pw // 2 - 2, ph, round(26 * k))}")
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
    json.dump(timeline, open(os.path.join(OUT, 'timeline_v13.json'), 'w'), indent=1)
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
    ass = os.path.join(OUT, f'captions_v13_{SHAPE}.ass')
    open(ass, 'w').write(build_ass(timeline, total))
    fl.append(f"[vc]subtitles={ass}[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_v13_{SHAPE}.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
    print(out, f"{total:.2f}s")


main()
