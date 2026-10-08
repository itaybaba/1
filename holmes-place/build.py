"""Inline frames/*.jpg into a single self-contained storyboard.html."""
import base64, pathlib, re

here = pathlib.Path(__file__).parent
src = (here / "storyboard.src.html").read_text(encoding="utf-8")

def inline(m):
    data = base64.b64encode((here / m.group(1)).read_bytes()).decode()
    return f'src="data:image/jpeg;base64,{data}"'

(here / "storyboard.html").write_text(re.sub(r'src="(frames/[^"]+\.jpg)"', inline, src), encoding="utf-8")
