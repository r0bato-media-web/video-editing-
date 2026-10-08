"""Reel 1 v8: 'Is a hot dog a sandwich?' Cuts, static crops, hook, tally and captions for the body.

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
    ('int_ant',         16.96, 17.92, 780, 1.0, None, False),        # No. No. (navy shirt, mouth moving, mic on him)
    ('int_ant',         17.92, 18.40, 1060, 1.0, None, False),       # Yes. (floral shirt)
    ('int_darryl',      35.29, 37.59, 860, 1.0, None, False),        # A hot dog in my book is
    ('int_darryl',      37.59, 39.22, 820, 1.15, None, False),       # NOT a sandwich. It's a hot dog. (punch-in)
    ('int_hotdog',      43.60, 45.16, 820, 1.0, None, False),        # No, not a sandwich (trucker cap says all of it; friend in frame)
    ('int_hotdog',      56.64, 57.72, 660, 1.0, None, False),        # No, it's
    ('int_hotdog',      57.72, 58.68, 660, 1.15, None, False),       # DEFINITELY not a sandwich (punch-in)
    ('int_hotdog',      58.68, 59.48, 980, 1.15, None, False),       # No, (driver) then her shot plays on under FINAL, sound muted
]
MUTE = {('int_hotdog', 58.68): 58.93}  # mute from here (the interviewer's "all right" follows the driver's "No")
HOLD = 0.0


def mute_for(seg):
    for (c, i), m in MUTE.items():
        if c == seg['clip'] and abs(i - seg['in']) < 0.05:
            return m
    return None
# One vote per person, keyed to the word that casts it: (clip, word start, side)
VOTES = [
    ('int_ant', 17.08, 'N'), ('int_ant', 18.10, 'S'),
    ('int_darryl', 37.61, 'N'),
    ('int_hotdog', 44.12, 'N'),
    ('int_hotdog', 57.98, 'N'),
    ('int_hotdog', 58.68, 'N'),
]
# Vertical crop centre (fraction of frame height) where the speaker sits low; default 0.42
YFRAC = {}
# One vote per person, keyed to the word that casts it: (clip, word start, side)
VOTES = [
    ('int_ant', 17.08, 'N'), ('int_ant', 18.10, 'S'),
    ('int_evan_darien', 12.50, 'S'),
    ('int_evan_darien', 16.06, 'N'),
    ('int_darryl', 37.61, 'N'),
    ('int_hotdog', 44.12, 'N'),
    ('int_hotdog', 57.98, 'N'),
    ('int_hotdog', 58.68, 'N'),
]


def words_for(clip, a, b):
    return [w for s in json.load(open(os.path.join(TR, clip + '.json'))) for w in s['words']
            if w['s'] >= a - 0.02 and w['e'] <= b + 0.02]


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def src_to_out(timeline, clip, t):
    for seg in timeline:
        if seg['clip'] == clip and seg['in'] <= t < seg['out']:
            return seg['t0'] + t - seg['in']
    return None


def build_ass(timeline, total):
    v = SHAPE == '916'
    fs = 78 if v else 64
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,{fs},&H00FFFFFF,&H00FFFFFF,&H00753304,&H00753304,-1,0,0,0,100,100,0,0,3,14,0,2,80,80,{560 if v else 90},1
Style: Hook,Inter Black,{118 if v else 104},&H00FFFFFF,&H00FFFFFF,&H00753304,&H00753304,-1,0,0,0,100,100,0,0,3,22,0,8,70,70,{330 if v else 120},1
Style: Tag,Inter ExtraBold,{40 if v else 34},&H00753304,&H00753304,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,2,0,3,10,0,8,80,80,{240 if v else 60},1
Style: Tally,Inter ExtraBold,{52 if v else 44},&H00FFFFFF,&H00FFFFFF,&H00753304,&H00753304,-1,0,0,0,100,100,1,0,3,14,0,8,60,60,{250 if v else 50},1
Style: Final,Inter Black,{70 if v else 60},&H00FFFFFF,&H00FFFFFF,&H00753304,&H00753304,-1,0,0,0,100,100,1,0,3,18,0,8,60,60,{250 if v else 50},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hook_end = sum(s['out'] - s['in'] for s in timeline if s['hook'])
    L = [f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,120)}}IS A HOT DOG\\NA SANDWICH?",
         f"Dialogue: 1,{ts(0)},{ts(hook_end)},Tag,,0,0,{(330 + 300) if SHAPE == '916' else 380},,THROWBACK · MILA'S MULLIGANS 2025"]
    # tally: changes on each vote word; shown from first vote to end of footage
    last = timeline[-1]; mute = mute_for(last)
    final_t = last['t0'] + (mute - last['in']) if mute else total - HOLD
    events = sorted((src_to_out(timeline, c, t), side) for c, t, side in VOTES if src_to_out(timeline, c, t) is not None)
    s = n = 0
    for i, (t, side) in enumerate(events):
        s += side == 'S'; n += side == 'N'
        nxt = events[i + 1][0] if i + 1 < len(events) else final_t
        pop = r"{\t(0,90,\fscx118\fscy118)\t(90,200,\fscx100\fscy100)}"
        txt_s = (pop if side == 'S' else '') + f"SANDWICH {s}"
        txt_n = (pop if side == 'N' else '') + f"NOT A SANDWICH {n}"
        L.append(f"Dialogue: 1,{ts(t)},{ts(nxt)},Tally,,0,0,0,,{txt_s}{{\\r}}  |  {txt_n}")
    L.append(f"Dialogue: 1,{ts(final_t)},{ts(total)},Final,,0,0,0,,{{\\fad(80,0)}}FINAL: NOT A SANDWICH {n}-{s}")
    # word-timed captions (3-word chunks), active word light blue
    for seg in timeline:
        m = mute_for(seg)
        ws = [w for w in seg['words'] if not m or w['s'] < m]; chunks, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or w['w'].strip().endswith(('.', '?', '!', ',')):
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        for ci, ch in enumerate(chunks):
            c_end = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else (m or seg['out'])
            for wi, w in enumerate(ch):
                st = seg['t0'] + max(w['s'], seg['in']) - seg['in']
                en = seg['t0'] + min(ch[wi + 1]['s'] if wi + 1 < len(ch) else c_end, seg['out']) - seg['in']
                en = min(en, seg['t0'] + seg['out'] - seg['in'] - 1 / 30)  # never spill into the next shot
                if seg['hook']:
                    continue  # the hook carries the question
                parts = [(r"{\c&HFFC39D&}" + x['w'].strip().upper() + r"{\c&HFFFFFF&}") if k == wi else x['w'].strip().upper()
                         for k, x in enumerate(ch)]
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{' '.join(parts)}")
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
    json.dump(timeline, open(os.path.join(OUT, 'timeline_v8.json'), 'w'), indent=1)
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
    ass = os.path.join(OUT, f'captions_v8_{SHAPE}.ass')
    open(ass, 'w').write(build_ass(timeline, total))
    fl.append(f"[vc]subtitles={ass}[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_v8_{SHAPE}.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
    print(out, f"{total:.2f}s")


main()
