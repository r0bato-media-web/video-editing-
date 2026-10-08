"""Join body + end card, two-pass loudnorm to -14 LUFS, write R0BATO metadata, make a chat preview.
Usage: python finish_reel1.py <reel1_dir> <version>"""
import json, os, subprocess, sys
D, V = sys.argv[1], sys.argv[2]
META = {'title': 'Is a hot dog a sandwich?', 'artist': 'Rob Lopez / Robato Media',
        'comment': f'INTERNAL TEST {V} - not for posting. robatomedia.com | r0bato@robatomedia.com | (570) 664-0550',
        'description': "Throwback to Mila's Mulligans 2025: golfers vote on whether a hot dog is a sandwich. Every dollar goes to the Arian Walker Hannon-Kohler Memorial Scholarship.",
        'keywords': "Mila's Mulligans, charity golf tournament, golf fundraiser, Whitetail Golf Club, Bath PA, Lehigh Valley, throwback, MilasMulligans, CharityGolf"}
for sh, tag, pw, ph in (('916', '9x16', 540, 960), ('169', '16x9', 960, 540)):
    body, end = os.path.join(D, f'body_{V}_{sh}.mp4'), os.path.join(D, f'end_{tag}.mp4')
    name = f'MilasMulligans_Throwback2025_HotDogSandwich_{tag}_INTERNALTEST_RobatoMedia'
    joined = os.path.join(D, f'joined_{V}_{sh}.mp4')
    fc = ("[0:v]setsar=1[b];[1:v]fps=30,setsar=1,format=yuv420p[e];anullsrc=r=48000:cl=stereo,atrim=end=4.5[s];"
          "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[ba];[b][ba][e][s]concat=n=2:v=1:a=1[v][a]")
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', body, '-i', end, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'pcm_s16le', joined.replace('.mp4', '.mov')], check=True)
    joined = joined.replace('.mp4', '.mov')
    r = subprocess.run(['ffmpeg', '-nostdin', '-i', joined, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    md = sum((['-metadata', f'{k}={v}'] for k, v in META.items()), []) + ['-metadata', 'copyright=']
    final = os.path.join(D, 'finals', name + '.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', joined, '-af', ln + ',aresample=48000', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart'] + md + [final], check=True)
    prev = os.path.join(D, 'previews', f'{name}_{V}_preview.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', final, '-vf', f'scale={pw}:{ph}:flags=lanczos', '-c:v', 'libx264',
                    '-crf', '23', '-preset', 'medium', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart'] + md + [prev], check=True)
    os.remove(joined)
    print(final); print(prev)
