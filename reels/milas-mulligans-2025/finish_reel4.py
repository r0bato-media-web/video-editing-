"""Reel 4: dissolve the body into the 3 s photo ending, two-pass loudnorm to -14 LUFS, write R0BATO metadata.
Usage: python finish_reel4.py <work_dir> <version>   (expects body_<v>_916.mov, timeline_<v>.json and end_D.mp4 in <work_dir>)
The file it writes is H.264 High 4:2:0, the delivery format (Rob, 16 Oct 2026)."""
import json, os, subprocess, sys
D, V = sys.argv[1], sys.argv[2]
os.chdir(D)
tl = json.load(open(f'timeline_{V}.json')); nf, tail = tl['body_frames'], tl['tail_frames']
META = {'title': "Couldn't ask for a better day", 'artist': 'Rob Lopez / Robato Media',
        'comment': f'INTERNAL TEST {V} - not for posting. robatomedia.com | r0bato@robatomedia.com | (570) 664-0550',
        'description': "Throwback to Mila's Mulligans 2025: one golfer on the weather at Whitetail Golf Club. Proceeds from the tournament help fund the Arian Walker Hannon-Kohler Memorial Scholarship and other charitable initiatives.",
        'keywords': "Mila's Mulligans, charity golf tournament, golf fundraiser, Whitetail Golf Club, Bath PA, Lehigh Valley, throwback, MilasMulligans, CharityGolf, GolfFundraiser, LehighValley, BathPA"}
total = nf + 90
fc = (f"[0:v]fps=30,format=yuv420p,settb=1/30[b];"
      f"[1:v]fps=30,scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setsar=1,settb=1/30[e];"
      f"[b][e]xfade=transition=fade:duration={tail / 30:.4f}:offset={nf / 30:.4f}[v];"
      f"[0:a]apad,atrim=end={total / 30:.4f}[a]")
joined = f'joined_{V}.mov'
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', f'body_{V}_916.mov', '-i', 'end_D.mp4', '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-profile:v', 'high', '-level', '4.1', '-pix_fmt', 'yuv420p',
                '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', '-c:a', 'pcm_s16le', joined], check=True)
r = subprocess.run(['ffmpeg', '-nostdin', '-i', joined, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
md = sum((['-metadata', f'{k}={v}'] for k, v in META.items()), []) + ['-metadata', 'copyright=']
final = f'MilasMulligans_BetterDay_{V}_review.mp4'
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', joined, '-af', ln + ',aresample=192000,alimiter=limit=0.63:attack=1:release=50:level=false,aresample=48000',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart'] + md + [final], check=True)
os.remove(joined)
print(final, f'{total} frames, {total / 30:.2f} s; measured in {m["input_i"]} LUFS, TP {m["input_tp"]}')
