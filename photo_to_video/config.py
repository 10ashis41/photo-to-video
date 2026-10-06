import json
import os
import pathlib

CONFIG_PATH = pathlib.Path(__file__).resolve().parent.parent / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"{CONFIG_PATH} not found. Copy config.example.json to config.json and fill in "
            "your RunPod endpoint IDs (see README \"One-time setup\")."
        )
    cfg = json.loads(CONFIG_PATH.read_text())
    api_key = os.environ.get("RUNPOD_API_KEY") or cfg.get("runpod_api_key")
    if not api_key:
        raise RuntimeError("Set RUNPOD_API_KEY env var or put runpod_api_key in config.json")
    cfg["runpod_api_key"] = api_key
    return cfg
