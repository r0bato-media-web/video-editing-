# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v4, 7 Oct 2026. Not approved for posting.

A 22.5 s reel in 9:16 and 16:9: golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

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

Then join body and end card (4.5 s of silence under the card, 0.34 s audio fade at the end of the body), write R0BATO metadata with the comment marked internal, and write a `_SOCIAL_COPY.txt` per file.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre, zoom and whip-blur window.
- **Votes:** `VOTES` counts only answers that are in the cut. The final tally reads NOT A SANDWICH 6-3.
- **Captions:** placeholder style (Inter ExtraBold, white on navy, active word light blue) until the client's caption style is on file.

## Avoid

- Any crop that follows the camera's own move. One static crop per cut, and a sideways blur on the camera's whip.
- Framing anyone but the person holding the mic during an answer.
- Counting or captioning the interviewer's own remarks as an answer.
- Arian.MP4, any picture of Arian, and any amount raised, player count or next year's date.
- Music. No licensed track has been supplied.

## Done means

- [x] Frames from the rendered v4 finals from 5.50 to 8.00 s, through the cut 3 to 4 whip, in both shapes. The other cuts are unchanged from v3, where frames were checked at every cut.
- [x] Every answer framed on whoever holds the mic, from the first frame of its cut to the last
- [x] Captions come from the transcript word timings, and every quote's time range is listed in the sidecar
- [x] -14.9 LUFS integrated, 22.508 s, metadata read back with the comment "INTERNAL TEST v4 - not for posting"
- [x] Sidecars updated to v4, unslop check 0 strong
- [x] Previews sent to Rob
