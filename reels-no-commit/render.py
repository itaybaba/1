"""Render a reel page frame-by-frame to MP4.  usage: render.py page.html out.mp4 [fps] [--stills t1,t2,...]"""
import sys, subprocess, http.server, threading, functools, os
from playwright.sync_api import sync_playwright

page_name, out = sys.argv[1], sys.argv[2]
fps = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 30
stills = None
if "--stills" in sys.argv:
    stills = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]

root = os.path.dirname(os.path.abspath(__file__))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
H = type("Q",(http.server.SimpleHTTPRequestHandler,),{"log_message":lambda *a: None}); H = functools.partial(H, directory=root)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/{page_name}"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--force-color-profile=srgb"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.on("console", lambda m: print("console:", m.text))
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.goto(url)
    pg.wait_for_function("window.READY === true", timeout=30000)
    pg.wait_for_timeout(300)
    if stills:
        os.makedirs(out, exist_ok=True)
        for t in stills:
            pg.evaluate(f"seek({t})")
            pg.screenshot(path=f"{out}/t{t:05.2f}.jpg", type="jpeg", quality=80)
    else:
        dur = pg.evaluate("window.DURATION")
        n = int(round(dur * fps))
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                              stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"seek({i / fps})")
            ff.stdin.write(pg.screenshot(type="png"))
        ff.stdin.close(); ff.wait()
        print("wrote", out, n, "frames")
    b.close()
srv.shutdown()
