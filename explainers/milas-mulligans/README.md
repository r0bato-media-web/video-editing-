# Mila's Mulligans: "Where your mulligan goes"

Internal test. Not approved for posting.

Two explainer styles, each in 9:16 (1080x1920) and 16:9 (1920x1080), 20 s at 30 fps, silent:

- `Iso-*`: four isometric blocks rise in order, and a dot travels to the next block.
- `WB-*`: one line drawing per scene, drawn stroke by stroke.
- `End-*`: a 4.5 s end card for footage reels (the cap draws on, then the scholarship line, "We play for Arian." and the link). The 2025 throwback reel in `../../reels/milas-mulligans-2025` uses it.

The brief, with its Avoid and Done-means lines, is in [`../../briefs/milas-mulligans.md`](../../briefs/milas-mulligans.md).

## Render

```
npm install
npm run render:all
```

In a container without Remotion's own Chrome download, add
`--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.

`out/` is git-ignored. Finished files get R0BATO metadata and a `_SOCIAL_COPY.txt` sidecar before they leave the job folder.

## Open items before this can go to the client

- Colours are sampled from the approved "one week out" flyer, because the client logo folder on Drive is empty. Swap in logo-file colours in `src/brand.ts` when available.
- Fonts are stand-ins: Caladea for the flyer serif, Inter for the sans.
- Remotion's license terms for company use are unchecked. Check remotion.dev/license before client delivery.
- Confirm the family is comfortable with "We play for Arian." on a memorial piece.
