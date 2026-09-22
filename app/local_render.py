"""Free-first, frame-by-frame 2D cartoon renderer.

This is deliberately procedural: each scene has a distinct action and the
characters are redrawn every frame with walk cycles, gestures, expressions,
gaze, props and a moving camera. It is a 2D rigged cartoon, not 3D or AI video.
"""
from __future__ import annotations

import math
import os
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
ASSET_DIR = Path(os.getenv("KIDS_ASSET_DIR", "/tmp/kids-assets"))
FONT_PATHS = (
    "C:/Windows/Fonts/Nirmala.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)

PALETTE = {
    "ink": "#263238", "skin": "#C98762", "hair": "#29252B",
    "yellow": "#FFD34E", "blue": "#438BD4", "red": "#E84A4A",
    "teal": "#35C4C6", "purple": "#8354B8", "brown": "#9B6747",
    "cream": "#FFE0B4", "green": "#4A9C62", "white": "#FFFDF7",
}

# Each beat is a short, playable scene. Actions are interpreted by the rigs
# below; the narration is intentionally in natural, short Hindi sentences.
SCENES = [
    {"title":"चमकता हुआ बीज", "line":"अरे, यह चमकता बीज कहाँ से आया?", "action":"discover", "place":"garden", "speaker":"chintu"},
    {"title":"मिन्नी की तरकीब", "line":"इसे मिट्टी में लगाते हैं। हम रोज़ पानी देंगे।", "action":"plant", "place":"garden", "speaker":"mini"},
    {"title":"गोलू की मदद", "line":"मेरी छोटी बोतल से पानी लो!", "action":"water", "place":"garden", "speaker":"golu"},
    {"title":"टिंकू देखता है", "line":"पौधे को धूप भी चाहिए।", "action":"point", "place":"garden", "speaker":"tinku"},
    {"title":"नन्हा पौधा", "line":"मिनी, इस गमले को धूप में ले चलें।", "action":"carry", "place":"garden", "speaker":"chintu"},
    {"title":"खुशी की कली", "line":"वाह! हमारी कली खिल गई!", "action":"bloom", "place":"garden", "speaker":"mini"},
    {"title":"बीज बाँटें", "line":"दोस्तों ने और बीज लगाए। बगीचा रंगों से भर गया।", "action":"celebrate", "place":"garden", "speaker":"narrator"},
    {"title":"आज की सीख", "line":"प्यार और देखभाल से छोटी चीज़ भी बड़ा बदलाव ला सकती है।", "action":"wave", "place":"garden", "speaker":"narrator"},
]

def font(size: int):
    for path in FONT_PATHS:
        if Path(path).exists():
            # RAQM supplies Indic shaping where Pillow was built with it.
            try:
                return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
            except (AttributeError, ValueError):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(tuple(int(v) for v in box), radius=int(radius), fill=fill, outline=outline, width=width)

def background(t: float, scene_index: int, camera: float) -> Image.Image:
    """Layered garden with independently drifting clouds, hills and foliage."""
    img = Image.new("RGB", (W, H), "#8BD5F0")
    d = ImageDraw.Draw(img)
    # Parallax clouds drift at different speeds.
    for i, (cx, cy, r) in enumerate(((130,115,35),(570,145,27),(1040,92,43))):
        x = (cx + t*(9+i*3) + camera*(.08+i*.02)) % (W+180) - 90
        d.ellipse((x-r,cy-r*.45,x+r,cy+r*.5),fill="#FFFFFF")
        d.ellipse((x-r*.55,cy-r,x+r*.55,cy+r*.35),fill="#FFFFFF")
        d.ellipse((x,cy-r*.55,x+r,cy+r*.5),fill="#FFFFFF")
    d.ellipse((1000,58,1100,158), fill="#FFE16A")
    # Distant hills slide gently behind the foreground.
    d.ellipse((-180-camera*.17,290,580-camera*.17,610), fill="#8ACF8A")
    d.ellipse((420-camera*.12,270,1240-camera*.12,620), fill="#77C47E")
    d.rectangle((0,440,W,H), fill="#72BE68")
    # Garden rows and path establish depth; foreground moves faster.
    d.polygon([(475,440),(745,440),(1040,H),(245,H)], fill="#D8BB88")
    for i in range(14):
        x=(i*111 - t*22 - camera*.32)%(W+90)-40
        y=464+(i%3)*56
        d.ellipse((x,y,x+18,y+11), fill="#4F9E57")
    for i in range(10):
        x=(i*151 - t*9 - camera*.12)%(W+100)-50
        d.rectangle((x,345,x+17,480), fill="#80573B")
        d.ellipse((x-58,277,x+77,397), fill=("#64B96B" if i%2 else "#6FC274"))
    # Animated butterflies / flower specks
    for i in range(5):
        x=(i*287 + math.sin(t*2+i)*28 - t*13)%(W+40)
        y=280+math.sin(t*2.5+i)*24
        d.ellipse((x,y,x+10,y+7),fill=("#FF78AB" if i%2 else "#FFE36E"))
        d.ellipse((x+9,y,x+19,y+7),fill=("#FF78AB" if i%2 else "#FFE36E"))
    return img

def draw_human(d: ImageDraw.ImageDraw, x: float, floor: float, kind: str,
               t: float, emotion: str, speaking: bool, facing: int = 1,
               walk: float = 0.0, gesture: float = 0.0, scale: float = 1.0):
    """A small articulated cartoon rig with limb swing and changing face."""
    s=scale; bob=math.sin(t*8)*3*s if walk else abs(math.sin(t*5))*2*s
    x=float(x); y=floor-bob
    if kind=="chintu": shirt,shorts,shoe,hair,skin="#FFD34E","#438BD4","#E84A4A",PALETTE["hair"],PALETTE["skin"]
    else: shirt,shorts,shoe,hair,skin="#35C4C6","#8354B8","#FFFDF7",PALETTE["hair"],PALETTE["skin"]
    # shadow and legs: alternating stride is visible while traveling.
    d.ellipse((x-43*s,floor-7*s,x+43*s,floor+7*s),fill="#4E8A4E")
    phase=math.sin(t*9)*18*s if walk else math.sin(t*3)*3*s
    hip_y=y-52*s
    for side in (-1,1):
        hip=x+side*13*s; knee_y=hip_y+31*s+abs(phase)*.22
        foot_dx=phase*side
        d.line((hip,hip_y,knee_y*0+hip+foot_dx*.35,knee_y),fill=shorts,width=max(7,int(13*s)))
        d.line((hip+foot_dx*.35,knee_y,hip+foot_dx,y-5*s),fill=shorts,width=max(7,int(13*s)))
        rounded(d,(hip+foot_dx-13*s,y-15*s,hip+foot_dx+13*s,y+1*s),7*s,shoe)
    # torso and hoodie/top
    rounded(d,(x-34*s,y-112*s,x+34*s,y-42*s),19*s,shirt)
    if kind=="chintu":
        d.line((x,y-105*s,x,y-56*s),fill="#F6B82E",width=max(2,int(3*s)))
        d.ellipse((x-5*s,y-91*s,x+5*s,y-86*s),fill="#F6B82E")
    else:
        rounded(d,(x-8*s,y-104*s,x+8*s,y-69*s),5*s,"#F7E7FF")
    # shoulders, elbows and hands; active arm reaches/points toward the prop.
    swing=math.sin(t*9)*19*s if walk else math.sin(t*4)*4*s
    active=math.sin(gesture*math.pi/2) if gesture else 0
    for side in (-1,1):
        shoulder=(x+side*29*s,y-99*s)
        if side==facing:
            elbow=(x+side*(48+(12 if walk else 18)*active)*s,y-79*s-16*active*s)
            reach=65 if walk else 52+38*active
            hand=(x+side*reach*s,y-42*s-(18*active*s if not walk else 0))
        else:
            elbow=(x+side*43*s,y-78*s+swing*.4)
            hand=(x+side*50*s,y-55*s+swing)
        d.line((*shoulder,*elbow),fill=shirt,width=max(8,int(15*s)))
        d.line((*elbow,*hand),fill=skin,width=max(7,int(12*s)))
        d.ellipse((hand[0]-7*s,hand[1]-7*s,hand[0]+7*s,hand[1]+7*s),fill=skin)
    # head tilt is a subtle but continuous secondary motion.
    tilt=math.sin(t*2.2)*2*s
    hx=x+tilt; hy=y-145*s
    d.ellipse((hx-37*s,hy-42*s,hx+37*s,hy+38*s),fill=skin)
    # hair silhouette and Mini's signature twin ponytails.
    d.pieslice((hx-39*s,hy-47*s,hx+39*s,hy+30*s),180,360,fill=hair)
    d.ellipse((hx-33*s,hy-43*s,hx+33*s,hy-2*s),fill=hair)
    if kind=="mini":
        for side,col in ((-1,"#FF73A8"),(1,"#FFD34E")):
            px=hx+side*34*s
            d.ellipse((px-6*s,hy-16*s,px+6*s,hy-4*s),fill=col)
            d.ellipse((px-8*s,hy-4*s,px+8*s,hy+18*s),fill=hair)
            d.ellipse((hx+side*22*s-5*s,hy-30*s,hx+side*22*s+4*s,hy-21*s),fill=col)
    # gaze shifts to the current object/speaker.
    eye_y=hy-7*s; gaze=facing*2*s
    for side in (-1,1):
        ex=hx+side*13*s
        d.ellipse((ex-5*s,eye_y-6*s,ex+5*s,eye_y+6*s),fill="white")
        d.ellipse((ex-2*s+gaze,eye_y-3*s,ex+3*s+gaze,eye_y+4*s),fill=PALETTE["ink"])
        brow_y=eye_y-12*s + (3*s if emotion=="surprised" else 0)
        d.line((ex-5*s,brow_y,ex+4*s,brow_y-2*s),fill=hair,width=max(2,int(3*s)))
    if speaking and int(t*7)%2:
        d.ellipse((hx-7*s,hy+12*s,hx+8*s,hy+25*s),fill="#743B3A")
    elif emotion=="surprised":
        d.ellipse((hx-5*s,hy+12*s,hx+6*s,hy+22*s),fill="#743B3A")
    elif emotion=="thinking":
        d.arc((hx-10*s,hy+12*s,hx+8*s,hy+26*s),190,340,fill="#743B3A",width=max(2,int(3*s)))
    else:
        d.arc((hx-13*s,hy+8*s,hx+13*s,hy+28*s),5,175,fill="#743B3A",width=max(2,int(3*s)))

def draw_squirrel(d,x,floor,t,action,gesture=0,speaking=False,scale=1.0):
    s=.74*scale; bob=abs(math.sin(t*6))*6*s; y=floor-bob
    d.ellipse((x-36,y-7,x+36,y+5),fill="#4E8A4E")
    # curled tail swishes, with a cream inner patch
    d.ellipse((x+12,y-91,x+79,y-24),fill="#9B6747")
    d.ellipse((x+28,y-78,x+65,y-40),fill="#FFE0B4")
    d.ellipse((x-25,y-77,x+31,y-9),fill="#9B6747")
    d.ellipse((x-17,y-56,x+25,y-5),fill="#FFE0B4")
    d.ellipse((x-20,y-111,x+23,y-66),fill="#B77B56")
    d.ellipse((x-23,y-117,x-4,y-96),fill="#9B6747"); d.ellipse((x+5,y-117,x+25,y-96),fill="#9B6747")
    for ex in (x-9,x+9): d.ellipse((ex-3,y-101,ex+3,y-93),fill="#263238")
    d.ellipse((x-3,y-89,x+4,y-83),fill="#4A2925")
    if speaking and int(t*8)%3:
        d.ellipse((x-4,y-88,x+5,y-80),fill="#743B3A")
    else:
        d.arc((x-5,y-89,x+6,y-80),5,175,fill="#743B3A",width=2)
    # green backpack, tiny straps
    rounded(d,(x-22,y-65,x+12,y-42),6,"#4EAE68")
    if action=="water":
        d.line((x+20,y-49,x+47,y-31),fill="#9B6747",width=8)
        d.arc((x+40,y-30,x+68,y-2),180,360,fill="#57BFE8",width=5)

def draw_robot(d,x,floor,t,speaking,point=False,scale=1.0):
    s=.76*scale; y=floor+math.sin(t*4)*2*s
    d.ellipse((x-36,floor-7,x+36,floor+5),fill="#4E8A4E")
    rounded(d,(x-28,y-66,x+28,y-9),13,"#EAF5F9",outline="#6CA8C5",width=3)
    rounded(d,(x-33,y-119,x+33,y-61),15,"#F8FCFF",outline="#6CA8C5",width=3)
    d.line((x,y-135,x,y-120),fill="#537E99",width=4)
    d.ellipse((x-7,y-143,x+7,y-131),fill="#FF9E47")
    # animated eye lights and gaze
    pulse=1 if int(t*4)%2 else 0
    for ex in (x-15,x+15):
        d.ellipse((ex-7,y-100,ex+7,y-85),fill=("#33D2EA" if pulse else "#68BFE0"))
        d.ellipse((ex-2,y-97,ex+3,y-89),fill="#FFFFFF")
    if speaking and int(t*8)%3:
        d.ellipse((x-5,y-78,x+5,y-71),fill="#426B83")
    else:
        rounded(d,(x-12,y-76,x+12,y-71),3,"#F39A42")
    if point:
        d.line((x-20,y-51,x-43,y-34),fill="#D7EBF5",width=8)
        d.line((x-43,y-34,x-46,y-5),fill="#D7EBF5",width=7)
    else:
        d.line((x+22,y-50,x+35,y-27+math.sin(t*4)*7),fill="#D7EBF5",width=8)
        d.ellipse((x+30,y-31+math.sin(t*4)*7,x+41,y-20+math.sin(t*4)*7),fill="#F39A42")

def draw_scene_frame(scene, scene_index, t, speaking, duration):
    action=scene["action"]
    beat=max(0.0,min(1.0,t/max(.1,duration)))
    camera=(scene_index*48)+math.sin(t*.55)*16
    img=background(t,scene_index,camera)
    d=ImageDraw.Draw(img)
    # Blocking changes with the story beat. Close shots keep the speaking
    # character and the shared prop readable; only group beats use a wide cast.
    cast={
        "discover": (370, 815, 1070, 1090),
        "plant": (360, 750, 1040, 1090),
        "water": (330, 650, 850, 1085),
        "point": (375, 700, 1050, 830),
        "carry": (370+beat*85, 790+beat*85, 1060, 1090),
        "bloom": (365, 760, 1050, 1090),
        "celebrate": (220, 500, 825, 1100),
        "wave": (220, 500, 825, 1100),
    }
    cx,mini_x,squirrel_x,robot_x=cast[action]
    cx+=math.sin(t*.7)*8
    mini_x-=math.sin(t*.7)*5
    present={
        "discover": (True,True,False,False), "plant": (True,True,True,False),
        "water": (True,True,True,False), "point": (True,True,False,True),
        "carry": (True,True,True,False), "bloom": (True,True,True,False),
        "celebrate": (True,True,True,True), "wave": (True,True,True,True),
    }[action]
    pot_x=535+beat*48 if action=="carry" else 535
    pot_bob=abs(math.sin(t*9))*4 if action=="carry" else 0
    if action in ("plant","water","carry","bloom"):
        rounded(d,(pot_x,515+pot_bob,pot_x+119,599+pot_bob),17,"#C47648",outline="#8D4F37",width=5)
        d.ellipse((pot_x+10,507+pot_bob,pot_x+109,535+pot_bob),fill="#533E30")
        if action=="bloom":
            bloom=max(0.0,min(1.0,(beat-.24)*1.9))
            stem_y=493-int(42*bloom)
            d.line((pot_x+60,520,pot_x+60,stem_y),fill="#318748",width=8)
            for ang in (0,72,144,216,288):
                a=math.radians(ang); radius=23*bloom
                px=pot_x+60+math.cos(a)*radius; py=stem_y+math.sin(a)*radius
                d.ellipse((px-12*bloom,py-9*bloom,px+12*bloom,py+9*bloom),fill="#FF75A7")
            d.ellipse((pot_x+60-10*bloom,stem_y-10*bloom,pot_x+60+10*bloom,stem_y+10*bloom),fill="#FFD34E")
        elif action!="plant":
            d.line((pot_x+60,520+pot_bob,pot_x+60,492+pot_bob),fill="#318748",width=6)
            d.ellipse((pot_x+43,487+pot_bob,pot_x+59,499+pot_bob),fill="#78C86A")
            d.ellipse((pot_x+61,487+pot_bob,pot_x+77,499+pot_bob),fill="#78C86A")
    gesture=max(0.0,math.sin(math.pi*beat))
    chintu_emotion="surprised" if action in ("discover","bloom") else ("thinking" if action=="plant" else "happy")
    mini_emotion="thinking" if action in ("plant","discover") else ("surprised" if action=="bloom" else "happy")
    scale=1.27 if action not in ("celebrate","wave") else 1.13
    draw_human(d,cx,595,"chintu",t,chintu_emotion,speaking.get("chintu",False),1,
               walk=1.0 if action=="carry" else 0,
               gesture=gesture if action in ("discover","plant","carry","celebrate") else 0,scale=scale)
    draw_human(d,mini_x,595,"mini",t,mini_emotion,speaking.get("mini",False),-1,
               walk=1.0 if action=="carry" else 0,
               gesture=gesture if action in ("plant","water","bloom","celebrate") else 0,scale=scale)
    if present[2]: draw_squirrel(d,squirrel_x,596,t,action,gesture,speaking.get("golu",False),scale=1.25)
    if present[3]: draw_robot(d,robot_x,595,t,speaking.get("tinku",False),point=(action=="point"),scale=1.25)
    # The seed drops into soil, water arcs from Golu's bottle, and the sprout
    # responds on the shared prop instead of adding unrelated ambient motion.
    if action=="discover":
        seed_y=493+abs(math.sin(t*4))*9
        sx=cx+49
        d.ellipse((sx-12,seed_y-12,sx+12,seed_y+12),fill="#FFE269",outline="#FFF8B0",width=3)
        for a in range(0,360,90):
            ax=sx+math.cos(math.radians(a))*19; ay=seed_y+math.sin(math.radians(a))*19
            d.line((ax-4,ay,ax+4,ay),fill="#FFF4A8",width=3)
    if action=="plant":
        sy=446+min(1,beat)*76
        d.ellipse((pot_x+52,sy,pot_x+68,sy+17),fill="#FFD34E")
    if action=="water":
        for i in range(6):
            drop_t=(t*1.7+i*.16)%1
            px=690+drop_t*105; py=435+drop_t*105-math.sin(drop_t*math.pi)*20
            d.ellipse((px-4,py-8,px+4,py+8),fill="#49BDE8",outline="#D8F6FF")
    if action=="celebrate":
        for i in range(18):
            px=(i*79+t*34)%(W); py=205+(i*37)%240+math.sin(t*4+i)*17
            d.ellipse((px-5,py-5,px+5,py+5),fill=("#FF76A4" if i%2 else "#FFE16A"))
    rounded(d,(32,24,1248,105),22,"#FFFEF3",outline="#52AED0",width=3)
    d.text((61,40),scene["title"],font=font(38),fill="#173B53",stroke_width=0)
    rounded(d,(70,620,1210,693),18,"#FFFFFF",outline="#FFE16A",width=3)
    d.text((93,632),scene["line"],font=font(26),fill="#263746")
    zoom=1.025+.07*math.sin(math.pi*beat)
    nw,nh=int(W*zoom),int(H*zoom)
    img=img.resize((nw,nh),Image.Resampling.BICUBIC)
    ox=(nw-W)//2; oy=(nh-H)//2
    return img.crop((ox,oy,ox+W,oy+H))

def run(cmd, **kwargs):
    subprocess.run(cmd, check=True, **kwargs)

def speech_duration(path: Path) -> float:
    with wave.open(str(path),"rb") as wav:
        return wav.getnframes()/float(wav.getframerate())

def concatenate_scene_audio(wavs: list[Path], durations: list[float], output: Path):
    """Put each line in its own scene slot so voice and mouth cues stay aligned."""
    with wave.open(str(wavs[0]),"rb") as first:
        params=first.getparams()
    signature=(params.nchannels,params.sampwidth,params.framerate,params.comptype)
    with wave.open(str(output),"wb") as combined:
        combined.setparams(params)
        for path,duration in zip(wavs,durations):
            with wave.open(str(path),"rb") as line:
                other=line.getparams()
                if (other.nchannels,other.sampwidth,other.framerate,other.comptype) != signature:
                    raise ValueError("TTS clips must share the same WAV format")
                frames=line.readframes(line.getnframes())
            combined.writeframes(frames)
            speech_seconds=len(frames)/(params.framerate*params.nchannels*params.sampwidth)
            silence_samples=max(0,round((duration-speech_seconds)*params.framerate))
            combined.writeframes(b"\x00"*(silence_samples*params.nchannels*params.sampwidth))

def synthesize_voice(text: str, out_wav: Path):
    # Free offline Hindi fallback. Hosted providers remain opt-in; no paid
    # credits are used. Keep speed moderate and lines short for intelligibility.
    run(["espeak","-v","hi","-s","132","-p","48","-a","165","-w",str(out_wav),text])

def build_video(topic: str, out_mp4: Path):
    ASSET_DIR.mkdir(parents=True,exist_ok=True)
    scenes=[dict(item) for item in SCENES]
    if topic and topic.strip() and topic.strip() not in ("चिंटू और दोस्तों की जादुई किताब", "चिंटू और दोस्तों की नई खोज"):
        # The fixed original episode is safe and coherent; preserve the user's
        # topic in the opening slate instead of pretending to have rewritten it.
        scenes[0]["title"]=topic.strip()[:32]
    durations=[]
    wavs=[]
    for i,scene in enumerate(scenes):
        wav=ASSET_DIR/f"line_{i:02d}.wav"
        synthesize_voice(scene["line"],wav)
        wavs.append(wav)
        durations.append(max(4.8,speech_duration(wav)+1.1))
    total=sum(durations)
    audio=ASSET_DIR/"narration.wav"
    concatenate_scene_audio(wavs,durations,audio)
    # Raw-frame pipe avoids a directory full of thousands of PNGs and keeps
    # every body, face, background and prop animated at the output frame rate.
    out_mp4.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",str(out_mp4)],stdin=subprocess.PIPE)
    offset=0.0
    previous_frame=None
    transition_frames=round(.42*FPS)
    try:
        for si,(scene,duration) in enumerate(zip(scenes,durations)):
            frames=math.ceil(duration*FPS)
            spk=scene["speaker"]
            for fi in range(frames):
                local_t=fi/FPS
                # Approximate word timing from the speech line; the character
                # mouth moves only during the corresponding spoken scene.
                speaking={"chintu":False,"mini":False,"tinku":False,"golu":False}
                if spk in speaking and local_t < duration-0.75:
                    speaking[spk]=int(local_t*8)%3 != 0
                frame=draw_scene_frame(scene,si,offset+local_t,speaking,duration)
                if previous_frame is not None and fi < transition_frames:
                    # Brief cross-dissolves join story beats as a cartoon
                    # sequence instead of a hard cut between poster-like cards.
                    alpha=min(1.0,(fi+1)/transition_frames)
                    frame=Image.blend(previous_frame,frame,alpha)
                proc.stdin.write(frame.tobytes())
                if fi == frames-1:
                    previous_frame=frame.copy()
            offset+=duration
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError("ffmpeg failed while encoding animated frames")
    except Exception:
        if proc.stdin and not proc.stdin.closed: proc.stdin.close()
        proc.kill(); proc.wait(); raise
    muxed=ASSET_DIR/"final.mp4"
    run(["ffmpeg","-y","-i",str(out_mp4),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-af","apad","-t",f"{total:.2f}","-c:v","copy","-c:a","aac","-b:a","128k","-movflags","+faststart",str(muxed)])
    muxed.replace(out_mp4)

if __name__=="__main__":
    topic=os.getenv("KIDS_TOPIC","चिंटू और दोस्तों की बगीचे वाली खोज")
    output=Path(os.getenv("KIDS_OUTPUT","/tmp/kids-video.mp4"))
    build_video(topic,output)
    print(output)
