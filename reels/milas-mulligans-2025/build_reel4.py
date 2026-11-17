"""Reel 4: "Couldn't ask for a better day" (Mila's Mulligans 2025 throwback, 9:16).
v2 (Rob, 16 Nov 2026: v1 was "only 10 seconds", "more sizzle reel after it", and yes to more voices): four golfers on the day, then a
sizzle of swings, putts and carts with the course's own sound, then the photo ending (finish_reel4.py).
v3 (Rob, 16 Nov 2026: "we can use different b roll than the stuff i already used in another video", "no drone shots over them talking?"):
drone shots sit over the talking, and the sizzle drops the swing clips his Countdown and Grab Your Foursome reels already used
(00057, 00069, 00021, 00101 and their lookalikes). The only drone footage is from the 2026 tournament, an overcast day, so only shots
that look down at the course are used and the tag no longer names a year.
Usage: python build_reel4.py <work_dir> <version>     (<work_dir> needs fonts/ with InterDisplay-Black.ttf and InterDisplay-Bold.ttf)"""
import json, os, subprocess, sys
import numpy as np
OUT, V = sys.argv[1], sys.argv[2]
VID = "E:/MILA'S MULLIGANS/MILAS MULLS '25/VIDS/"
T = VID + "2025 MM TOUR. TONY/"
W, H = 1080, 1920
YEL = '&H3FD2FF&'
STAB_ZOOM = 1.04      # punch-in on the two smoothed cuts, to hide the edges the smoothing moves
JBF, INT2 = T + 'Mila 2025 5/Jasmin bf interview.MP4', T + 'Mila 2025 5/Interview 2.MP4'
ANGEL, MITO = T + 'Mila 2025 4/Angel interview.MP4', T + 'Mila 2025 4/Mito Interview.MP4'
CART = T + 'Mila 2025/Cart Driving.MP4'
DRONE = "E:/MILA'S MULLIGANS/MILAS MULLS '26/TOURNEY/VIDS/DRONE/"     # 2026 tournament, DJI, 4K or 2.7K, no sound
D359, D361, D362, D363, D368, D370 = (DRONE + f'DJI_0{n}.MP4' for n in (359, 361, 362, 363, 368, 370))
# Voice segments. a / b = the voice's in and out (source s).
# cuts = picture: (file, source in or None for "where the voice is", frames or None for "the rest", crop centre x, stabilize).
# Crop centre x is in source pixels for the 1920-wide camera files and a fraction of the width (0 to 1) for the drone files.
# phrases = caption phrases as (WORD, onset s); ends = phrase index -> the time it leaves, when that is before the next phrase.
SEGS = [
    {'name': 'jbf', 'voice': JBF, 'a': 5.12, 'b': 12.70,   # in: the level dip before "I couldn't"; out: the quiet after "weather" (interviewer's next word 13.14)
     'cuts': [(JBF, None, 47, 760, False), (D359, 6.0, 46, 0.62, False), (D363, 8.5, 42, 0.52, False), (D370, 104.0, 41, 0.62, False), (JBF, None, None, 760, False)],
     'phrases': [[("I", 5.40), ("COULDN'T", 5.48), ("ASK", 5.68)], [("FOR", 5.82), ("A", 5.98), ("BETTER", 6.10), ("DAY", 6.22)], [("YOU", 6.74), ("KNOW", 6.95)],
                 [("I", 7.62), ("THINK", 7.70), ("IT'S", 7.80)], [("SUPPOSED", 7.92), ("TO", 8.02), ("BE", 8.08)], [("RAINY", 8.16), ("TOMORROW", 8.34)],
                 [("SO", 8.78), ("IT'S", 9.08), ("BEEN", 9.38)], [("PLEASANT", 9.66)], [("YOU", 11.06), ("KNOW", 11.14)],
                 [("CAN'T", 11.72), ("ASK", 11.88), ("FOR", 11.96)], [("BETTER", 12.08), ("WEATHER", 12.24)]],
     'ends': {1: 6.62, 2: 7.22, 5: 8.72, 7: 10.72, 8: 11.32, 10: 12.58}},
    # one word, after the interviewer's "...Whitetail Golf Course?" (ends 6.6). The camera drifts 114 px/s here; the cut gets light smoothing.
    {'name': 'int2', 'voice': INT2, 'a': 6.78, 'b': 7.56,
     'cuts': [(INT2, None, None, 650, True)], 'phrases': [[("FANTASTIC", 6.86)]], 'ends': {0: 7.52}},
    # in: the dip after the interviewer's "Course?"; out: the quiet after "loose" (next sound 57.14). One camera bump (184 px/s); light smoothing.
    {'name': 'angel', 'voice': ANGEL, 'a': 53.56, 'b': 57.06,
     'cuts': [(D370, 226.0, 28, 0.55, False), (ANGEL, None, None, 1340, True)],   # his cap hides his eyes on the first sentence, so a drone shot covers it
     'phrases': [[("IT'S", 53.62), ("A", 53.96)], [("BEAUTIFUL", 54.04), ("DAY", 54.24)], [("I'M", 55.02), ("FEELING", 55.14)], [("ACTUALLY", 55.30)],
                 [("VERY", 55.64), ("GOOD", 56.02)], [("VERY", 56.38), ("LOOSE", 56.48)]],
     'ends': {1: 54.46, 4: 56.30, 5: 57.00}},
    # the interviewer's question (she stands at the frame's left; her arm and mic reach in) and the golfer's answer
    {'name': 'mito', 'voice': MITO, 'a': 30.60, 'b': 37.02,
     'cuts': [(D362, 60.0, 81, 0.45, False), (MITO, None, None, 1000, False)],    # the carts and the field from above under the interviewer's question, then the golfers for the answer
     'phrases': [[("DO", 30.62), ("YOU", 30.70), ("THINK", 30.80)], [("WE'RE", 31.04), ("GOING", 31.56)], [("TO", 31.68), ("BE", 31.74), ("THE", 31.98)], [("WINNERS", 32.32)],
                 [("HERE", 32.54), ("TODAY", 32.80)], [("NO", 33.78)], [("BUT", 34.10), ("WE'LL", 34.16), ("KEEP", 34.34)], [("THE", 34.46), ("VIBES", 34.62), ("UP", 34.92)],
                 [("THE", 35.00), ("WHOLE", 35.14)], [("ENTIRE", 35.30), ("TIME", 35.58)], [("THAT'S", 35.98), ("ALL", 36.14)],
                 [("WE'RE", 36.22), ("HERE", 36.38), ("FOR", 36.48)], [("REALLY", 36.80)]],
     'ends': {4: 33.20, 5: 34.02, 9: 35.92, 12: 37.00}},
]
# Sizzle: (file, the moment the club meets the ball, crop centre x). Each shot runs from 0.45 s before that moment to 0.35 s after.
# The moment is the sharpest peak in the clip's own sound. The cart shot has no hit; its "moment" just places the 0.8 s.
SIZ_N = 24
SIZZLE = [(CART, 88.45, 900), (VID + '00077.MTS', 8.55, 520), (D361, 23.45, 0.48), (VID + '00032.MTS', 6.34, 830), (VID + '00089.MTS', 7.04, 640),
          (D368, 5.45, 0.45), (VID + '00074.MTS', 7.92, 730), (VID + '00092.MTS', 10.92, 630), (VID + '00019.MTS', 8.92, 940)]
TAIL = 6                            # extra frames of the last shot, under the dissolve into the ending
VOICE_DB, SIZ_DB = -20.0, -23.0     # each voice's louder half is brought to VOICE_DB and each sizzle shot's loudest 50 ms to SIZ_DB; the finish step sets the whole mix to -14 LUFS


def ts(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def pcm(f, a, d):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                       capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768


def win_db(x, n=800):
    e = np.array([np.sqrt(np.mean(x[i:i + n] ** 2)) for i in range(0, max(len(x) - n, 1), n)]) + 1e-9
    return 20 * np.log10(e)


_size = {}


def crop_for(f, cx, z):
    """A 9:16 crop of any source: full height (less the stabilizer's punch-in), centred on cx (pixels, or a 0 to 1 fraction of the width)."""
    if f not in _size:
        o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f],
                           capture_output=True, text=True).stdout.split()[0].strip(',').split(',')   # first line only: some .MTS files list the stream twice
        _size[f] = (int(o[0]), int(o[1]))
    sw, sh = _size[f]
    ch = round(sh / z / 2) * 2
    cw = round(ch * 9 / 16 / 2) * 2
    c = cx * sw if cx <= 1 else cx
    x = int(min(max(c - cw / 2, 0), sw - cw))
    return f"crop={cw}:{ch}:{x}:{(sh - ch) // 2}"


def stabilize(f, a, d, key):
    """Light smoothing only (Rob, 16 Nov 2026: he asked "you're adding hard stabilization?" about v3's tripod lock and chose light smoothing).
    The handheld movement stays; vidstab averages the camera path over about a third of a second each side (smoothing=20 at 60 fps), which takes down a bump or a jitter."""
    out, trf = f'stab_{key}.mp4', f'stab_{key}.trf'
    rng = ['-ss', f'{a:.3f}', '-t', f'{d + 0.2:.3f}', '-i', f]
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + rng + ['-vf', f'vidstabdetect=shakiness=5:accuracy=15:result={trf}', '-f', 'null', '-'], check=True)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + rng + ['-vf', f'vidstabtransform=input={trf}:smoothing=20:crop=keep:interpol=bicubic:optzoom=0:zoom=0',
                    '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', out], check=True)
    return out


def main():
    inputs, fl, vlab, alab, tl, L = [], [], [], [], [], []
    k, t0 = 0, 0          # input index, frames so far
    for seg in SEGS:
        nf = round((seg['b'] - seg['a']) * 30)
        used = 0
        for ci, (f, a, n, cx, stab) in enumerate(seg['cuts']):
            if a is None:
                a = seg['a'] + used / 30
            if n is None:
                n = nf - used
            z = STAB_ZOOM if stab else 1.0
            if stab:
                inputs += ['-i', stabilize(f, a, n / 30, f"{seg['name']}_{ci}")]
            else:
                inputs += ['-ss', f'{a:.3f}', '-t', f'{n / 30 + 0.2:.3f}', '-i', f]
            fl.append(f"[{k}:v:0]fps=30,{crop_for(f, cx, z)},scale={W}:{H}:flags=lanczos,setsar=1,trim=end_frame={n},setpts=PTS-STARTPTS,format=yuv420p[v{k}]")
            vlab.append(f'[v{k}]')
            tl.append({'seg': seg['name'], 'file': f.replace(VID, ''), 'in': round(a, 3), 'frames': n, 't0': round((t0 + used) / 30, 4), 'cx': cx, 'stab': stab})
            used += n
            k += 1
        d = nf / 30
        db = win_db(pcm(seg['voice'], seg['a'], d))
        gain = VOICE_DB - float(np.mean(np.sort(db)[len(db) // 2:]))
        inputs += ['-ss', f"{seg['a']:.3f}", '-t', f'{d:.3f}', '-i', seg['voice']]
        fl.append(f"[{k}:a:0]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.1f}dB,afade=t=in:d=0.025,afade=t=out:st={d - 0.06:.3f}:d=0.06,"
                  f"apad,atrim=end={d:.4f},asetpts=PTS-STARTPTS[a{k}]")
        alab.append(f'[a{k}]')
        k += 1
        base = t0 / 30 - seg['a']
        for pi, ph in enumerate(seg['phrases']):
            p_end = seg['ends'].get(pi, seg['phrases'][pi + 1][0][1] if pi + 1 < len(seg['phrases']) else seg['b'])
            for wi, (w, s) in enumerate(ph):
                st = base + s
                en = base + (ph[wi + 1][1] if wi + 1 < len(ph) else p_end)
                parts = [("{\\c" + YEL + "}" + x_ + "{\\c&HFFFFFF&}") if j == wi else x_ for j, (x_, _) in enumerate(ph)]
                pre = "{\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
                L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{pre}{' '.join(parts)}")
        tl.append({'seg': seg['name'], 'voice_gain_dB': round(gain, 1)})
        t0 += nf
    siz_t0 = t0
    for si, (f, imp, cx) in enumerate(SIZZLE):
        last = si == len(SIZZLE) - 1
        n = SIZ_N + (TAIL if last else 0)
        a = imp - 0.45
        inputs += ['-ss', f'{a:.3f}', '-t', f'{n / 30 + 0.3:.3f}', '-i', f]
        di = 'yadif=0,' if f.endswith('.MTS') else ''
        fl.append(f"[{k}:v:0]{di}fps=30,{crop_for(f, cx, 1.0)},scale={W}:{H}:flags=lanczos,setsar=1,trim=end_frame={n},setpts=PTS-STARTPTS,format=yuv420p[v{k}]")
        d = n / 30
        k += 1
        if f.startswith(DRONE):          # the drone has no sound: these shots carry the cart shot's crowd sound from a little later in that clip
            af, aa = CART, 92.0 + si
        else:
            af, aa = f, a
        inputs += ['-ss', f'{aa:.3f}', '-t', f'{d + 0.3:.3f}', '-i', af]
        gain = min(SIZ_DB - float(np.max(win_db(pcm(af, aa, SIZ_N / 30)))), 6.0)   # never lift a quiet shot more than 6 dB (it only brings up noise)
        fo = f"afade=t=out:st={SIZ_N / 30 - 0.08:.3f}:d=0.08" if last else f"afade=t=out:st={d - 0.03:.3f}:d=0.03"
        fl.append(f"[{k}:a:0]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.1f}dB,afade=t=in:d=0.03,{fo},apad,atrim=end={d:.4f},asetpts=PTS-STARTPTS[a{k}]")
        vlab.append(f'[v{k - 1}]')
        alab.append(f'[a{k}]')
        tl.append({'seg': 'sizzle', 'file': f.replace(VID, ''), 'in': round(a, 3), 'frames': n, 't0': round(t0 / 30, 4), 'cx': cx, 'gain_dB': round(gain, 1)})
        t0 += n
        k += 1
    body = t0 - TAIL
    fl.append(''.join(vlab) + f'concat=n={len(vlab)}:v=1:a=0[vc]')
    fl.append(''.join(alab) + f'concat=n={len(alab)}:v=0:a=1[ao]')
    head = "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Cap,Inter Display Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,7,4,2,70,70,610,1",
        "Style: Tag,Inter Display,34,&H00FFFFFF,&H00FFFFFF,&H66000000,&H66000000,-1,0,0,0,100,100,4,0,3,14,0,8,80,80,290,1", "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", ""])
    L.insert(0, f"Dialogue: 1,{ts(0.15)},{ts(47 / 30)},Tag,,0,0,0,," + "{\\fad(150,120)}" + "THROWBACK · MILA'S MULLIGANS")
    open(f'captions_{V}.ass', 'w', encoding='utf8').write(head + "\n".join(L) + "\n")
    json.dump({'body_frames': body, 'tail_frames': TAIL, 'sizzle_start_frame': siz_t0, 'cuts': tl}, open(f'timeline_{V}.json', 'w'), indent=1)
    fl.append(f"[vc]subtitles=captions_{V}.ass:fontsdir=fonts[vo]")
    out = f'body_{V}_916.mov'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fl), '-map', '[vo]', '-map', '[ao]',
                    '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', out], check=True)
    print(out, f'body {body} frames ({body / 30:.2f} s) + {TAIL} tail; sizzle starts at {siz_t0 / 30:.2f} s')


os.chdir(OUT)
main()
