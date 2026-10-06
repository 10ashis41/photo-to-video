import json
import time
import urllib.request

API_BASE = "https://api.runpod.ai/v2"


def _headers(api_key):
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def run_job(endpoint_id, input_payload, api_key):
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint_id}/run",
        data=json.dumps({"input": input_payload}).encode(),
        headers=_headers(api_key),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def job_status(endpoint_id, job_id, api_key):
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint_id}/status/{job_id}",
        headers=_headers(api_key),
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def wait_for_job(endpoint_id, job_id, api_key, poll_every=10, timeout=1200, on_poll=None):
    """Poll until the job reaches a terminal status. Cold starts on a heavy
    video-model image can take several minutes — timeout defaults generously."""
    start = time.time()
    while True:
        data = job_status(endpoint_id, job_id, api_key)
        status = data.get("status")
        if on_poll:
            on_poll(status, time.time() - start)
        if status in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            return data
        if time.time() - start > timeout:
            raise TimeoutError(
                f"job {job_id} did not finish within {timeout}s (last status={status})"
            )
        time.sleep(poll_every)
