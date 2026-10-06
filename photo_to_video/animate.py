import base64
import mimetypes
import pathlib

from .runpod_client import run_job, wait_for_job

DEFAULT_NEGATIVE = "blurry, low quality, distorted, text, watermark"


def animate_image(
    cfg,
    image_path,
    motion_prompt,
    negative_prompt=DEFAULT_NEGATIVE,
    width=1024,
    height=1024,
    length=81,       # 81 ~= 5s clip, 40 ~= 2.5s clip (model renders ~2x the input frame count)
    steps=10,
    cfg_scale=2.0,
    seed=None,
    out_path=None,
):
    """Animate a still image into a short video via the Wan2.2 endpoint.

    Sends the image as base64 directly in the job payload — no need to host
    it anywhere first, unlike driving this through a chat tool with a token
    budget. A real script can just read the bytes and post them.
    """
    image_path = pathlib.Path(image_path)
    mime = mimetypes.guess_type(str(image_path))[0] or "image/png"
    b64 = base64.b64encode(image_path.read_bytes()).decode()

    payload = {
        "prompt": motion_prompt,
        "negative_prompt": negative_prompt,
        "image_base64": f"data:{mime};base64,{b64}",
        "width": width,
        "height": height,
        "length": length,
        "steps": steps,
        "cfg": cfg_scale,
    }
    if seed is not None:
        payload["seed"] = seed

    resp = run_job(cfg["wan22_endpoint_id"], payload, cfg["runpod_api_key"])
    job_id = resp["id"]
    print(f"[animate] queued job {job_id} for {image_path.name} (cold start can take minutes)...")

    result = wait_for_job(
        cfg["wan22_endpoint_id"], job_id, cfg["runpod_api_key"], timeout=1800,
        on_poll=lambda s, t: print(f"[animate] {s} ({t:.0f}s)"),
    )
    if result["status"] != "COMPLETED":
        raise RuntimeError(f"animate job failed: {result}")

    out_path = pathlib.Path(out_path or (str(image_path.with_suffix("")) + "_video.mp4"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(result["output"]["video"]))
    print(f"[animate] wrote {out_path}")
    return out_path
