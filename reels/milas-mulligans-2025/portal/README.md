# Mila's Mulligans · portal approvals pages

Two pages for the R0BATO client portal (r0batomediaprojs-d5fc52.netlify.app), in the portal's dark design and laid out like the Build & Burn approvals page:

- `clients/<slug>/approvals/index.html`: "What's posting" calendar (proposed dates from `../review-page/schedule.json`) and a project card per project.
- `clients/<slug>/approvals/throwback-reels/index.html`: the three approved reels (hot dog v19, Mayo or sand? v4, Guess the 50-50 v3) with their captions, copy buttons, a download link and a review form (name, decision, notes with video timestamps). The form is a Netlify Form named `mila-reel-review` (forms are enabled on the site), so reviews land in Netlify's form submissions.

Build:

```
python gen_portal.py ../review-page <dir with the three *_review.mp4 files> <out>/drafts/<slug>/ <slug>
```

The review videos are the 1080x1920, about 19 MB copies on the claude.ai review page (https://claude.ai/artifact/LYgrb7NjKyp3B1UHrquSFF, "Save video" under each reel). Videos stay out of git.

Publishing follows the robato-client-portal skill and `claude/Client-Portal-Source-and-Deploy.md` on the SSD: use Mila's existing slug from `portal-source/clients/`, save the draft to `client-portal/drafts/<slug>/`, log it in `PORTAL-LOG.txt`, then the deploy rule (copy the live release, add only these files, draft deploy first, check every file and link, publish, copy back into `portal-source/`, log in `ADOPT-LOG.txt`). This could not run from the 16 Oct cloud session: the SSD and the portal source are on Rob's computer, and the session's network blocks the portal site.
