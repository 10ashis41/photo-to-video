import pathlib
import subprocess
import tempfile

FONT = pathlib.Path(__file__).resolve().parent.parent / "fonts" / "PlayfairDisplay-Regular.ttf"


def make_endcard(
    title, subtitle, out_path,
    size="1024x1024", duration=2.5, fps=30,
    bg="0x1a1208", color="0xE8C878",
    title_size=72, subtitle_size=44,
):
    """Render a fading title/subtitle card on a flat background — a simple
    closing slate. Uses Playfair Display so it reads as premium/editorial
    instead of the generic sans every AI-video tool defaults to."""
    vf = (
        f"drawtext=fontfile={FONT}:text='{title}':fontcolor={color}:fontsize={title_size}:"
        f"x=(w-text_w)/2:y=(h/2)-90:alpha='if(lt(t,0.4),0,if(lt(t,1.2),(t-0.4)/0.8,1))',"
        f"drawtext=fontfile={FONT}:text='{subtitle}':fontcolor={color}:fontsize={subtitle_size}:"
        f"x=(w-text_w)/2:y=(h/2)+10:alpha='if(lt(t,0.9),0,if(lt(t,1.7),(t-0.9)/0.8,1))'"
    )
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c={bg}:s={size}:d={duration}:r={fps}",
        "-vf", vf, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path),
    ], check=True)
    return out_path


def normalize(in_path, out_path, size="1024x1024"):
    """Rescale a clip to a common resolution so it can be concatenated with
    others that were rendered at a different size."""
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(in_path),
        "-vf", f"scale={size.replace('x', ':')}",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path),
    ], check=True)
    return out_path


def concat(clips, out_path):
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for c in clips:
            f.write(f"file '{pathlib.Path(c).resolve()}'\n")
        listfile = f.name
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", listfile,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path),
    ], check=True)
    return out_path
