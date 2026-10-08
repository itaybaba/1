"""Assemble the ONE film from real footage.

Put one clip per moment in edit/clips/ named 01.mp4 ... 11.mp4 (any ffmpeg-readable
format). Optional start offsets (seconds) go in edit/clips/offsets.txt as "07 2.5" lines;
by default the middle 3 seconds of each clip are used.

Builds: card (1s) + clip (3s) per moment, then a 6s closer on the last clip's final
frame. Writes 16:9 and 9:16 masters to edit/out/.
"""
import pathlib, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = ROOT / "animatic/outfit-latin-400-normal.woff"
LOGO = ROOT / "frames/logo.jpg"
FPS, CARD, SHOT, CLOSER = 25, 1.0, 3.0, 6.0
WORDS = ["one step", "one effort", "one more", "one rhythm", "one stretch", "one breath",
         "one lap", "one drop", "one pause", "one touch", "one smile"]
FORMATS = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
# Shared look: slightly muted, warm, soft contrast, fine grain.
GRADE = "eq=contrast=1.04:saturation=0.88:gamma=0.98,colorbalance=rs=.03:gs=.01:bs=-.03:rm=.02:bm=-.02,noise=alls=6:allf=t"


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def encode_args(w, h):
    return ["-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-s", f"{w}x{h}", "-an"]


def card_png(word, w, h, path):
    im = Image.new("RGB", (w, h), (247, 244, 239))
    size = round(min(w, h) * 0.115)
    ImageDraw.Draw(im).text((w / 2, h / 2), word, font=ImageFont.truetype(str(FONT), size),
                            fill=(17, 17, 17), anchor="mm")
    im.save(path)


def closer_frames(still, w, h, outdir):
    """Darken the last frame, fade in logo then slogan, fade to black."""
    bg = Image.open(still).convert("RGB")
    logo = Image.open(LOGO).convert("RGB")
    lw = round(min(w, h) * 0.32)
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    lx, ly = (w - lw) // 2, h // 2 - logo.height // 2 - round(h * .05)
    font = ImageFont.truetype(str(FONT), round(min(w, h) * 0.072))
    ease = lambda t: max(0, min(1, t)) ** 2 * (3 - 2 * max(0, min(1, t)))
    for f in range(int(CLOSER * FPS)):
        t = f / FPS
        frame = Image.eval(bg, lambda v, k=1 - .62 * ease(t): int(v * k))
        if (a := ease((t - .9) / .8)):
            frame.paste(Image.blend(frame.crop((lx, ly, lx + lw, ly + logo.height)), logo, a), (lx, ly))
        if (a := ease((t - 1.7) / .9)):
            layer = Image.new("RGBA", (w, h))
            ImageDraw.Draw(layer).text((w / 2, ly + logo.height + round(h * .085)), "One life. Live it well.",
                                       font=font, fill=(255, 255, 255, int(255 * a)), anchor="mm")
            frame = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
        if (k := 1 - ease((t - 5.4) / .6)) < 1:
            frame = Image.eval(frame, lambda v, k=k: int(v * k))
        frame.save(outdir / f"c{f:04d}.png")


def build(fmt, clips, offsets):
    w, h = FORMATS[fmt]
    work = HERE / "work" / fmt
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    parts = []
    for i, (word, clip) in enumerate(zip(WORDS, clips), 1):
        card_png(word, w, h, work / f"card{i:02d}.png")
        run("-loop", "1", "-t", str(CARD), "-i", str(work / f"card{i:02d}.png"), *encode_args(w, h),
            str(work / f"{i:02d}a.mp4"))
        start = offsets.get(i, max(0, (duration(clip) - SHOT) / 2))
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={FPS},{GRADE}"
        run("-ss", str(start), "-t", str(SHOT), "-i", str(clip), "-vf", vf, *encode_args(w, h),
            str(work / f"{i:02d}b.mp4"))
        parts += [work / f"{i:02d}a.mp4", work / f"{i:02d}b.mp4"]
    run("-sseof", "-0.1", "-i", str(parts[-1]), "-frames:v", "1", "-update", "1", str(work / "last.png"))
    closer_frames(work / "last.png", w, h, work)
    run("-framerate", str(FPS), "-i", str(work / "c%04d.png"), *encode_args(w, h), str(work / "12.mp4"))
    parts.append(work / "12.mp4")
    (work / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    out = HERE / "out" / f"one-{fmt}.mp4"
    out.parent.mkdir(exist_ok=True)
    music = HERE / "clips/music.mp3"
    audio = (["-i", str(music), "-af", f"afade=t=out:st={len(WORDS) * 4 + 4.5}:d=1.5", "-c:a", "aac", "-b:a", "192k", "-shortest"]
             if music.exists() else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-c:a", "aac", "-shortest"])
    run("-f", "concat", "-safe", "0", "-i", str(work / "list.txt"), *audio, "-c:v", "copy",
        "-movflags", "+faststart", str(out))
    print(out, round(duration(out), 2), "s")


def main():
    clips_dir = HERE / "clips"
    clips = []
    for i in range(1, len(WORDS) + 1):
        found = sorted(p for p in clips_dir.glob(f"{i:02d}.*") if p.suffix not in (".txt", ".mp3"))
        if not found:
            sys.exit(f"missing clip {i:02d} in {clips_dir}")
        clips.append(found[0])
    offsets = {}
    if (clips_dir / "offsets.txt").exists():
        for line in (clips_dir / "offsets.txt").read_text().split("\n"):
            if line.strip():
                k, v = line.split()
                offsets[int(k)] = float(v)
    for fmt in sys.argv[1:] or FORMATS:
        build(fmt, clips, offsets)


if __name__ == "__main__":
    main()
