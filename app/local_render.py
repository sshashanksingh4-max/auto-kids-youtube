"""Free-first, frame-by-frame 2D cartoon renderer.

This is deliberately procedural: each scene has a distinct action and the
characters are redrawn every frame with walk cycles, gestures, expressions,
gaze, props and a moving camera. It is a 2D rigged cartoon, not 3D or AI video.
"""
from __future__ import annotations

import math
import json
import os
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from app.voice import synthesize_scene_voice

W, H, FPS = 1280, 720, 24
ASSET_DIR = Path(os.getenv("KIDS_ASSET_DIR", "/tmp/kids-assets"))
STORY_TITLE = "चिंटू और दोस्तों का चमकता बीज"
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

# Twelve authored beats form a six-minute original story. Each action reuses
# the same consistent character rigs while dialogue, props and timed gestures
# advance a complete seed-to-garden arc.
SCENES = [
    {"title":"चमकता हुआ बीज", "line":"एक सुनहरी सुबह चिंटू अपने दोस्तों के साथ बगीचे में खेल रहा था। तभी घास के पास एक छोटी रोशनी चमकी। चिंटू धीरे से झुका और बोला, अरे, यह चमकता बीज कहाँ से आया? मिन्नी ने ध्यान से देखा और गोलू उछलकर पास आ गया।", "action":"discover", "place":"garden", "speaker":"chintu", "seconds":30},
    {"title":"मिन्नी की योजना", "line":"मिन्नी ने कहा, शायद इसे मिट्टी और देखभाल चाहिए। हम इसे गमले में लगाएंगे, लेकिन पहले सही जगह चुनेंगे। चिंटू ने नरम मिट्टी ढूँढ़ी और गोलू ने सूखे पत्ते हटाए। टिंकू ने अपने छोटे सेंसर से जाँचकर बताया कि मिट्टी साफ और नम है।", "action":"plant", "place":"garden", "speaker":"mini", "seconds":30},
    {"title":"पहली बूँदें", "line":"गोलू अपनी छोटी बोतल लेकर आया। उसने धीरे-धीरे पानी डाला ताकि बीज बह न जाए। चिंटू ने गमले को थामे रखा और मिन्नी ने देखा कि पानी मिट्टी में समा रहा है। गोलू मुस्कराकर बोला, अब इसे रोज़ थोड़ा पानी मिलेगा, बहुत ज़्यादा नहीं।", "action":"water", "place":"garden", "speaker":"golu", "seconds":30},
    {"title":"धूप का रास्ता", "line":"टिंकू ने आसमान की ओर इशारा किया। पौधों को पानी के साथ धूप भी चाहिए। बगीचे के एक कोने में पेड़ की छाया थी, इसलिए दोस्तों ने धूप वाली जगह खोजी। मिन्नी ने सुबह की किरणें देखीं और चिंटू को गमला वहाँ रखने का सुझाव दिया।", "action":"point", "place":"garden", "speaker":"tinku", "seconds":30},
    {"title":"मिलकर उठाएँ", "line":"गमला थोड़ा भारी था, इसलिए चिंटू ने अकेले उठाने की कोशिश नहीं की। उसने मिन्नी से मदद माँगी। दोनों ने नीचे से पकड़कर धीरे-धीरे कदम बढ़ाए। गोलू आगे रास्ता दिखाता रहा और टिंकू ने बताया कि वे सुरक्षित जगह पहुँच गए हैं।", "action":"carry", "place":"garden", "speaker":"chintu", "seconds":30},
    {"title":"बगीचे की रखवाली", "line":"अगली सुबह दोस्तों ने गमले को देखा। मिट्टी सूखी लग रही थी, मगर बीज अभी भी ठीक था। गोलू ने छोटी मात्रा में पानी दिया, मिन्नी ने गमले के पास गिरी टहनी हटाई और चिंटू ने पौधे को तेज़ हवा से बचाने के लिए उसे दीवार के पास रखा।", "action":"water", "place":"garden", "speaker":"mini", "seconds":30},
    {"title":"नन्ही कोंपल", "line":"कुछ दिनों बाद मिट्टी से हरी कोंपल बाहर आई। चिंटू खुशी से उछला, लेकिन मिन्नी ने कहा कि हमें इसे धीरे बढ़ने देना चाहिए। गोलू ने पास की मिट्टी नरम की और टिंकू ने सबको याद दिलाया कि पौधे को रोज़ देखना है, खींचना नहीं।", "action":"bloom", "place":"garden", "speaker":"narrator", "seconds":30},
    {"title":"साझा देखभाल", "line":"अब हर दोस्त की एक छोटी ज़िम्मेदारी थी। चिंटू गमले को देखता, मिन्नी पानी की मात्रा जाँचती, गोलू सूखे पत्ते हटाता और टिंकू धूप का समय बताता। किसी दिन एक दोस्त व्यस्त होता तो बाकी उसकी मदद करते। पौधा अकेले किसी एक की मेहनत से नहीं, सबकी देखभाल से बढ़ा।", "action":"celebrate", "place":"garden", "speaker":"narrator", "seconds":30},
    {"title":"फूलों की खुशबू", "line":"एक सुबह पौधे पर छोटी कली दिखाई दी। मिन्नी ने उसे छुए बिना सबको पास बुलाया। कली धीरे-धीरे खुली और बगीचे में रंग भर गया। गोलू ने दूर से ताली बजाई, चिंटू ने खुशी बाँटी और टिंकू की नीली आँखें खुशी से चमक उठीं।", "action":"bloom", "place":"garden", "speaker":"mini", "seconds":30},
    {"title":"नई जगह की खोज", "line":"फूल देखकर दोस्तों को याद आया कि उनके पास और भी बीज हैं। उन्होंने बगीचे में खाली जगह ढूँढ़ी। चिंटू ने हर पौधे के लिए जगह छोड़ी, मिन्नी ने धूप की दिशा देखी और गोलू ने कहा कि तितलियों के लिए भी कुछ फूल रहने चाहिए।", "action":"carry", "place":"garden", "speaker":"chintu", "seconds":30},
    {"title":"रंगों से भरा बगीचा", "line":"कुछ समय बाद कई छोटे पौधे उग आए। तितलियाँ फूलों के ऊपर मंडराईं और दोस्त पानी बाँटने लगे। टिंकू ने समझाया कि पौधे हवा और जीवों के लिए उपयोगी होते हैं। गोलू ने मज़ाक में अपनी बोतल छिपाई, फिर हँसते हुए उसे सबके साथ साझा कर दिया।", "action":"water", "place":"garden", "speaker":"golu", "seconds":30},
    {"title":"छोटी कोशिश, बड़ा बदलाव", "line":"शाम को चारों दोस्त बगीचे के पास बैठे। चिंटू ने कहा कि एक छोटा बीज इतना सुंदर बगीचा बन सकता है, यह उसने नहीं सोचा था। मिन्नी बोली, धैर्य और मिलकर काम करना ज़रूरी है। उन्होंने सीखा कि प्यार और देखभाल से छोटी कोशिश भी बड़ा बदलाव ला सकती है।", "action":"wave", "place":"garden", "speaker":"narrator", "seconds":30},
]

SHORT_SCENES = [
    {"title":"चमकता हुआ बीज!", "line":"अरे, घास में यह चमकता बीज किसका है? चलो, इसे मिलकर उगाते हैं!", "action":"discover", "place":"garden", "speaker":"chintu", "seconds":10},
    {"title":"दोस्ती की योजना", "line":"मिट्टी, पानी और धूप—मिन्नी ने सही तरकीब खोज ली!", "action":"point", "place":"garden", "speaker":"mini", "seconds":10},
    {"title":"बूँद से कली", "line":"गोलू ने पानी दिया और देखो, नन्ही कली खिल गई!", "action":"water", "place":"garden", "speaker":"golu", "seconds":10},
    {"title":"सबका बगीचा", "line":"सबने बीज बाँटे। मिलकर की छोटी कोशिश बड़ा बगीचा बन गई!", "action":"celebrate", "place":"garden", "speaker":"narrator", "seconds":10},
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
               walk: float = 0.0, gesture: float = 0.0, scale: float = 1.0,
               interaction: tuple[float,float] | None = None):
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
        if side==facing and interaction is not None:
            # Reach toward the shared seed, pot or flower, then retract with
            # the gesture pulse; elbows follow the wrist instead of pointing
            # in a fixed direction unrelated to the prop.
            default_hand=hand
            hand=(default_hand[0]+(interaction[0]-default_hand[0])*active,
                  default_hand[1]+(interaction[1]-default_hand[1])*active)
            elbow=(shoulder[0]+(hand[0]-shoulder[0])*.58,
                   shoulder[1]+(hand[1]-shoulder[1])*.62-10*s)
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

def draw_squirrel(d,x,floor,t,action,gesture=0,speaking=False):
    bob=abs(math.sin(t*6))*6; y=floor-bob
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

def draw_robot(d,x,floor,t,speaking,point=False):
    y=floor+math.sin(t*4)*2
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

def draw_scaled_sprite(img, anchor_x, anchor_y, bounds, scale, painter):
    """Draw a small rig on transparency, scale it, and keep its feet planted."""
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    painter(ImageDraw.Draw(layer))
    sprite=layer.crop(bounds)
    sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
    left=round(anchor_x+(bounds[0]-anchor_x)*scale)
    top=round(anchor_y+(bounds[1]-anchor_y)*scale)
    img.paste(sprite,(left,top),sprite)

def draw_scene_frame(scene, scene_index, t, speaking, duration, speech_seconds, local_t, show_subtitles=True):
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
    gesture=max(0.0,math.sin(math.pi*beat))*(.72+.28*math.sin(t*3.1))
    chintu_emotion="surprised" if action in ("discover","bloom") else ("thinking" if action=="plant" else "happy")
    mini_emotion="thinking" if action in ("plant","discover") else ("surprised" if action=="bloom" else "happy")
    scale=1.27 if action not in ("celebrate","wave") else 1.13
    discover_seed_y=493+abs(math.sin(t*4))*9
    chintu_target=None
    mini_target=None
    if action=="discover": chintu_target=(cx+55,discover_seed_y)
    if action=="plant": mini_target=(pot_x+60,510)
    if action=="water": mini_target=(pot_x+105,540)
    if action=="carry":
        chintu_target=(pot_x+12,548); mini_target=(pot_x+108,548)
    if action=="bloom": mini_target=(pot_x+60,450)
    draw_human(d,cx,595,"chintu",t,chintu_emotion,speaking.get("chintu",False),1,
               walk=1.0 if action=="carry" else 0,
               gesture=gesture if action in ("discover","plant","carry","celebrate") else 0,scale=scale,
               interaction=chintu_target)
    draw_human(d,mini_x,595,"mini",t,mini_emotion,speaking.get("mini",False),-1,
               walk=1.0 if action=="carry" else 0,
               gesture=gesture if action in ("plant","water","bloom","celebrate") else 0,scale=scale,
               interaction=mini_target)
    if present[2]:
        draw_scaled_sprite(img,squirrel_x,596,(squirrel_x-40,471,squirrel_x+85,604),1.28,
            lambda sd: draw_squirrel(sd,squirrel_x,596,t,action,gesture,speaking.get("golu",False)))
        d=ImageDraw.Draw(img)
    if present[3]:
        draw_scaled_sprite(img,robot_x,595,(robot_x-44,445,robot_x+44,603),1.24,
            lambda sd: draw_robot(sd,robot_x,595,t,speaking.get("tinku",False),point=(action=="point")))
        d=ImageDraw.Draw(img)
    # The seed drops into soil, water arcs from Golu's bottle, and the sprout
    # responds on the shared prop instead of adding unrelated ambient motion.
    if action=="discover":
        seed_y=discover_seed_y
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
            px=918-drop_t*300; py=435+drop_t*105-math.sin(drop_t*math.pi)*20
            d.ellipse((px-4,py-8,px+4,py+8),fill="#49BDE8",outline="#D8F6FF")
    if action=="celebrate":
        for i in range(18):
            px=(i*79+t*34)%(W); py=205+(i*37)%240+math.sin(t*4+i)*17
            d.ellipse((px-5,py-5,px+5,py+5),fill=("#FF76A4" if i%2 else "#FFE16A"))
    rounded(d,(32,24,1248,105),22,"#FFFEF3",outline="#52AED0",width=3)
    d.text((61,40),scene["title"],font=font(38),fill="#173B53",stroke_width=0)
    if show_subtitles:
        rounded(d,(70,620,1210,693),18,"#FFFFFF",outline="#FFE16A",width=3)
        words=scene["line"].split()
        chunks=[words[i:i+8] for i in range(0,len(words),8)]
        chunk_index=min(len(chunks)-1,int(local_t/max(.1,speech_seconds)*len(chunks))) if chunks else 0
        chunk=chunks[chunk_index] if chunks else []
        d.text((93,622)," ".join(chunk[:4]),font=font(22),fill="#263746")
        d.text((93,650)," ".join(chunk[4:]),font=font(22),fill="#263746")
    zoom=1.025+.07*math.sin(math.pi*beat)
    nw,nh=int(W*zoom),int(H*zoom)
    img=img.resize((nw,nh),Image.Resampling.BICUBIC)
    ox=(nw-W)//2; oy=(nh-H)//2
    return img.crop((ox,oy,ox+W,oy+H))

def render_thumbnail(scene: dict, output_path: Path):
    """Save a clean, high-resolution story frame without dialogue captions."""
    output_path.parent.mkdir(parents=True,exist_ok=True)
    speaking={"chintu":False,"mini":False,"tinku":False,"golu":False}
    speaker=scene["speaker"]
    if speaker in speaking:
        speaking[speaker]=True
    frame=draw_scene_frame(
        scene,0,4.0,speaking,float(scene.get("seconds",10)),8.0,4.0,
        show_subtitles=False,
    )
    frame.save(output_path,"JPEG",quality=94,optimize=True,progressive=True)

def extract_video_thumbnail(source_video: Path, output_path: Path, at_seconds: float=4.0):
    """Extract a sharp poster frame while preserving the video's aspect ratio."""
    output_path.parent.mkdir(parents=True,exist_ok=True)
    run([
        "ffmpeg","-y","-v","error","-ss",str(at_seconds),"-i",str(source_video),
        "-frames:v","1","-q:v","2",str(output_path),
    ])

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

def build_video(out_mp4: Path, scene_definitions: list[dict] | None = None):
    ASSET_DIR.mkdir(parents=True,exist_ok=True)
    scenes=[dict(item) for item in (scene_definitions if scene_definitions is not None else SCENES)]
    durations=[]
    speech_durations=[]
    wavs=[]
    voice_modes=[]
    for i,scene in enumerate(scenes):
        wav=ASSET_DIR/f"line_{i:02d}.wav"
        voice_modes.append(synthesize_scene_voice(scene["line"],scene["speaker"],wav))
        wavs.append(wav)
        speech_seconds=speech_duration(wav)
        speech_durations.append(speech_seconds)
        durations.append(max(float(scene.get("seconds",4.8)),speech_seconds+1.1))
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
        for si,(scene,duration,speech_seconds) in enumerate(zip(scenes,durations,speech_durations)):
            frames=math.ceil(duration*FPS)
            spk=scene["speaker"]
            for fi in range(frames):
                local_t=fi/FPS
                # Approximate word timing from the speech line; the character
                # mouth moves only during the corresponding spoken scene.
                speaking={"chintu":False,"mini":False,"tinku":False,"golu":False}
                if spk in speaking and local_t < speech_seconds:
                    speaking[spk]=int(local_t*8)%3 != 0
                frame=draw_scene_frame(scene,si,offset+local_t,speaking,duration,speech_seconds,local_t)
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
    # Keep honest provenance alongside the render so QA and later publishing
    # gates can distinguish preview audio from the requested natural-voice path.
    out_mp4.with_suffix(".voices.json").write_text(
        json.dumps({
            "provider": os.getenv("KIDS_TTS_PROVIDER", "svara").strip().lower(),
            "scene_voice_modes": voice_modes,
            "note": "eSpeak preview audio is robotic and must not be published.",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_mp4

def render_vertical_short(source_mp4: Path, short_path: Path):
    """Render a separate 40-second story summary in a portrait 9:16 frame."""
    short_path.parent.mkdir(parents=True,exist_ok=True)
    run([
        "ffmpeg","-y","-i",str(source_mp4),"-filter_complex",
        "[0:v]split=2[bg][fg];"
        "[bg]scale=320:568:force_original_aspect_ratio=increase,crop=320:568,boxblur=12:4,scale=720:1280[bgblur];"
        "[fg]scale=720:-2[foreground];"
        "[bgblur][foreground]overlay=(W-w)/2:(H-h)/2,setsar=1[v]",
        "-map","[v]","-map","0:a:0","-c:v","libx264","-preset","veryfast",
        "-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",
        "-movflags","+faststart",str(short_path),
    ])
    source_voice_metadata=source_mp4.with_suffix(".voices.json")
    if source_voice_metadata.exists():
        short_path.with_suffix(".voices.json").write_text(
            source_voice_metadata.read_text(encoding="utf-8"),encoding="utf-8"
        )

if __name__=="__main__":
    output=Path(os.getenv("KIDS_OUTPUT","/tmp/kids-video.mp4"))
    short_output=Path(os.getenv("KIDS_SHORT_OUTPUT","/tmp/kids-short.mp4"))
    thumbnail=Path(os.getenv("KIDS_THUMBNAIL_OUTPUT",str(output.with_suffix(".jpg"))))
    short_thumbnail=Path(os.getenv("KIDS_SHORT_THUMBNAIL_OUTPUT",str(short_output.with_suffix(".jpg"))))
    short_landscape=ASSET_DIR/"short-landscape.mp4"
    build_video(output,SCENES)
    render_thumbnail(SCENES[0],thumbnail)
    build_video(short_landscape,SHORT_SCENES)
    render_vertical_short(short_landscape,short_output)
    extract_video_thumbnail(short_output,short_thumbnail)
    print({"long":str(output),"short":str(short_output),"thumbnail":str(thumbnail),"short_thumbnail":str(short_thumbnail)})
