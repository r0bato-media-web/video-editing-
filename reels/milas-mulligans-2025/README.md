# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v18, 14 Oct 2026. Not approved for posting.

A 18.3 s vertical reel (9:16 only; Rob, 14 Oct 2026: no horizontal version): golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

## Build

```
# 1. footage: list.tsv is "<name>\t<Drive file id>" per line (not committed)
./dl.sh <scratch>                       # -> <scratch>/m25/raw/<name>.mp4
# 2. audio + transcripts (faster-whisper small.en, word timestamps)
for f in raw/*.mp4; do ffmpeg -v error -y -i $f -vn -ac 1 -ar 16000 audio/$(basename $f .mp4).wav; done
python transcribe.py audio transcripts
# 3. sound + body (cuts, static crops, hook, tally, captions, pops and boom)
python make_sfx.py <m25_dir>/sfx      # or copy sfx/*.wav from this folder
python build_reel1.py <m25_dir> 916
# 4. end card
cd ../../explainers/milas-mulligans && npx remotion render src/index.tsx End-9x16 out/end_9x16.mp4
```

Then `python finish_reel1.py <m25>/reel1 v18` dissolves the body into the end card over 0.35 s (the card starts past its blank first frames; silence under the card), normalises to -14 LUFS with two-pass `loudnorm` plus an oversampled limiter for true peak, writes R0BATO metadata with the comment marked internal and makes the chat previews (audio copied from the final, so the preview measures the same). Write a `_SOCIAL_COPY.txt` per file.

Before anything is called done, check the whole file:

```
python qa_dense.py <m25>/reel1/timeline_v18.json <final or preview>.mp4 qa_916.png 150 267   # 9:16
```

It pulls a frame every 0.25 s over the whole file plus the first and last frame of every cut. Look at every frame: the person talking must be in frame, sharp and centred, with their whole face in. Transition frames are no exception. `qa_sheet.py` is a quicker first, middle and last frame pass.

Audio sync: `sync_check.py <video> <timeline.json> <m25>` cross-correlates every cut against its source.

Frozen frames: `ffmpeg -i <file>.mp4 -vf freezedetect=n=0.002:d=0.2 -an -f null -` must find nothing before the end card.

Camera motion: `camera_speed.py <m25> <clip> <in> <out>` measures camera speed on the background before a cut is chosen (keep 9:16 cuts under about 75 source px/s). `output_motion.py <video> <timeline.json>` measures apparent motion per cut in a rendered file.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre on the person talking, and zoom. No cut holds a frame. Wherever the speaker changes, the cut is split and the new speaker gets their own static crop. Every cut is snapped to whole frames. `YFRAC` lowers the crop where a speaker sits low in frame.
- **Votes:** `VOTES` counts one vote per person in the cut. The final tally reads NOT A SANDWICH 7-2. In the first cart the black-cap friend says "No" and the trucker cap says "not a sandwich": two voices, one vote each, each on her own cut. On the course there are four golfers and four answers, each on its own cut: pink shirt "Yes", navy shirt "No", floral shirt "No", white shirt "Yes" (the interviewer's "split answers"). Each was matched by mouth at full resolution and by voice pitch. In the second cart the trucker cap says "No" and the driver says "definitely not a sandwich": two people, one vote each, each framed on her own cut. The navy-jacket answer has the camera swinging through it, and the camera pans off the sunglasses answer mid-word, so both are cut. The navy-shirt golfer says "No" twice and counts once.
- **Ending:** the driver's "definitely not a sandwich. No." Her closing "No" is hers by mouth and voice; it's captioned and not counted again. Her shot plays on live while the picture dims and a big FINAL card pops up in the middle (FINAL, NOT A SANDWICH, 7-2, one line after another), held about 1.5 s before dissolving into the end card (cap, scholarship line, link; no "We play for Arian." since v18, Rob 14 Oct 2026), and `MUTE` fades the sound right after her "No", so the interviewer's "all right, four for four" is never heard.
- **Sound:** a pop on every scoreboard change and a boom 0.15 s ahead of the FINAL card, with a softer pop on the card itself. `sfx/pop.wav` and `sfx/boom.wav` are made from scratch by `make_sfx.py` (no samples) as stand-ins, because the approved kit (`R0BATO TOOLKIT/assets/sfx/`) is on the SSD (Rob, 14 Oct 2026: "make the sounds using whatever you can"). Swap in `cute_pop.wav` and `vine_boom.wav` when the kit is reachable. Each pop sits 6 dB under the voice it lands on (`POP_DB`), so the one-word answers stay clear; `sfx_v17.json` logs every hit's time and gain.
- **Captions and tally:** house style until the client's caption style is on file: Inter Display Black, white with a black outline, the spoken word in yellow, whole phrases of up to four words (`BREAK_BEFORE` forces a phrase break), each phrase popping in. The tally is a hot dog: golden bun carrying the SANDWICH and NOT A SANDWICH labels, the score on the sausage, a mustard squiggle that breaks around the numbers. The number that changes flashes mustard and settles to white; at the end the winner's number turns mustard and the loser's dims, under the big FINAL card.

## Avoid

- Any stretch where the camera pans or swings (it reads as tracking in 9:16), any crop that follows the camera's move, and any blurred frame.
- Any frozen frame while someone talks. Where the camera pans off a speaker, cut on their last sharp frame or drop the answer.
- Any answer said off camera.
- Framing anyone but the person holding the mic during an answer.
- Counting, captioning or ending on the interviewer's own remarks.
- Framing a line on whoever held the mic at the start of the sentence. Check the mouth on every word.
- Counting the same person twice.
- Arian.MP4, any picture of Arian, and any amount raised, player count or next year's date.
- Music. No licensed track has been supplied.
- A pop louder than the answer it lands on. The first v17 mix at a flat -5 dB was up to 13 dB over the quiet course answers.

## Done means

- [x] v18 changes only the end card. Audio is bit-identical to v17; frames before the dissolve match v17 at 63.8 dB PSNR on average (encoding noise only); the dissolve and the card checked frame by frame, with the link on the last frame.
- [x] v17's picture is the v16 picture frame for frame (decoded-frame MD5s match on the body and the final), so the v16 frame checks below still hold.
- [x] Every sound lands within 2 ms of its graphic, and each pop measures 3 to 7 dB under the voice around it (v17 audio minus v16, loudest 50 ms windows).
- [x] Frames every 0.25 s over the whole v16 preview, plus the first and last frame of all 12 cuts (`qa_dense.py`, 96 frames). The speaker is in frame and sharp in every one, with no blurred frames and no caption or graphic spilling into the next shot.
- [x] Every golfer in each group accounted for, mouth by mouth at full resolution: the course four (int_ant 15.9-18.9 s, plus voice pitch per answer) and both carts (int_hotdog 43.5-45.2 s and 56.6-59.0 s, plus voice pitch).
- [x] `freezedetect` finds no frozen stretch of 0.2 s or more before the end card (14.17 s).
- [x] Apparent motion per cut in 9:16 peaks at 82 px/s (Ava's hook); the white-shirt cut averages 70, the other course cuts 22 or less.
- [x] The join into the end card checked frame by frame: no blank frames, the FINAL card holds about 1.5 s on live footage and stays clear of the end card's cap in the dissolve.
- [x] Audio for all 12 cuts lines up with the source within 2 ms (`sync_check.py`).
- [x] v17: -14.4 LUFS integrated, peak -1.8 dB on the final and the preview, metadata read back with the comment "INTERNAL TEST v18 - not for posting" and no copyright tag
- [x] Sidecar updated to v18 (unsourced "did not go the way we expected" replaced with "Nine golfers, nine answers."), unslop check 0 strong
- [x] Previews sent to Rob
