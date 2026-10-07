# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v5, 7 Oct 2026. Not approved for posting.

A 21.0 s reel in 9:16 and 16:9: golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

## Build

```
# 1. footage: list.tsv is "<name>\t<Drive file id>" per line (not committed)
./dl.sh <scratch>                       # -> <scratch>/m25/raw/<name>.mp4
# 2. audio + transcripts (faster-whisper small.en, word timestamps)
for f in raw/*.mp4; do ffmpeg -v error -y -i $f -vn -ac 1 -ar 16000 audio/$(basename $f .mp4).wav; done
python transcribe.py audio transcripts
# 3. body (cuts, static crops, whip blur, hook, tally, captions, -14 LUFS)
python build_reel1.py <m25_dir> 916
python build_reel1.py <m25_dir> 169
# 4. end card
cd ../../explainers/milas-mulligans && npx remotion render src/index.tsx End-9x16 out/end_9x16.mp4
```

Then join body and end card (4.5 s of silence under the card), normalise the final to -14 LUFS with two-pass `loudnorm`, write R0BATO metadata with the comment marked internal, and write a `_SOCIAL_COPY.txt` per file.

Before anything is called done, check the whole file:

```
python qa_sheet.py <m25>/reel1/timeline_v5.json <final or preview>.mp4 qa_916.png 160 284   # 9:16
python qa_sheet.py <m25>/reel1/timeline_v5.json <final or preview>.mp4 qa_169.png 320 180   # 16:9
```

It pulls the first, middle and last frame of every cut, plus the end of the file. Look at every frame.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre on the person holding the mic, zoom and whip-blur window. Wherever the mic moves to someone else, the cut is split and the new speaker gets their own static crop. Every cut is snapped to whole frames.
- **Votes:** `VOTES` counts one vote per person in the cut. The final tally reads NOT A SANDWICH 6-3. The navy-shirt golfer says "No" twice and counts once.
- **Ending:** the driver's "No", frozen for 0.8 s under the final tally. The interviewer's "four for four" line is cut.
- **Captions:** placeholder style (Inter ExtraBold, white on navy, active word light blue) until the client's caption style is on file.

## Avoid

- Any crop that follows the camera's own move. One static crop per cut, and a sideways blur on the camera's whip.
- Framing anyone but the person holding the mic during an answer, in either shape.
- Counting, captioning or ending on the interviewer's own remarks.
- Counting the same person twice.
- Arian.MP4, any picture of Arian, and any amount raised, player count or next year's date.
- Music. No licensed track has been supplied.

## Done means

- [x] Frames from the rendered v5 finals and previews, at the first, middle and last frame of all 14 cuts plus the end card, in both shapes (`qa_sheet.py`)
- [x] Every answer framed on whoever holds the mic, from the first frame of its cut to the last. Speakers identified by mic position, mouth movement and audio level.
- [x] Audio for all 14 cuts lined up against the source at 0 ms offset. Picture 21.033 s.
- [x] -14.2 LUFS integrated, true peak -1.4 dBFS, metadata read back with the comment "INTERNAL TEST v5 - not for posting"
- [x] Sidecars updated to v5, unslop check 0 strong
- [x] Previews sent to Rob
