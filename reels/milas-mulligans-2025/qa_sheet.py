"""QA contact sheets for a rendered reel body: first, middle and last frame of every cut, plus the freeze.
Usage: python qa_sheet.py <timeline.json> <video> <out.png> <w> <h>"""
import json, subprocess, sys
tl, vid, out, w, h = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
t = json.load(open(tl)); times = []
for s in t:
    d = s['out'] - s['in']; times += [s['t0'] + 0.017, s['t0'] + d / 2, s['t0'] + d - 0.05]
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=duration', '-of', 'csv=p=0', vid]))
times.append(dur - 0.1)
ins = []
for i, x in enumerate(times):
    p = f'{out}.{i:02d}.png'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{x:.3f}', '-i', vid, '-frames:v', '1', '-vf',
                    f"scale={w}:{h},drawtext=text='{x:.2f}':fontcolor=yellow:fontsize=20:x=4:y=4:box=1:boxcolor=black", p], check=True)
    ins += ['-i', p]
n = len(times); cols = 9 if w < h else 6
lay = '|'.join(f'{(k % cols) * w}_{(k // cols) * h}' for k in range(n))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + ins + ['-filter_complex', f'xstack=inputs={n}:layout={lay}:fill=black', out], check=True)
print(n, 'frames ->', out)
