# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v9, 8 Oct 2026. Not approved for posting.

A 17.0 s reel in 9:16 and 16:9: golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

## Build

```
# 1. footage: list.tsv is "<name>\t<Drive file id>" per line (not committed)
./dl.sh <scratch>                       # -> <scratch>/m25/raw/<name>.mp4
# 2. audio + transcripts (faster-whisper small.en, word timestamps)
for f in raw/*.mp4; do ffmpeg -v error -y -i $f -vn -ac 1 -ar 16000 audio/$(basename $f .mp4).wav; done
python transcribe.py audio transcripts
# 3. body (cuts, static crops, hook, tally, captions)
python build_reel1.py <m25_dir> 916
python build_reel1.py <m25_dir> 169
# 4. end card
cd ../../explainers/milas-mulligans && npx remotion render src/index.tsx End-9x16 out/end_9x16.mp4
```

Then `python finish_reel1.py <m25>/reel1 v9` joins body and end card (4.5 s of silence under the card), normalises to -14 LUFS with two-pass `loudnorm`, writes R0BATO metadata with the comment marked internal and makes the chat previews. Write a `_SOCIAL_COPY.txt` per file.

Before anything is called done, check the whole file:

```
python qa_dense.py <m25>/reel1/timeline_v9.json <final or preview>.mp4 qa_916.png 150 267   # 9:16
python qa_dense.py <m25>/reel1/timeline_v9.json <final or preview>.mp4 qa_169.png 240 135   # 16:9
```

It pulls a frame every 0.25 s over the whole file plus the first and last frame of every cut. Look at every frame: the person talking must be in frame, sharp and centred, with their whole face in. Transition frames are no exception. `qa_sheet.py` is a quicker first, middle and last frame pass.

Audio sync: `sync_check.py <video> <timeline.json> <m25>` cross-correlates every cut against its source.

Frozen frames: `ffmpeg -i <file>.mp4 -vf freezedetect=n=0.002:d=0.2 -an -f null -` must find nothing before the end card.

Camera motion: `camera_speed.py <m25> <clip> <in> <out>` measures camera speed on the background before a cut is chosen (keep 9:16 cuts under about 75 source px/s). `output_motion.py <video> <timeline.json>` measures apparent motion per cut in a rendered file.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre on the person talking, and zoom. No cut holds a frame. Wherever the speaker changes, the cut is split and the new speaker gets their own static crop. Every cut is snapped to whole frames. `YFRAC` lowers the 16:9 crop where a speaker sits low in frame.
- **Votes:** `VOTES` counts one vote per person in the cut. The final tally reads NOT A SANDWICH 5-1. In the second cart the trucker cap says "No" and the driver says "definitely not a sandwich": two people, one vote each, each framed on her own cut. The first "Yes" in int_ant was said off camera, the navy-jacket answer has the camera swinging through it, and the camera pans off the sunglasses answer mid-word, so all three are cut. The navy-shirt golfer says "No" twice and counts once.
- **Ending:** the driver's "definitely not a sandwich". Her shot plays on live under the final tally, and `MUTE` fades the sound right after "sandwich", so the low-confidence "No," and the interviewer's "all right, four for four" are never heard.
- **Captions and tally:** house style until the client's caption style is on file: Inter Display Black, white with a black outline, the spoken word in yellow, whole phrases of up to four words (`BREAK_BEFORE` forces a phrase break), each phrase popping in. The tally is a navy scoreboard with SANDWICH and NOT A SANDWICH columns; the number that changes pops in yellow, and the result gets a yellow FINAL tag with the losing side dimmed.

## Avoid

- Any stretch where the camera pans or swings (it reads as tracking in 9:16), any crop that follows the camera's move, and any blurred frame.
- Any frozen frame while someone talks. Where the camera pans off a speaker, cut on their last sharp frame or drop the answer.
- Any answer said off camera.
- Framing anyone but the person holding the mic during an answer, in either shape.
- Counting, captioning or ending on the interviewer's own remarks.
- Framing a line on whoever held the mic at the start of the sentence. Check the mouth on every word.
- Counting the same person twice.
- Arian.MP4, any picture of Arian, and any amount raised, player count or next year's date.
- Music. No licensed track has been supplied.

## Done means

- [x] Frames every 0.25 s over the whole v9 preview, plus the first and last frame of all 9 cuts, in both shapes (`qa_dense.py`, 83 frames each). The speaker is in frame and sharp in every one, with no blurred frames and no caption or graphic spilling into the next shot.
- [x] The second cart checked mouth by mouth at 15 frames a second (56.6-59.0 s): trucker cap "No", driver "it's definitely not a sandwich".
- [x] `freezedetect` finds no frozen stretch of 0.2 s or more before the end card (12.47 s), in either final.
- [x] Apparent motion per cut in 9:16 peaks at 82 px/s (Ava's hook) and averages 40 or less; the ending cuts measure 0-20.
- [x] Audio for all 9 cuts lines up with the source within 1 ms (`sync_check.py`), in both previews. Sound after the driver's last word measures -63 dB.
- [x] -14.3 LUFS integrated, true peak -1.5 dBTP, metadata read back with the comment "INTERNAL TEST v9 - not for posting"
- [x] Sidecars updated to v9, unslop check 0 strong
- [x] Previews sent to Rob
