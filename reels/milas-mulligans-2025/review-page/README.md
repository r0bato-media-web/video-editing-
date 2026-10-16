# Mila's reel review page

Published (private until Rob shares it): https://claude.ai/artifact/LYgrb7NjKyp3B1UHrquSFF

One page with the three throwback reels (hot dog v19, Mayo or sand? v4, Guess the 50-50 v3), each reel's Instagram caption, pinned comment and Facebook text, and a review form: name, a decision (Approved / Approved with small changes / Needs changes) and notes. An "Add time" button stamps the video's current time (like 0:12) into the notes, and times in submitted notes jump the video to that moment. Each review shows the day and time it was submitted.

- `template.html` is the page; `data.json` holds the captions (pulled from `../copy/*_SOCIAL_COPY.txt`) and the video links; `schedule.json` holds the posting calendar (proposed dates from `briefs/milas-mulligans-metricool.md`). The published page is `template.html` with `__DATA__` and `__SCHEDULE__` replaced by those two files. The calendar follows the Build & Burn approvals page: a month grid, a dot per post, tap a date to see what goes out.
- Videos are review copies made from the finals to fit the page's 20 MiB per-file limit: 1080x1920, H.264 High profile, level 4.1, **yuv420p**, two-pass at about 19 MB, faststart, audio copied from the final (loudness unchanged). The first upload (15 Oct) was High 4:4:4 (yuv444p), which iPhones and Safari can't play; replaced 16 Oct 2026 (Rob). Command per file:
  `ffmpeg -i <final> -map 0 -c:v libx264 -profile:v high -level 4.1 -pix_fmt yuv420p -preset slow -b:v <kbps> -pass 1 -an -f mp4 /dev/null` then the same with `-pass 2 -c:a copy -movflags +faststart <out>`, where kbps = 19.4 MB x 8 / duration - 200.
  A CRF 18 export (Rob's command) comes out at 23.4, 25.8 and 37.7 MB, over the page's limit; use those where size doesn't matter. Full-quality finals stay out of git.
- Reviews are stored in the page's database, one document per reviewer at `reviews/<their id>`; everyone who can open the page reads them, each reviewer writes only their own. Submitting needs a signed-in viewer with Contributor access.
