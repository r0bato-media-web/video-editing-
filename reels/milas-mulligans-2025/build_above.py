"""Mila's Mulligans 2026 drone reel: a drone-only reel (9:16), Rob's pick on 16 Nov 2026.
Eight drone shots from the 2026 tournament, a hook card on the first, then the logo ending over a drone still.
The drone has no sound. v2 (Rob, 16 Nov 2026, after the research run: Instagram says it makes reels published without audio less
visible) lays the crowd sound from the pavilion under the whole reel, from a Sony clip shot the same day; on Instagram a library
instrumental still goes on at posting.
Usage: python build_above.py <work_dir> <version>   (<work_dir> needs fonts/ with the Inter Display files and end_above.mp4, the EndPhoto render)"""
import json, os, subprocess, sys
OUT, V = sys.argv[1], sys.argv[2]
D = "E:/MILA'S MULLIGANS/MILAS MULLS '26/TOURNEY/VIDS/DRONE/"
W, H = 1080, 1920
YEL = '&H3FD2FF&'
N = 70            # frames per shot (2.33 s)
TAIL = 6          # extra frames of the last shot under the dissolve into the ending
BED, BED_IN, BED_GAIN = "bed.wav", 0, 0.0   # built by make_bed()
# (clip number, source in s, crop centre as a fraction of the width, what it shows)
SHOTS = [(360, 9.0, 0.45, 'pulling back from the pavilion and the carts'),
         (365, 9.9, 0.55, 'the carts lined up along the trees'),
         (366, 84.0, 0.84, 'carts rolling out past the fence'),
         (363, 51.0, 0.37, 'a golfer on a tee box'),
         (367, 5.0, 0.42, 'a group walking up a fairway'),
         (370, 167.0, 0.45, 'a cart on the path and a golfer by a hole marker'),
         (371, 4.0, 0.40, 'the course from high up: fairways and ponds'),
         (370, 76.0, 0.50, 'a tall pine, a green and a bunker'),
         (367, 22.0, 0.55, 'a golfer swinging on a tee'),
         (370, 46.0, 0.50, 'a cart path winding through trees'),
         (371, 15.2, 0.50, 'trees and the path with the pavilion in the distance'),
         (360, 17.0, 0.50, 'high over the pavilion and the carts, still pulling back')]   # not DJI_0371 at 28 s: two young women and a man are on the green there, ages unknown
# v4 (Rob, 16 Nov 2026): DJI_0374 is out. Rob stands in the middle of it holding the drone controller ("15 seconds in literally holding it in
# the middle"). DJI_0370 at 198 s is not used either: a man in a cap is right under the drone. Twelve shots take it past 30 s ("at least 30 seconds").
# Sound: "fade out of the cart sounds and just go to the sounds of the course".
SONY154 = "E:/MILA'S MULLIGANS/MILAS MULLS '26/TOURNEY/VIDS/SONY/C0154.MP4"                     # carts rolling out; used from 12 s (words only at 2.4 to 6.9 s)
OSMO39 = "E:/MILA'S MULLIGANS/MILAS MULLS '26/TOURNEY/VIDS/OSMO/DJI_20260822125907_0039_D.MP4"  # a golfer on a tee, 5.6 to 13.3 s


FREESOUND = "E:/MILA'S MULLIGANS/488938__klankbeeld__golf-course-nl-oct-191019_0079.ogg"
# "Golf course NL Oct 191019_0079" by klankbeeld, https://freesound.org/people/klankbeeld/sounds/488938/ , CC BY 4.0.
# The licence requires a credit to klankbeeld and freesound.org wherever the reel is posted. Rob downloaded it on 16 Nov 2026.


def make_bed(total):
    """v7: the carts driving away under the first three shots, then a 1.5 s crossfade into the real golf course recording.
    Rob asked for exactly this ("fade out of the cart sounds and just go to the sounds of the course"); v6 dropped the carts and he
    said so ("the golf carts driving away was good to start it i told you"). Carts: Sony C0154 20 to 28 s at +13.6 dB, as in v5.
    Course: the Freesound recording from 10:28 (628 s) at +6.4 dB, the stretch Rob picked by ear, running on unbroken to the end."""
    f = "aresample=48000,aformat=channel_layouts=stereo"
    fc = (f"[0:a]{f},volume=13.6dB[c];[1:a]{f},volume=6.4dB[g];[c][g]acrossfade=d=1.5,"
          f"afade=t=in:d=0.4,afade=t=out:st={total - 1.0:.3f}:d=1.0,alimiter=limit=0.5:level=false,atrim=end={total:.4f}[o]")
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', '20', '-t', '8', '-i', SONY154,
                    '-ss', '628', '-t', f'{total:.3f}', '-i', FREESOUND, '-filter_complex', fc, '-map', '[o]', '-c:a', 'pcm_s16le', 'bed.wav'], check=True)


def ts(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def crop_for(f, cx):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f],
                       capture_output=True, text=True).stdout.split()[0].strip(',').split(',')
    sw, sh = int(o[0]), int(o[1])
    cw = round(sh * 9 / 16 / 2) * 2
    x = int(min(max(cx * sw - cw / 2, 0), sw - cw))
    return f"crop={cw}:{sh}:{x}:0"


def main():
    inputs, fl, tl = [], [], []
    for i, (n, a, cx, what) in enumerate(SHOTS):
        f = D + f'DJI_0{n}.MP4'
        nf = N + (TAIL if i == len(SHOTS) - 1 else 0)
        inputs += ['-ss', f'{a:.3f}', '-t', f'{nf / 30 + 0.3:.3f}', '-i', f]
        fl.append(f"[{i}:v:0]fps=30,{crop_for(f, cx)},scale={W}:{H}:flags=lanczos,setsar=1,trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
        tl.append({'file': f'DJI_0{n}.MP4', 'in': a, 'frames': nf, 't0': round(i * N / 30, 4), 'cx': cx, 'shows': what})
    body = N * len(SHOTS)
    fl.append(''.join(f'[v{i}]' for i in range(len(SHOTS))) + f'concat=n={len(SHOTS)}:v=1:a=0[vc]')
    head = "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Hook,Inter Display Black,94,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,1,0,1,9,5,8,60,60,330,1",
        "Style: Tag,Inter Display,34,&H00FFFFFF,&H00FFFFFF,&H66000000,&H66000000,-1,0,0,0,100,100,4,0,3,14,0,8,80,80,290,1", "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", ""])
    d1 = N / 30
    # no "FROM ABOVE": Rob, 16 Nov 2026, "dont need to say FROM ABOVE", "THEY CAN SEE ITS FROM ABOVE",
    L = [f"Dialogue: 2,{ts(0.1)},{ts(d1)},Hook,,0,0,0,," + "{\\fad(120,150)}" + "MILA'S MULLIGANS\\N{\\c" + YEL + "}2026",
         f"Dialogue: 1,{ts(0.25)},{ts(d1)},Tag,,0,0,0,," + "{\\fad(150,150)}" + "AUG 22, 2026 · WHITETAIL GOLF CLUB"]
    open(f'captions_{V}.ass', 'w', encoding='utf8').write(head + "\n".join(L) + "\n")
    fl.append(f"[vc]subtitles=captions_{V}.ass:fontsdir=fonts[vb]")
    total = body + 90
    make_bed(total / 30)
    k = len(SHOTS)
    inputs += ['-i', 'end_above.mp4']
    fl.append(f"[vb]settb=1/30[b];[{k}:v]fps=30,scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setsar=1,settb=1/30[e];"
              f"[b][e]xfade=transition=fade:duration={TAIL / 30:.4f}:offset={body / 30:.4f}[vo]")
    meta = {'title': "Mila's Mulligans 2026", 'artist': 'Rob Lopez / Robato Media',
            'comment': f'INTERNAL TEST {V} - not for posting. robatomedia.com | r0bato@robatomedia.com | (570) 664-0550',
            'description': "Mila's Mulligans 2026 at Whitetail Golf Club, Bath PA, from the drone. Proceeds from the tournament help fund the Arian Walker Hannon-Kohler Memorial Scholarship and other charitable initiatives.",
            'keywords': "Mila's Mulligans, charity golf tournament, golf fundraiser, Whitetail Golf Club, Bath PA, Lehigh Valley, drone, MilasMulligans, CharityGolf, GolfFundraiser, LehighValley, BathPA"}
    md = sum((['-metadata', f'{a}={b}'] for a, b in meta.items()), []) + ['-metadata', 'copyright=']
    out = f'MilasMulligans_FromAbove2026_{V}_review.mp4'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + inputs + ['-ss', f'{BED_IN}', '-t', f'{total / 30 + 0.2:.4f}', '-i', BED,
                    '-filter_complex', ';'.join(fl) + f";[{k + 1}:a:0]aresample=48000,aformat=channel_layouts=stereo,volume={BED_GAIN}dB,"
                    f"afade=t=in:d=0.4,afade=t=out:st={total / 30 - 1.0:.3f}:d=1.0,alimiter=limit=0.5:level=false,atrim=end={total / 30:.4f}[ao]",
                    '-map', '[vo]', '-map', '[ao]',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-profile:v', 'high', '-level', '4.1', '-pix_fmt', 'yuv420p',
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-t', f'{total / 30:.4f}'] + md + [out], check=True)
    json.dump({'body_frames': body, 'tail_frames': TAIL, 'total_frames': total, 'shots': tl}, open(f'timeline_{V}.json', 'w'), indent=1)
    print(out, f'{total} frames, {total / 30:.2f} s')


os.chdir(OUT)
main()
