# Photo to Video

A small pipeline that turns a text prompt into a still image, animates that
still into a short video, and stitches multiple clips together with a
title-card ending — all on cheap, scale-to-zero GPU rendering instead of a
paid per-second video API.

Built from two open-source RunPod Hub workers, chained together:

- **Stills** — [`gevondyanerik/runpod-worker-flux2`](https://github.com/gevondyanerik/runpod-worker-flux2)
  (FLUX.2 klein, text-to-image)
- **Animation** — [`wlsdml1114/generate_video`](https://github.com/wlsdml1114/generate_video)
  ("Wan2.2 with LoRA", image-to-video)

This repo doesn't vendor or fork either of those — it deploys them as-is from
the RunPod Hub and just owns the orchestration: generate → pick a still →
animate → stitch → add text. That's the part that was actually custom.

## Cost

Both endpoints are serverless and scale to zero — you only pay while a job is
actually rendering, not while idle.

- Stills (FLUX.2, 4-step distilled): a few cents per batch of 3
- Animation (Wan2.2, RTX 4090 pool, ~$1.10/hr serverless rate): roughly
  $0.05–0.15 per clip depending on length/resolution
- Leaving the endpoints deployed costs a small idle **disk** fee even at zero
  GPU workers (~$0.01–0.015/hr combined for both) — delete them when you're
  done for a stretch (see Teardown below)

## One-time setup

1. Install ffmpeg (`apt install ffmpeg` or equivalent) — the only non-Python
   dependency. No pip packages are required; everything else is stdlib.
2. Get a RunPod API key: https://console.runpod.io/user/settings
3. Deploy the two Hub workers as serverless endpoints, scale-to-zero. Either:
   - Ask Claude Code with the RunPod MCP connected: *"deploy
     gevondyanerik/runpod-worker-flux2 and wlsdml1114/generate_video as
     scale-to-zero serverless endpoints"*, or
   - Deploy manually from https://console.runpod.io/hub by searching each
     repo name and clicking Deploy (workers min: 0).
4. Copy `config.example.json` → `config.json` and fill in the two endpoint
   IDs. Either put your API key in `config.json` too, or export
   `RUNPOD_API_KEY` instead (preferred — keeps the key out of the file).

## Usage

```bash
export RUNPOD_API_KEY=...   # if not already in config.json

# 1. Generate a few still options
python -m photo_to_video stills "extreme macro close-up of raw honeycomb, honey dripping, golden light" -n 3

# 2. Pick one, animate it (length 81 ~= 5s, 40 ~= 2.5s)
python -m photo_to_video animate out/stills/still_0.png \
  "slow cinematic side drift, honey dripping, warm golden light shimmering" \
  --length 81 -o out/clips/shot1.mp4

# 3. Repeat animate for as many shots as you want, then stitch them together
python -m photo_to_video stitch out/clips/shot1.mp4 out/clips/shot2.mp4 out/clips/shot3.mp4 -o out/sequence.mp4

# 4. Make a title card and tack it on the end
python -m photo_to_video endcard "Artisanal Honey" "from the Austrian Alps" -o out/clips/endcard.mp4
python -m photo_to_video stitch out/sequence.mp4 out/clips/endcard.mp4 -o out/final.mp4
```

Cold starts: the first job after a period of idleness can take 1–5+ minutes
(the worker has to pull the image and load model weights) — this is normal
and the script polls through it with status updates printed to the console.

## Teardown

Delete the endpoints when you're done for a while, to stop the small idle
disk charge:

```bash
# via Claude Code + RunPod MCP:
# "delete the flux2 and wan22 photo-to-video endpoints"

# or manually in the console: https://console.runpod.io/serverless
```

Redeploying later (step 3 above) takes under a minute.
