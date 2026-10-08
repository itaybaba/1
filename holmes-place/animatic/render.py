"""Render the ONE animatic (16:9, 25fps) from the storyboard stills.

Each moment: cream card (1s) -> action frame (3s) with a slow push-in.
Then a 6s closer: last frame darkens, logo and slogan fade in.
Frames are piped straight into ffmpeg.
"""
import pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1280, 720, 25
BASE = 1.25  # source is prepared at 1.25x so the push-in never upsamples past it
CREAM = (247, 244, 239)
FONT = ImageFont.truetype(str(ROOT / "animatic/outfit-latin-400-normal.woff"), 82)
SLOGAN_FONT = ImageFont.truetype(str(ROOT / "animatic/outfit-latin-400-normal.woff"), 52)

# word, action image
MOMENTS = [
    ("one step",    "frames/step.jpg"),
    ("one effort",  "frames/effort.jpg"),
    ("one more",    "frames/more.jpg"),
    ("one rhythm",  "frames/rhythm.jpg"),
    ("one stretch", "frames/stretch.jpg"),
    ("one breath",  "frames/breath.jpg"),
    ("one lap",     "frames/splash.jpg"),
    ("one drop",    "frames/drop.jpg"),
    ("one pause",   "frames/pause.jpg"),
    ("one touch",   "frames/touch.jpg"),
    ("one smile",   "frames/smile.jpg"),
]
CARD, SHOT, CLOSER = 25, 75, 150

rng = np.random.default_rng(7)


def prepare(path, focus=.5):
    """Cover-crop to 16:9 at BASE size, then sharpen the upscale a little."""
    im = Image.open(ROOT / path).convert("RGB")
    tw, th = int(W * BASE), int(H * BASE)
    scale = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    x = (im.width - tw) // 2
    y = round((im.height - th) * focus)
    im = im.crop((x, y, x + tw, y + th))
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))


def ease(t):
    return t * t * (3 - 2 * t)


def kenburns(src, t, zoom=0.08, drift=(0, 0)):
    """Slow push-in: window shrinks from full BASE frame by `zoom`, with a small drift."""
    z = 1 + zoom * ease(t)
    ww, wh = src.width / z, src.height / z
    cx = src.width / 2 + drift[0] * ease(t) * (src.width - ww) / 2
    cy = src.height / 2 + drift[1] * ease(t) * (src.height - wh) / 2
    box = (cx - ww / 2, cy - wh / 2, cx + ww / 2, cy + wh / 2)
    return src.resize((W, H), Image.BICUBIC, box=box)


def card(word):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.text((W / 2, H / 2), word, font=FONT, fill=(17, 17, 17), anchor="mm")
    return im


def grain(im, amount=3.5):
    a = np.asarray(im, dtype=np.int16)
    n = rng.normal(0, amount, (H, W, 1)).astype(np.int16)
    return np.clip(a + n, 0, 255).astype(np.uint8)


def frames():
    drifts = [(-.4, .2), (.4, -.2), (0, .3), (-.3, -.2), (.3, .2), (0, -.3)]
    for i, (word, act) in enumerate(MOMENTS):
        c = np.asarray(card(word))
        for _ in range(CARD):
            yield c
        src = prepare(act)
        for f in range(SHOT):
            yield grain(kenburns(src, f / (SHOT - 1), .10, drifts[i % 6]))

    # Closer: last action frame darkens, logo then slogan fade in, fade to black.
    bg_src = prepare(MOMENTS[-1][1])
    logo = Image.open(ROOT / "frames/logo.jpg").convert("RGB")
    lw = 230
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    lx, ly = (W - lw) // 2, H // 2 - logo.height // 2 - 40
    for f in range(CLOSER):
        t = f / FPS
        bg = kenburns(bg_src, min(1, f / (CLOSER - 1)), .05)
        dark = 1 - 0.62 * ease(min(1, t / 1.0))
        frame = Image.eval(bg, lambda v, k=dark: int(v * k))
        a_logo = ease(min(1, max(0, (t - 0.9) / 0.8)))
        if a_logo:
            region = frame.crop((lx, ly, lx + lw, ly + logo.height))
            frame.paste(Image.blend(region, logo, a_logo), (lx, ly))
        a_text = ease(min(1, max(0, (t - 1.7) / 0.9)))
        if a_text:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((W / 2, ly + logo.height + 62), "One life. Live it well.",
                                       font=SLOGAN_FONT, fill=(255, 255, 255, int(255 * a_text)), anchor="mm")
            frame = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
        fade = 1 - ease(min(1, max(0, (t - 5.4) / 0.6)))
        if fade < 1:
            frame = Image.eval(frame, lambda v, k=fade: int(v * k))
        yield grain(frame, 3.0)


def main(out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
           "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for fr in frames():
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
        n += 1
    p.stdin.close()
    sys.exit(p.wait() or print(f"{n} frames -> {out}"))


if __name__ == "__main__":
    main(ROOT / "animatic/one-animatic-16x9.mp4")
