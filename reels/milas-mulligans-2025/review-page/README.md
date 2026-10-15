# Mila's reel review page

Published (private until Rob shares it): https://claude.ai/artifact/LYgrb7NjKyp3B1UHrquSFF

One page with the three throwback reels (hot dog v19, Mayo or sand? v4, Guess the 50-50 v3), each reel's Instagram caption, pinned comment and Facebook text, and a review form: name, role or organization, a decision (Approved / Approved with small changes / Needs changes) and notes.

- `template.html` is the page; `data.json` holds the captions (pulled from `../copy/*_SOCIAL_COPY.txt`) and the video links. The published page is `template.html` with `__DATA__` replaced by `data.json`.
- Videos are review copies made from the finals to fit the page's 20 MiB per-file limit: 1080x1920, two-pass H.264 at about 19 MB, audio copied from the final (loudness unchanged). Full-quality finals stay out of git.
- Reviews are stored in the page's database, one document per reviewer at `reviews/<their id>`; everyone who can open the page reads them, each reviewer writes only their own. Submitting needs a signed-in viewer with Contributor access.
