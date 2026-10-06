import base64
import pathlib

from .runpod_client import run_job, wait_for_job


def generate_stills(cfg, prompt, n=3, width=1024, height=1024, out_dir="out/stills", prefix="still"):
    """Generate n still images from a text prompt via the FLUX.2 endpoint."""
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    resp = run_job(
        cfg["flux2_endpoint_id"],
        {"prompt": prompt, "width": width, "height": height, "n": n, "output_format": "png"},
        cfg["runpod_api_key"],
    )
    job_id = resp["id"]
    print(f"[stills] queued job {job_id} (cold start ~30-90s if the worker is asleep)...")

    result = wait_for_job(
        cfg["flux2_endpoint_id"], job_id, cfg["runpod_api_key"],
        on_poll=lambda s, t: print(f"[stills] {s} ({t:.0f}s)"),
    )
    if result["status"] != "COMPLETED":
        raise RuntimeError(f"stills job failed: {result}")

    paths = []
    for i, img in enumerate(result["output"]["images"]):
        p = out / f"{prefix}_{i}.png"
        p.write_bytes(base64.b64decode(img["b64"]))
        paths.append(p)
        print(f"[stills] wrote {p}")
    return paths
