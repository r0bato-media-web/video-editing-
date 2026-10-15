# Mila's Mulligans: Metricool write-up

Internal. Pulled read-only from Metricool on 14 Oct 2026. Nothing was scheduled, sent for review or posted.

## Where the account stands

- Metricool brand "milasmulligans" (id 7278866), joined 6 Oct 2026, time zone America/New_York.
- Connected: Instagram @milasmulligans only. Facebook is not connected, though the brief plans Facebook for the 16:9 explainers. TikTok isn't connected either.
- Scheduled posts from 14 Oct to 31 Dec: none.

## Instagram, 5 Aug to 14 Oct 2026

Metricool's history for this account starts 5 Aug.

| Measure | Number |
|---|---|
| Followers | 250 on 13 Oct (249 on 5 Oct) |
| Posts and reels | 16, of them 4 reels |
| Reel views | 4,463 across the 4 reels |
| Average reach per reel | 712 |
| Average reach per post | 509 |
| Reel engagement | 6.2% |
| Engagement, all posts | 4.2% |
| Last post | 12 Sep 2026 |

The four reels:

| Date | Views | Interactions that day | Reel shares that day |
|---|---|---|---|
| 10 Aug | 1,112 | 25 | 9 |
| 18 Aug | 1,666 | 91 | 20 |
| 21 Aug | 931 | 60 | 4 |
| 12 Sep | 754 | 35 | 2 |

Two things stand out. Reels reach about 40% more people than the account's other posts (712 against 509), and the best one, on 18 Aug, ran four days before the tournament. The account has posted nothing since 12 Sep. Since 14 Sep, daily reach has stayed under 12 people on all but two days (41 on 22 Sep, 55 on 23 Sep). The backlog of finished pieces can fix that.

## When to post

Metricool's best-time model for this account, for the week of 19 Oct (higher is better):

| Slot | Score |
|---|---|
| Fri 10 am | 6,734 |
| Wed 10 am | 6,506 |
| Thu 10 am | 6,275 |
| Mon 10 am | 5,528 |
| Thu 6 pm | 5,078 |
| Sat 10 am | 3,409 |
| Sun 10 am | 2,582 |

Weekday mornings at 10 win every day. Weekends score about half. The evening slot at 6 pm is the backup on Tue to Thu.

## Proposed order, for Rob to OK or change

None of these are scheduled. Each needs Rob's OK for that post, and the client's OK where the piece is still an internal test.

| Slot | Piece | Note |
|---|---|---|
| Wed 21 Oct, 10 am | Hot dog reel v19 | Strongest finished piece. Talking reel, so it gets the Instagram music bed |
| Fri 23 Oct, 10 am | Where your mulligan goes, one style, 9:16 | Silent explainer. The other style goes to Facebook once it's connected |
| Wed 28 Oct, 10 am | Mayo or sand? v4 | Internal final, approved by Rob 15 Oct. Talking reel, so it gets the Instagram music bed. SFX kit swap still to do |
| After Mayo or sand? | Guess the 50-50 v3 | Internal final, approved by Rob 15 Oct. No reveal, so it can go before the total is known. Don't answer "what did it hit?" in the comments without the client's written number |

One post a week after that, on Wednesday or Friday at 10 am, keeps the account alive until next year's date is out.

## How each one goes in, once Rob says go

- Talking reels on Instagram get an instrumental from Instagram's library in `instagramData.audioConfiguration`, `audioVolume` 10, `videoVolume` 100 (the r0bato-video rule from 28 Sep 2026). Search a term first, then set the numeric id of an instrumental. After it posts, check the sound label on the live Reel and have Rob listen.
- The silent explainers can take a music bed too. That's Rob's call per post.
- Captions come from each piece's `_SOCIAL_COPY.txt`. The sidecars are in Drive, MilasMulligans_FINALS_14Oct2026, and all three reels' copy is in `reels/milas-mulligans-2025/copy/`; the review page shows the same captions.
- Facebook can't take music through Metricool.

## What Rob needs to do

- Connect the Mila's Mulligans Facebook page to this Metricool brand, if the client wants Facebook.
- Say go per post. "Send for review" in Metricool is a way to get the client's OK without anything going live.

## What to watch after each post

Reel views, shares and saves at 48 hours and 7 days, compared with the 18 Aug reel (1,666 views, 20 shares that day). Followers gained the same week.
