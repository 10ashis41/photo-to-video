import argparse
import pathlib

from .animate import animate_image
from .config import load_config
from .stills import generate_stills
from .stitch import concat, make_endcard, normalize


def main():
    p = argparse.ArgumentParser(prog="photo-to-video")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stills", help="Generate still images with FLUX.2")
    s.add_argument("prompt")
    s.add_argument("-n", type=int, default=3)
    s.add_argument("--size", default="1024x1024")
    s.add_argument("-o", "--out-dir", default="out/stills")

    a = sub.add_parser("animate", help="Animate a still into a short video with Wan2.2")
    a.add_argument("image")
    a.add_argument("prompt")
    a.add_argument("--negative", default="blurry, low quality, distorted, text, watermark")
    a.add_argument("--length", type=int, default=81, help="81 ~= 5s clip, 40 ~= 2.5s clip")
    a.add_argument("--size", default="1024x1024")
    a.add_argument("--seed", type=int, default=None)
    a.add_argument("-o", "--out")

    st = sub.add_parser("stitch", help="Scale clips to a common size and concatenate them")
    st.add_argument("clips", nargs="+")
    st.add_argument("--size", default="1024x1024")
    st.add_argument("-o", "--out", default="out/final.mp4")

    e = sub.add_parser("endcard", help="Render a title/subtitle end card")
    e.add_argument("title")
    e.add_argument("subtitle")
    e.add_argument("-o", "--out", default="out/endcard.mp4")
    e.add_argument("--duration", type=float, default=2.5)
    e.add_argument("--size", default="1024x1024")

    args = p.parse_args()

    if args.cmd == "stills":
        cfg = load_config()
        w, h = map(int, args.size.split("x"))
        generate_stills(cfg, args.prompt, n=args.n, width=w, height=h, out_dir=args.out_dir)

    elif args.cmd == "animate":
        cfg = load_config()
        w, h = map(int, args.size.split("x"))
        animate_image(
            cfg, args.image, args.prompt, negative_prompt=args.negative,
            width=w, height=h, length=args.length, seed=args.seed, out_path=args.out,
        )

    elif args.cmd == "stitch":
        out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        norm_dir = out.parent / "_normalized"
        norm_dir.mkdir(exist_ok=True)
        normed = []
        for i, c in enumerate(args.clips):
            np_ = norm_dir / f"clip_{i}.mp4"
            normalize(c, np_, size=args.size)
            normed.append(np_)
        concat(normed, out)
        print(f"[stitch] wrote {out}")

    elif args.cmd == "endcard":
        make_endcard(args.title, args.subtitle, args.out, size=args.size, duration=args.duration)
        print(f"[endcard] wrote {args.out}")


if __name__ == "__main__":
    main()
