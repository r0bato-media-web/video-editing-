"""Reel 1 v4: 'Is a hot dog a sandwich?' punched up. v4 starts cut 4 on 'disagree' (Rob OK, 7 Oct 2026).

Rob's notes (7 Oct 2026): punch it up; the camera track is too aggressive.
- No moving crops. Every piece has a static frame; the camera's own whip between cuts 3-4
  stays as a short, horizontally blurred whip transition.
- Hook title, live vote tally, hard 115% punch-ins on the emphasis word.

Usage: python build_reel1.py <m25_dir> <916|169>
"""
import json, os, subprocess, sys

M, SHAPE = sys.argv[1], sys.argv[2]
RAW, TR, OUT = (os.path.join(M, d) for d in ('raw', 'transcripts', 'reel1'))
W, H = (1080, 1920) if SHAPE == '916' else (1920, 1080)

# clip, in, out, 9:16 centre x, zoom, whip-blur window (source secs) or None
CUTS = [
    ('int_evan_darien', 8.72, 10.74, 1260, 1.0, None),            # Ava: is a hot dog a sandwich or not?
    ('int_ant',         16.06, 18.40, 900, 1.0, None),            # Yes. No. No. Yes.
    ('int_evan_darien', 11.34, 12.94, 1060, 1.0, (12.36, 12.94)), # I would consider it a sandwich. (whip out)
    ('int_evan_darien', 16.02, 18.02, 920, 1.0, (16.02, 16.14)),  # disagree with that. I don't think so. (whip lands; 920 holds her through the drift 1060->750)
    ('int_darryl',      35.30, 37.59, 900, 1.0, None),            # A hot dog in my book is
    ('int_darryl',      37.59, 39.22, 900, 1.15, None),           # NOT a sandwich. It's a hot dog.  (punch-in)
    ('int_hotdog',      43.60, 45.16, 900, 1.0, None),            # No, not a sandwich (golfer; 'hot dog is a hot dog' was the interviewer)
    ('int_hotdog',      56.64, 57.72, 680, 1.0, None),            # No, it's
    ('int_hotdog',      57.72, 58.74, 680, 1.15, None),           # DEFINITELY not a sandwich (punch-in)
    ('int_hotdog',      59.82, 62.12, 700, 1.0, None),            # Well, we got four for four. It's not a sandwich
]
# Votes, keyed to the word that casts them: (clip, word start, side)
VOTES = [
    ('int_ant', 16.18, 'S'), ('int_ant', 17.08, 'N'), ('int_ant', 17.60, 'N'), ('int_ant', 18.10, 'S'),
    ('int_evan_darien', 12.50, 'S'),
    ('int_evan_darien', 16.06, 'N'),
    ('int_darryl', 37.61, 'N'),
    ('int_hotdog', 44.12, 'N'),
    ('int_hotdog', 57.98, 'N'),
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
    hook_end = timeline[0]['out'] - timeline[0]['in']
    L = [f"Dialogue: 2,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,120)}}IS A HOT DOG\\NA SANDWICH?",
         f"Dialogue: 1,{ts(0)},{ts(hook_end)},Tag,,0,0,{(330 + 300) if SHAPE == '916' else 380},,THROWBACK · MILA'S MULLIGANS 2025"]
    # tally: changes on each vote word; shown from first vote to end of footage
    events = sorted((src_to_out(timeline, c, t), side) for c, t, side in VOTES if src_to_out(timeline, c, t) is not None)
    s = n = 0
    for i, (t, side) in enumerate(events):
        s += side == 'S'; n += side == 'N'
        nxt = events[i + 1][0] if i + 1 < len(events) else timeline[-1]['t0']
        pop = r"{\t(0,90,\fscx118\fscy118)\t(90,200,\fscx100\fscy100)}"
        txt_s = (pop if side == 'S' else '') + f"SANDWICH {s}"
        txt_n = (pop if side == 'N' else '') + f"NOT A SANDWICH {n}"
        L.append(f"Dialogue: 1,{ts(t)},{ts(nxt)},Tally,,0,0,0,,{txt_s}{{\\r}}  |  {txt_n}")
    L.append(f"Dialogue: 1,{ts(timeline[-1]['t0'])},{ts(total)},Final,,0,0,0,,{{\\fad(80,0)}}FINAL: NOT A SANDWICH {n}-{s}")
    # word-timed captions (3-word chunks), active word light blue
    for seg in timeline:
        ws = seg['words']; chunks, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or w['w'].strip().endswith(('.', '?', '!', ',')):
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        for ci, ch in enumerate(chunks):
            c_end = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else seg['out']
            for wi, w in enumerate(ch):
                st = seg['t0'] + max(w['s'], seg['in']) - seg['in']
                en = seg['t0'] + min(ch[wi + 1]['s'] if wi + 1 < len(ch) else c_end, seg['out']) - seg['in']
                if seg is timeline[0]:
                    continue  # the hook carries the question
                parts = [(r"{\c&HFFC39D&}" + x['w'].strip().upper() + r"{\c&HFFFFFF&}") if k == wi else x['w'].strip().upper()
                         for k, x in enumerate(ch)]
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{' '.join(parts)}")
    return head + "\n".join(L) + "\n"


def main():
    timeline, t = [], 0.0
    for clip, a, b, cx, z, blur in CUTS:
        timeline.append({'clip': clip, 'in': a, 'out': b, 'cx': cx, 'zoom': z, 'blur': blur, 't0': t,
                         'words': words_for(clip, a, b)})
        t += b - a
    total = t
    json.dump(timeline, open(os.path.join(OUT, 'timeline_v4.json'), 'w'), indent=1)
    inputs, fl = [], []
    for i, seg in enumerate(timeline):
        inputs += ['-ss', f"{seg['in']:.3f}", '-to', f"{seg['out']:.3f}", '-i', os.path.join(RAW, seg['clip'] + '.mp4')]
        z = seg['zoom']
        if SHAPE == '916':
            cw, ch = round(608 / z), round(1080 / z)
            x = min(max(seg['cx'] - cw // 2, 0), 1920 - cw)
            y = min(max(round(1080 * 0.42) - ch // 2, 0), 1080 - ch)
        else:
            cw, ch = round(1920 / z), round(1080 / z)
            x = min(max(round(seg['cx'] * 0.5 + 960 * 0.5) - cw // 2, 0), 1920 - cw)
            y = min(max(round(1080 * 0.42) - ch // 2, 0), 1080 - ch)
        chain = f"[{i}:v:0]crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,fps=30,setsar=1"
        if seg['blur']:
            b0, b1 = seg['blur'][0] - seg['in'], seg['blur'][1] - seg['in']
            chain += f",avgblur=sizeX=60:sizeY=1:enable='between(t,{b0:.3f},{b1:.3f})'"
        fl.append(chain + f",format=yuv420p[v{i}]")
        d = seg['out'] - seg['in']
        fl.append(f"[{i}:a:0]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.015,afade=t=out:st={d - 0.025:.3f}:d=0.025[a{i}]")
    n = len(timeline)
    fl.append(''.join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    ass = os.path.join(OUT, f'captions_v4_{SHAPE}.ass')
    open(ass, 'w').write(build_ass(timeline, total))
    fl.append(f"[vc]subtitles={ass}[vo]")
    fl.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    out = os.path.join(OUT, f'body_v4_{SHAPE}.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl),
                    '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
    print(out, f"{total:.2f}s")


main()
