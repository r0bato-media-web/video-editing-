# Mila's Mulligans 2025 throwback: "Is a hot dog a sandwich?"

Internal test v19, 15 Oct 2026: the internal final (Rob, 15 Oct 2026: "v19 is good"). Not approved for posting: needs the client's OK and Rob's go per post.

A 22.0 s vertical reel (9:16 only; Rob, 14 Oct 2026: no horizontal version): golfers from Mila's Mulligans 2025 answer the question, a live tally counts the votes, and the end card (`End-*` in `explainers/milas-mulligans`) says where the money goes. Footage: the "2025 Milas Mulls" Drive folder, captured by Tony. Footage and renders stay out of git.

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

Then `mkdir -p <m25>/reel1/finals <m25>/reel1/previews` and `python finish_reel1.py <m25>/reel1 v19` dissolves the body into the end card over 0.35 s (the card starts past its blank first frames; silence under the card), normalises to -14 LUFS with two-pass `loudnorm` plus an oversampled limiter for true peak, writes R0BATO metadata with the comment marked internal and makes the chat previews (audio copied from the final, so the preview measures the same). Write a `_SOCIAL_COPY.txt` per file.

Before anything is called done, check the whole file:

```
python qa_dense.py <m25>/reel1/timeline_v19.json <final or preview>.mp4 qa_916.png 150 267   # 9:16
```

It pulls a frame every 0.25 s over the whole file plus the first and last frame of every cut. Look at every frame: the person talking must be in frame, sharp and centred, with their whole face in. Transition frames are no exception. `qa_sheet.py` is a quicker first, middle and last frame pass.

Audio sync: `sync_check.py <video> <timeline.json> <m25>` cross-correlates every cut against its source.

Frozen frames: `ffmpeg -i <file>.mp4 -vf freezedetect=n=0.002:d=0.2 -an -f null -` must find nothing before the end card.

Camera motion: `camera_speed.py <m25> <clip> <in> <out>` measures camera speed on the background before a cut is chosen (keep 9:16 cuts under about 75 source px/s). `output_motion.py <video> <timeline.json>` measures apparent motion per cut in a rendered file.

## Export rule (Rob, 16 Oct 2026)

The finals are H.264 High 4:4:4 (yuv444p). Treat them as masters only. Every review, preview, phone or delivery copy is made 4:2:0: `-profile:v high -level 4.1 -pix_fmt yuv420p -movflags +faststart`, audio copied. iPhones and Safari can't play 4:4:4. The finish scripts' previews follow this from 16 Oct; previews and phone copies made before that are 4:4:4.

## Brief

- **Cuts:** in `CUTS` at the top of `build_reel1.py`, each with its source clip, in and out, crop centre on the person talking, and zoom. No cut holds a frame. Wherever the speaker changes, the cut is split and the new speaker gets their own static crop. Every cut is snapped to whole frames. `YFRAC` lowers the crop where a speaker sits low in frame.
- **Votes:** `VOTES` counts one vote per person in the cut. The final tally reads NOT A SANDWICH 7-2. In the first cart the black-cap friend says "No" and the trucker cap says "not a sandwich": two voices, one vote each, each on their own cut. On the course there are four golfers and four answers, each on its own cut: pink shirt "Yes", navy shirt "No", floral shirt "No", white shirt "Yes" (the interviewer's "split answers"). Each was matched by mouth at full resolution and by voice pitch. In the second cart the trucker cap says "No" and the driver says "definitely not a sandwich": two people, one vote each, each framed on their own cut. The navy-jacket answer has the camera swinging through it, and the camera pans off the sunglasses answer mid-word, so both are cut. The navy-shirt golfer says "No" twice and counts once.
- **Darryl:** the answer runs from "A hot dog in my book is" through "not a sandwich" (punch-in, the vote) and on to the end of the turn, "A hot dog is in a casing, bro." (v19, Rob 15 Oct 2026: "you cut off people's answers too early", then "in a casing bro"). Out at 42.95, just before the interviewer's "Alright" (43.07). The transcript heard "in case", so `WORD_FIX` carries Rob's wording; medium.en heard "in the casing, bruh" and small.en "encasing, bro".
- **Ending:** the driver's "definitely not a sandwich. No." The closing "No" is the driver's by mouth and voice; it's captioned and not counted again. The driver's shot plays on live while the picture dims and a big FINAL card pops up in the middle (FINAL, NOT A SANDWICH, 7-2, one line after another), held about 1.5 s before dissolving into the end card (cap, scholarship line, link; no "We play for Arian." since v18, Rob 14 Oct 2026), and `MUTE` fades the sound right after that "No", so the interviewer's "all right, four for four" is never heard.
- **Sound:** a pop on every scoreboard change and a boom 0.15 s ahead of the FINAL card, with a softer pop on the card itself. `sfx/pop.wav` and `sfx/boom.wav` are made from scratch by `make_sfx.py` (no samples) as stand-ins, because the approved kit (`R0BATO TOOLKIT/assets/sfx/`) is on the SSD (Rob, 14 Oct 2026: "make the sounds using whatever you can"). Swap in `cute_pop.wav` and `vine_boom.wav` when the kit is reachable. Each pop sits 6 dB under the voice it lands on (`POP_DB`), so the one-word answers stay clear; `sfx_<v>.json` logs every hit's time and gain.
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

- [x] v19 (15 Oct 2026) changes only Darryl's cut: out 42.95 (was 39.22), captions "A HOT DOG IS / IN A CASING, / BRO" from `WORD_FIX`; everything after it moves 3.73 s later. Body 17.90 s, final 22.0 s. 88 frames every 0.25 s over the whole final viewed: Darryl in the punch-in frame from 7.18 to 12.9 s, every other speaker in frame, scoreboard 2-3 through the line, FINAL 7-2, end card with the link and no "We play for Arian." Camera on the new stretch 0-25 source px/s, 18 px/s mean on screen. Audio of all 12 cuts within 2 ms of the source. -14.5 LUFS, true peak -1.4 dBFS on the final and the preview. No black frames; the only freeze starts at the end card (17.90 s); silence of 0.4 s or more starts at 17.64 s under the FINAL card (`MUTE`). Metadata read back: comment "INTERNAL TEST v19 - not for posting", no copyright tag. Pops measured against the source audio fitted to the final (method floor 13-30 dB under the voice): every pop from Darryl's on lands 1.9 to 6.0 dB under its voice; the first two course pops ("Yes" 3.05 s, "No" 3.55 s) read 2 to 4 dB over the voice in the 0.4 s after the hit. Those gains are unchanged since v17; Rob listened and kept them (15 Oct 2026: "the sound effect is fine").
- [x] v19 sidecar written fresh from the v19 video (the v18 one wasn't reachable): `copy/…HotDogSandwich…_SOCIAL_COPY.txt`, every claim sourced, no em dashes, 5 hashtags with #MilasMulligans first, unslop check 0 strong.
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

# Reel 2: "Mayo or sand?"

Internal final v3, approved by Rob 15 Oct 2026 ("Ok this cut is good"). Not approved for posting: that needs the client's OK and Rob's go per post. Filed in Drive MilasMulligans_FINALS_14Oct2026 / 04_MayoOrSand_v3.

v4, 15 Oct 2026 (Rob: "you cut off people's answers too early"), the internal final (Rob, 15 Oct 2026: "Ok to the videos approved"), replaces v3: the floral-shirt golfer's answer runs on through "I ain't doing that." (150 Hz, the golfer's voice; the interviewer is 229 Hz) to just before the interviewer's "Mayo all the way" (out 20.09, was 19.40). Every other cut was checked at both ends: the rest end on the last word of the turn and start on its first word. Two lines stay out on purpose: the blue polo's "Best condiment in the world" (the camera swings away at 300-376 px/s as it's said) and Darryl's "wash it out with more booze" (muted under FINAL since v1). v4 checks: 27.6 s, -14.1 LUFS, true peak -2.0 dBFS, sync within 1 ms, no black frames, no freeze before the end card, 111 frames every 0.25 s.

A 26.9 s vertical reel (22.8 s body + the same 4.5 s end card): ten golfers from Mila's Mulligans 2025 answer "would you rather eat a jar full of mayonnaise or a handful of sand?", a two-pill scoreboard (MAYO, SAND) counts the votes, and the FINAL card calls it: IT'S A TIE, 5-5. Darryl's "handful of sand all day every day" casts the tying vote and plays on live under FINAL, with the sound faded before "wash it out with more booze".

v2 (Rob, 14 Oct 2026: "you can stabilize them", "add jar of mayo or sand or sand castle, dress this up"):
- The three shaky cuts are stabilized with vidstab in tripod mode, locked to each cut's first frame, with a 6% punch-in (`stabilize`, `STAB_ZOOM`). Stabilizing the blue-polo cut too made it worse (120 against 100 px/s), so that one stays as shot.
- A mayo jar and a sand castle, drawn in `make_icons` (flat shapes in the reel's colors, ink outline, soft shadow; no clip art, no brand), sit in the scoreboard and pop when their side scores, pop in under the hook, and flank the 5-5 on the FINAL card. The pills are navy with a white edge so the icons read.

v3 (Rob, 14 Oct 2026: "No fun pic of Elote?", "you cut off the guy saying mayo is disgusting too early"):
- A drawn elote (`INSERTS`, `make_icons`) pops in on "elotes" with a pop 6 dB under the word and stays to the end of the sentence, right of the speaker's face.
- The blue-shirt cut now ends at 20.10, not 19.66. Whisper put the end of "disgusting" at 19.58; the audio shows the word running to about 19.80, then quiet until the next line at 20.20. Lesson: set a cut's out point from the audio's own tail, never from the transcript's word end.

## Build

```
# footage: list.tsv names are ant, darryl, frankie, interview3, jasmin_bf (Drive "2025 Milas Mulls" / TONY CONTENT)
./dl.sh <scratch>                         # then audio + transcripts as for reel 1
python build_reel2.py <m25_dir> v3        # -> <m25>/reel2/body_v2_916.mp4, timeline, captions, sfx_v2.json, mix_dry/wet_v2.wav
cp <End-9x16 render> <m25>/reel2/end_9x16.mp4
python finish_reel2.py <m25_dir> v3       # -> reel2/finals/ and reel2/previews/, -14 LUFS, metadata, copyright blank
python qa_pops.py <m25>/reel2 v3          # every sound effect against the voice it lands on, in the real mix
```

Pops sit about 6 dB under the voice they land on: `build_reel2.py` sets each gain from the vote word's loudest 50 ms in the source, and `qa_pops.py` measures the result in the mix (wet minus dry is the effects alone). Sounds are still the `make_sfx.py` stand-ins until `cute_pop.wav` and `vine_boom.wav` from the kit are reachable.

Votes, checked by mic position and mouth on the word: Mayo, frankie 42.22 (blue polo), frankie 15.28 (black shirt), ant 7.64 (pink), ant 9.48 (floral), jasmin_bf 36.48 (grey polo). Sand, interview3 19.10 (floral shirt, glasses), frankie 18.30 (blue shirt, beard), ant 8.84 (navy), ant 10.12 (white), darryl 8.12. Not counted: interview3 20.12 "Mayo all the way" (the interviewer teasing, on-mic level; the golfer answers "No, I can't slug mayo like that") and interview3 31.22 "Mayo." (-47 dB, off the mic, nobody on camera says it). Copy: `copy/MilasMulligans_Throwback2025_MayoOrSand_9x16_INTERNALTEST_RobatoMedia_SOCIAL_COPY.txt`.

## Done means (v3)

- [x] Frames every 0.25 s plus first and last frame of all 11 cuts (`qa_dense.py`, 111 frames); hook, scoreboard and FINAL at 540 px wide; first and last frame of each stabilized cut pulled by frame index. Every speaker's whole face is in frame on their answer, no icon covers text or a face, no stabilization edge shows.
- [x] Cuts land on their planned frames (frame-difference check on v2: 88, 144, 192, 317, 393, 417, 448, 468, 485, 525; v3 moves every cut after the blue-shirt answer 13 frames later), and all 11 cuts' audio lines up with the source within 2 ms on v3 (`sync_check.py`).
- [x] v3: frames through the elote insert (on at "elotes", clear of the speaker's face, off after "mayonnaise") and the blue-shirt cut's new end ("disgusting" whole, the hand wave in).
- [x] Apparent motion, output px/s max: stabilized cuts 63 (interview3), 80 (ant floral), 60 (ant white), down from 184, 161 and 341. Highest left is the blue-polo cut at 100, in its last 0.1 s after the word.
- [x] -14.1 LUFS integrated, true peak -2.0 dBFS (v3); no black frames; `freezedetect` finds nothing before the end card; the only silence of 0.4 s or more is the end card.
- [x] `qa_pops.py` on v3: every vote pop 6.0 to 8.2 dB under its voice, the elote pop 6.0 under "elotes"; the boom at the voice's level; the FINAL pop 6 dB under the reel's loudest answer, in silence after the fade.
- [x] 1080x1920, 30 fps, H.264 + AAC 48 kHz stereo; metadata read back with "INTERNAL TEST v3 - not for posting" and no copyright tag.
- [x] Sidecar updated to v3, unslop check 0 strong; copy in Drive 02 INTERNAL / MilasMulligans_MayoOrSand_v3_INTERNALTEST_14Oct2026.
- [ ] Swap in `cute_pop.wav` / `vine_boom.wav`.
- [x] Rob approved v4 (Rob, 15 Oct 2026: "Ok to the videos approved").

# Reel 3: "Guess the 50-50"

Internal final v3, 15 Oct 2026 (Rob, 15 Oct 2026: "Ok to the videos approved"). Not approved for posting: needs the client's OK and Rob's go per post.

A 60.2 s vertical reel (56.1 s body + the same end card). The interviewer asks how much the 50-50 will reach, then twelve golfers from Mila's Mulligans 2025 answer, lowest to highest: $575, $675, $700, $725, $855, $1,150, $2,000, $2,300, $2-3K, $5,000, $7,000, $11,000. A drawn raffle ticket at the top shows "GUESS #n" and "$ ?", and the number pops in on the first word of the guess, with a pin on a log-scale number line ($500 to $10K) that stays for the rest of the reel. The real 2025 total isn't on file, so there is no reveal (Rob, 15 Oct 2026: "Make a third video now"). It ends on the last golfer's live shot, dimmed and muted after the laugh, with "12 GUESSES", "$575 TO $11,000", "WHAT DID IT HIT?" and "COMMENT YOUR GUESS", then the end card.

- **Who said what.** Every guess was checked by mic position and mouth on the number at full resolution, and by voice pitch in the jasmin_dad group (blue cap 198 Hz, backwards cap 142 Hz, teal glasses 198 Hz with a different face and glasses, interviewer 262 Hz). One guess per person. The interviewer's repeats are never used ("675.", "21-50", "Two, 3,000.", "Last person said 675", "Show me the money").
- **Dropped for camera motion.** jasmin_dad "21-50" (pan up to 226 px/s through the answer; vidstab tripod mode left 146 to 827 px/s) and "I say 1,500" (125-150 px/s on the word; two stabilizing tries each jumped 200+ px/s on "500", so it stopped there).
- **Out points: the end of the person's turn** (v2, Rob, 15 Oct 2026: "you cut off people's answers too early"). v1 cut at the first dip in level after the number, which dropped the rest of what people said: "Book it.", "That's my guess." and the $2,000 golfer's "And that's a great prize today for anybody who's involved in the 50-50." Each answer now runs through the rest of the sentence, any sign-off or laugh, to just before the interviewer's next word (checked by mic, mouth and pitch on every tail). The $2,000 golfer steps left during the extra sentence (the tree behind holds still, so it's the person, not the camera), so that answer is two static crops split at the sentence break after "$1,000 each."
- **Lesson:** the number is not the end of the answer. Listen past it to the end of the turn before choosing the out point.
- **In points: the start of the person's turn** (v3, Rob, 15 Oct 2026: "The start of the second answer was cut off too"). The interview2 transcript squeezed "Six hundred and seventy-five dollars" into "675" at 15.54, so the cut began after "Six hundred and". `WORD_FIX` replaces those words with a medium.en / small.en re-transcription (both agree) timed from the voice onset at 14.50, and the cut starts at 14.40. Every guess was re-transcribed with medium.en to check its words and start: no other guess lost words, but two started mid-turn and now start on the golfer's first word: $5,000 at "If everybody plays," (81.35, crop moved to x 1300 so the golfer stays in frame through it) and $7,000 at "Oh my God, that's a good question." (36.86, the golfer's own voice by pitch). A start is clipped when the person is already talking at the cut; a clean start after a pause ("I'm going to go a little bit north...") is not.
- **Lesson:** check the level and the pitch in the second before an in point, not only the transcript. Speech the transcript missed is still speech.
- **Numbers in the transcript.** Whisper splits spoken numbers ("5" + "-75.", "$11" + ",000."). `all_words` joins them back, the ticket, pin and pop land on the joined word's first frame (the same frame its caption appears), and "5-75" / "7.25" are captioned 575 / 725 like the ticket.

## Build

```
python build_reel3.py <m25_dir> v3        # -> <m25>/reel3/body_v3_916.mp4, timeline, captions, sfx_v3.json, mix_dry/wet_v3.wav
cp <End-9x16 render> <m25>/reel3/end_9x16.mp4
python finish_reel3.py <m25_dir> v3       # -> reel3/finals/ and reel3/previews/, -14 LUFS, metadata, copyright blank
python qa_pops.py <m25>/reel3 v3
```

Clip names are the list.tsv names; random_guy, interview2, jasmin_dad, angel and evan_darien_int read their audio from `<m25>/audio2/`. Copy: `copy/MilasMulligans_Throwback2025_Guess5050_9x16_INTERNALTEST_RobatoMedia_SOCIAL_COPY.txt`.

## Done means (v3)

- [x] v3: every cut's in point checked by level and pitch in the second before it, plus a medium.en re-transcription of every guess; the $675, $5,000 and $7,000 answers start on the golfer's first word. 241 frames every 0.25 s across the whole final, every speaker in frame; audio of all 14 cuts within 1 ms; -14.0 LUFS, true peak -1.9 dBFS on the final and the preview; no black frames, no freeze before the end card (56.13 s); every guess pop 6.0 to 7.8 dB under its voice.
- [x] v2: every cut's tail listened through to the next speaker; the tails added are the golfer's own words or laugh (mic, mouth, pitch); the $2,000 golfer in frame through the step (two static crops, 470 then 340, split at the sentence break).
- [x] v2: 223 frames every 0.25 s across the whole final; audio of all 14 cuts within 1 ms of the source; -14.1 LUFS, true peak -1.6 dBFS on the final and the preview; no black frames, no freeze before the end card (51.70 s); every guess pop 6.0 to 7.8 dB under its voice.
- [x] v1 checks, kept for the record: frames every 0.25 s across the whole final (190 frames, 180 px) plus key frames at 360 px: every speaker in frame on their guess, the ticket and number line clear of faces, captions clear of the Reels caption area, the question held about 1.5 s on live footage before the end card dissolve.
- [x] Each ticket number, its pin, its pop and its caption land on the same frame (first word of the number); v1's first pass popped up to 2 s after the caption and was fixed before sending.
- [x] Audio of all 13 cuts lines up with the source within 1 ms (`sync_check.py`).
- [x] -14.0 LUFS integrated, true peak -1.9 dBFS on the final and the preview; no black frames; `freezedetect` finds nothing before the end card (43.47 s). Silence of 0.4 s or more starts at 42.59 s: the last 0.9 s of the muted question shot, then the end card.
- [x] `qa_pops.py`: every guess pop 6.0 to 7.8 dB under its voice (v1's first pass measured the whole joined number and put three pops level with or over the voice; now measured over the 0.4 s from the hit); boom at the loudest guess's level, question pop 6 dB under it.
- [x] Source camera motion under about 50 px/s on every cut used (`camera_speed.py`); the two cuts over it were dropped, not stabilized.
- [x] 1080x1920, 30 fps, H.264 + AAC 48 kHz stereo; metadata read back with "INTERNAL TEST v1 - not for posting" and no copyright tag.
- [x] Sidecar with every guess's source and timecode, unslop check 0 strong.
- [ ] Swap in `cute_pop.wav` / `vine_boom.wav`.
- [x] Rob approved v3 (Rob, 15 Oct 2026: "Ok to the videos approved").
- [ ] A reveal ending, once the client gives the 2025 total in writing.
