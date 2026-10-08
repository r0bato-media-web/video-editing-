"""Dense QA sheet: a frame every STEP seconds over the whole file, plus the first and last frame of every cut.
Usage: python qa_dense.py <timeline.json> <video> <out.png> <w> <h> [step=0.25]"""
import json, subprocess, sys
tl, vid, out, w, h = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
step = float(sys.argv[6]) if len(sys.argv) > 6 else 0.25
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=duration', '-of', 'csv=p=0', vid]))
times = {round(k * step, 3) for k in range(int(dur / step) + 1) if k * step < dur - 0.02}
for s in json.load(open(tl)):
    d = s['out'] - s['in']; times |= {round(s['t0'] + 0.017, 3), round(s['t0'] + d - 0.05, 3)}
times = sorted(times); ins = []
for i, x in enumerate(times):
    p = f'{out}.{i:03d}.png'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{x:.3f}', '-i', vid, '-frames:v', '1', '-vf',
                    f"scale={w}:{h},drawtext=text='{x:.2f}':fontcolor=yellow:fontsize=18:x=3:y=3:box=1:boxcolor=black", p], check=True)
    ins += ['-i', p]
n = len(times); cols = 12 if w < h else 8
lay = '|'.join(f'{(k % cols) * w}_{(k // cols) * h}' for k in range(n))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + ins + ['-filter_complex', f'xstack=inputs={n}:layout={lay}:fill=black', out], check=True)
print(n, 'frames ->', out)
