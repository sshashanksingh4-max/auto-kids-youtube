from __future__ import annotations

import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1280, 720
FPS = 24
ASSET_DIR = Path(os.getenv("KIDS_ASSET_DIR", "/tmp/kids-assets"))


def font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_character(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, kind: str):
    if kind == "chintu":
        body = "#FFD54F"
        shoe = "#E53935"
        skin = "#C6865B"
        hair = "#222222"
        body2 = "#42A5F5"
    elif kind == "mini":
        body = "#26C6DA"
        shoe = "#FFFFFF"
        skin = "#C6865B"
        hair = "#222222"
        body2 = "#7E57C2"
    elif kind == "golu":
        body = "#8D6E63"
        shoe = "#6D4C41"
        skin = "#FFE0B2"
        hair = "#6D4C41"
        body2 = "#A1887F"
    else:
        body = "#ECEFF1"
        shoe = "#90CAF9"
        skin = "#E3F2FD"
        hair = "#1565C0"
        body2 = "#64B5F6"

    s = scale
    # shadow
    draw.ellipse((x-55*s, y+125*s, x+55*s, y+150*s), fill="#00000030")
    # legs
    draw.rounded_rectangle((x-35*s, y+55*s, x-5*s, y+125*s), radius=12*s, fill=body2)
    draw.rounded_rectangle((x+5*s, y+55*s, x+35*s, y+125*s), radius=12*s, fill=body2)
    # shoes
    draw.ellipse((x-40*s, y+110*s, x, y+140*s), fill=shoe)
    draw.ellipse((x, y+110*s, x+40*s, y+140*s), fill=shoe)
    # body
    draw.rounded_rectangle((x-60*s, y-10*s, x+60*s, y+70*s), radius=24*s, fill=body)
    # arms
    draw.line((x-55*s, y+5*s, x-95*s, y+55*s), fill=body, width=max(4, int(12*s)))
    draw.line((x+55*s, y+5*s, x+95*s, y+55*s), fill=body, width=max(4, int(12*s)))
    # head
    draw.ellipse((x-55*s, y-85*s, x+55*s, y+25*s), fill=skin)
    # hair / robot top
    if kind == "robot":
        draw.rounded_rectangle((x-45*s, y-80*s, x+45*s, y-35*s), radius=15*s, fill=hair)
        draw.line((x, y-100*s, x, y-82*s), fill=hair, width=max(3, int(6*s)))
        draw.ellipse((x-5*s, y-108*s, x+5*s, y-98*s), fill="#FF9800")
    else:
        draw.arc((x-55*s, y-88*s, x+55*s, y-18*s), 180, 360, fill=hair, width=max(4, int(10*s)))
    # eyes
    for dx in (-20, 20):
        draw.ellipse((x+(dx-6)*s, y-45*s, x+(dx+6)*s, y-33*s), fill="#222222")
    draw.arc((x-20*s, y-10*s, x+20*s, y+10*s), 0, 180, fill="#8D4D36", width=max(3, int(5*s)))


def render_scene(path: Path, title: str, subtitle: str, scene_no: int):
    img = Image.new("RGB", (W, H), "#B3E5FC")
    d = ImageDraw.Draw(img)
    # sky
    d.rectangle((0, H*0.62, W, H), fill="#A5D6A7")
    # sun
    d.ellipse((80, 70, 230, 220), fill="#FFD54F")
    # simple trees
    for tx in (180, 510, 930, 1120):
        d.rectangle((tx-12, 300, tx+12, 515), fill="#795548")
        d.ellipse((tx-85, 210, tx+85, 390), fill="#66BB6A")
    # path
    d.polygon([(520, H*0.62), (760, H*0.62), (1000, H), (300, H)], fill="#D7CCC8")

    positions = [
        (360, 510, "chintu"),
        (640, 500, "mini"),
        (850, 525, "golu"),
        (1030, 520, "robot"),
    ]
    for x, y, kind in positions:
        draw_character(d, x, y, 1.05 if kind in {"chintu", "mini"} else 0.75, kind)

    d.rounded_rectangle((45, 35, 1235, 155), radius=28, fill="#FFFFFFD9", outline="#4FC3F7", width=5)
    d.text((75, 55), title, font=font(46), fill="#17324D")
    d.text((75, 108), subtitle, font=font(30), fill="#355C7D")
    d.text((1165, 620), f"{scene_no:02d}", font=font(34), fill="#FFFFFF", stroke_width=3, stroke_fill="#355C7D")
    img.save(path, quality=92)


def run(cmd: list[str]):
    subprocess.run(cmd, check=True)


def synthesize_voice(text: str, out_wav: Path):
    run([
        "espeak",
        "-v", "hi",
        "-s", "145",
        "-p", "52",
        "-a", "165",
        "-w", str(out_wav),
        text,
    ])


def build_video(topic: str, out_mp4: Path):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    scenes = [
        ("चिंटू और दोस्तों की नई खोज", "आज की कहानी शुरू होती है!", "एक सुबह चिंटू और मिन्नी को एक चमकता हुआ सुराग मिला।"),
        ("रहस्यमयी सुराग", "गोलू को कुछ मजेदार दिखाई दिया", "गोलू ने पेड़ों के बीच एक रंगीन निशान देखा और सबको वहाँ बुलाया।"),
        ("टिंकू की मदद", "एक दोस्त ने पहेली समझी", "टिंकू ने सुरागों को जोड़कर अगला रास्ता खोज लिया।"),
        ("बाग़ का रास्ता", "सब साथ-साथ चले", "चारों दोस्त हँसते हुए बगीचे की ओर बढ़े और रास्ते में छोटी-छोटी पहेलियाँ हल करते गए।"),
        ("पहली पहेली", "ध्यान से देखो!", "मिन्नी ने पत्तियों पर बने आकारों को देखकर सही क्रम पहचान लिया।"),
        ("छोटी नदी", "मिलकर पार करेंगे", "चिंटू ने सबको साथ रखा और टिंकू ने सुरक्षित रास्ता बताया।"),
        ("मुस्कुराता पेड़", "क्या यही जगह है?", "एक बड़े आम के पेड़ के नीचे उन्हें रोशनी की एक पतली लकीर दिखाई दी।"),
        ("जादुई रोशनी", "रहस्य और गहरा गया", "रोशनी ने एक छोटे से लकड़ी के डिब्बे तक उनका रास्ता दिखाया।"),
        ("खजाना क्या था?", "सच्चा जादू क्या है?", "डिब्बे के अंदर कोई सोना नहीं था, बल्कि बच्चों के लिए एक किताब थी।"),
        ("नई सीख", "किताब में क्या लिखा था?", "किताब ने बताया कि ज्ञान, दोस्ती और मदद सबसे कीमती खजाने हैं।"),
        ("खुशी बाँटना", "सबने कहानी साझा की", "चारों दोस्तों ने किताब को अपने साथियों के साथ साझा करने का फैसला किया।"),
        ("अंत", "आज की सीख", "मिलकर सीखना, दूसरों की मदद करना और खुशी बाँटना ही सच्चा जादू है।"),
    ]
    narration = " ".join(item[2] for item in scenes)

    scene_files = []
    for idx, (title, subtitle, _) in enumerate(scenes, 1):
        p = ASSET_DIR / f"scene_{idx:02d}.png"
        render_scene(p, title, subtitle, idx)
        scene_files.append(p)

    audio = ASSET_DIR / "narration.wav"
    synthesize_voice(narration, audio)

    concat = ASSET_DIR / "concat.txt"
    with concat.open("w", encoding="utf-8") as f:
        for p in scene_files:
            f.write(f"file '{p.as_posix()}'\n")
            f.write("duration 10\n")
        f.write(f"file '{scene_files[-1].as_posix()}'\n")

    video_only = ASSET_DIR / "video_only.mp4"
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", "scale=1280:720,zoompan=z='min(zoom+0.0008,1.12)':d=240:s=1280x720:fps=24",
        "-t", "120",
        "-r", "24",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        str(video_only),
    ])
    run([
        "ffmpeg", "-y",
        "-i", str(video_only),
        "-i", str(audio),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_mp4),
    ])


if __name__ == "__main__":
    topic = os.getenv("KIDS_TOPIC", "चिंटू और दोस्तों की जादुई किताब")
    output = Path(os.getenv("KIDS_OUTPUT", "/tmp/kids-video.mp4"))
    build_video(topic, output)
    print(output)
