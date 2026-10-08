# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v7, 8 Oct 2026. Not approved for posting.

A 19.0 s reel in 9:16 and 16:9: golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

## Build

```
# 1. footage: list.tsv is "<name>\t<Drive file id>" per line (not committed)
./dl.sh <scratch>                       # -> <scratch>/m25/raw/<name>.mp4
# 2. audio + transcripts (faster-whisper small.en, word timestamps)
for f in raw/*.mp4; do ffmpeg -v error -y -i $f -vn -ac 1 -ar 16000 audio/$(basename $f .mp4).wav; done
python transcribe.py audio transcripts
# 3. body (cuts, static crops, holds, hook, tally, captions)
python build_reel1.py <m25_dir> 916
python build_reel1.py <m25_dir> 169
# 4. end card
cd ../../explainers/milas-mulligans && npx remotion render src/index.tsx End-9x16 out/end_9x16.mp4
```

Then join body and end card (4.5 s of silence under the card), normalise the final to -14 LUFS with two-pass `loudnorm`, write R0BATO metadata with the comment marked internal, and write a `_SOCIAL_COPY.txt` per file.

Before anything is called done, check the whole file:

```
python qa_dense.py <m25>/reel1/timeline_v7.json <final or preview>.mp4 qa_916.png 150 267   # 9:16
python qa_dense.py <m25>/reel1/timeline_v7.json <final or preview>.mp4 qa_169.png 240 135   # 16:9
```

It pulls a frame every 0.25 s over the whole file plus the first and last frame of every cut. Look at every frame: the person talking must be in frame, sharp and centred, with their whole face in. Transition frames are no exception. `qa_sheet.py` is a quicker first, middle and last frame pass.

Camera motion: `camera_speed.py <m25> <clip> <in> <out>` measures camera speed on the background before a cut is chosen (keep 9:16 cuts under about 75 source px/s). `output_motion.py <video> <timeline.json>` measures apparent motion per cut in a rendered file.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre on the person talking, zoom, and an optional hold point where the picture freezes on a sharp frame while the sound finishes. Wherever the speaker changes, the cut is split and the new speaker gets their own static crop. Every cut is snapped to whole frames. `YFRAC` lowers the 16:9 crop where a speaker sits low in frame.
- **Votes:** `VOTES` counts one vote per person in the cut. The final tally reads NOT A SANDWICH 5-2. The first "Yes" in int_ant was said off camera, and the navy-jacket answer has the camera swinging through it, so both are cut. The navy-shirt golfer says "No" twice and counts once.
- **Ending:** the driver's "No", frozen for 0.8 s under the final tally. The interviewer's "four for four" line is cut.
- **Captions:** placeholder style (Inter ExtraBold, white on navy, active word light blue) until the client's caption style is on file.

## Avoid

- Any stretch where the camera pans or swings (it reads as tracking in 9:16), any crop that follows the camera's move, and any blurred frame. Where the camera pans off a speaker, hold their last sharp frame instead.
- Any answer said off camera.
- Framing anyone but the person holding the mic during an answer, in either shape.
- Counting, captioning or ending on the interviewer's own remarks.
- Counting the same person twice.
- Arian.MP4, any picture of Arian, and any amount raised, player count or next year's date.
- Music. No licensed track has been supplied.

## Done means

- [x] Frames every 0.25 s over the whole v7 preview, plus the first and last frame of all 10 cuts, in both shapes (`qa_dense.py`, 94 frames each). The speaker is in frame and sharp in every one, with no blurred frames and no caption spilling into the next shot.
- [x] Camera speed under about 75 source px/s in every cut except the first 0.2 s of Darryl's (100). The worst apparent drift in 9:16 is about 60 source px over 1.5 s (the first cart).
- [x] Back-to-back cuts from one clip join on the same frame, with no repeated frames.
- [x] Audio for all 10 cuts lines up with the source at a 0 ms offset, in both previews. Picture runs 18.97 s.
- [x] -14.2 LUFS integrated, true peak -1.4 dBFS, metadata read back with the comment "INTERNAL TEST v7 - not for posting"
- [x] Sidecars updated to v7, unslop check 0 strong
- [x] Previews sent to Rob
