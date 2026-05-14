#!/usr/bin/env python3
"""A3: render original page at 3508px wide, scale to A3."""
import subprocess, time
from datetime import datetime

A3_W, A3_H = 3508, 4961

server = subprocess.Popen(
    ["python3", "-m", "http.server", "8784"],
    cwd="/Users/daniel/fund-editor", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(1)

try:
    from playwright.sync_api import sync_playwright
    from PIL import Image

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": A3_W, "height": 900})
        page.goto("http://localhost:8784/index.html", wait_until="networkidle")
        page.evaluate("document.getElementById('gate').style.display='none'")
        page.evaluate("document.getElementById('main').style.display='block'")
        # Make page full width, minimal padding
        page.evaluate("""() => {
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            document.body.style.background = '#fff';
            var pg = document.querySelector('.page');
            pg.style.maxWidth = 'none';
            pg.style.margin = '0';
            pg.style.padding = '30px 40px';
        }""")

        ch = page.evaluate("document.body.scrollHeight")
        print(f"Content height: {ch}")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        tmp = f"/tmp/fund-wide-{ts}.png"
        page.screenshot(path=tmp, full_page=True, type="png")
        browser.close()

    img = Image.open(tmp)
    iw, ih = img.size
    print(f"Screenshot: {iw} x {ih}")

    # Scale to A3
    if ih < A3_H:
        scale = A3_H / ih
        new_w = int(iw * scale)
        resized = img.resize((new_w, A3_H), Image.LANCZOS)
        canvas = Image.new("RGB", (A3_W, A3_H), (255, 255, 255))
        x = (A3_W - new_w) // 2
        canvas.paste(resized, (x, 0))
    else:
        canvas = img.crop((0, 0, A3_W, A3_H))

    out = f"/Users/daniel/Desktop/五级基金体系架构图-A3-{ts}.png"
    canvas.save(out, "PNG")
    print(f"Final: {canvas.size[0]} x {canvas.size[1]}")
    print(f"Saved: {out}")

finally:
    server.terminate()
    server.wait()
