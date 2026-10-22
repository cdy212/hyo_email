# -*- coding: utf-8 -*-
"""Email-presign image pipeline: RSV workshop 2026.
Uses the organizer's source panels corresponding to the provided flyer.
Run: C:\\Python37\\python.exe build_email_261022_neonatology.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, random

DIR=Path(__file__).resolve().parent
W=1000
HEAD=572
PADDING=18
GAP=22
BOTTOM=86
BG="#86b8a2"
PINK="#fff8f5"
MINT="#639f8b"
DARK="#40312f"
LIME="#d1dc90"
random.seed(26)

def font(size, bold=False):
    paths = [
      "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
      "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    return ImageFont.load_default()

def centered(draw,text,y,fnt,fill,canvas_width=W):
    box=draw.textbbox((0,0),text,font=fnt)
    draw.text(((canvas_width-(box[2]-box[0]))//2,y),text,font=fnt,fill=fill)

def ellipse(d,bb,fill):d.ellipse(tuple(map(int,bb)),fill=fill)

def flower(d,cx,cy,r=13,petal="#efa89e",middle="#fff4bd"):
    for i in range(5):
        a=math.tau*i/5
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r
        ellipse(d,(x-8,y-11,x+8,y+11),petal)
    ellipse(d,(cx-7,cy-7,cx+7,cy+7),middle)

def bear(d,x,y,k=1):
    def E(bb,color): ellipse(d,[x+a*k if i%2==0 else y+a*k for i,a in enumerate(bb)],color)
    brown="#8a6353"; inner="#f1b3a0"
    E((5,-71,120,49),brown)
    E((4,-104,49,-58),brown);E((79,-107,124,-58),brown)
    E((16,-95,36,-73),inner);E((91,-95,111,-73),inner)
    E((16,-140,113,-52),brown)
    E((44,-110,52,-101),DARK);E((79,-110,87,-101),DARK)
    E((59,-88,70,-78),DARK)
    E((33,-87,49,-74),inner);E((80,-87,96,-74),inner)
    E((-4,-5,34,46),brown); E((100,-5,134,46),brown)
    flower(d,x+148*k,y+12*k,12)

def bird(d,x,y,k=1):
    def E(bb,color):ellipse(d,[x+a*k if i%2==0 else y+a*k for i,a in enumerate(bb)],color)
    yellow="#f9dd81"
    E((0,-88,104,28),yellow);E((30,-114,76,-65),yellow)
    E((17,-58,31,-44),DARK);E((70,-58,84,-44),DARK)
    E((36,-34,65,-14),"#e99a6a")
    E((12,-41,31,-23),"#eaa1a1");E((76,-41,95,-23),"#eaa1a1")
    flower(d,x+112*k,y-22*k,15,petal="#e5a4a3")
    flower(d,x-17*k,y-5*k,14,petal="#c58c9c")

def header_image():
    im=Image.new("RGB",(W,HEAD),PINK)
    d=ImageDraw.Draw(im)
    # Small leaves and elegant decorations
    colors=["#68b7ac","#e8a69a","#cfdc8c","#75a6ad","#e6c5a9"]
    coords=[(65,72),(120,35),(871,32),(932,80),(972,236),(28,295),(103,315),(902,345),(987,415)]
    for idx,(x,y) in enumerate(coords):
        d.ellipse((x-17,y-6,x+17,y+5),fill=colors[idx%len(colors)])
    d.text((806,25),"대한신생아학회",font=font(18,True),fill=MINT)
    centered(d,"제4회 대한신생아학회",100,font(63,True),DARK)
    centered(d,"감염관리 Workshop",175,font(77,True),MINT)
    d.line((97,278,903,278),fill="#aa9c97",width=2)
    centered(d,"RSV Prevention in the New Era:",292,font(30,True),DARK)
    centered(d,"From Evidence to Action in Korea",330,font(30,True),DARK)
    centered(d,"2026년 11월 27일(금) 13:00–17:30",387,font(29,True),DARK)
    centered(d,"롯데호텔월드 지하 1층 사파이어볼룸",426,font(28,True),DARK)
    d.polygon([(0,470),(150,478),(320,461),(540,477),(760,457),(1000,480),(1000,572),(0,572)],fill=LIME)
    d.polygon([(0,536),(220,511),(435,545),(650,509),(870,540),(1000,517),(1000,572),(0,572)],fill="#70a48c")
    bear(d,37,512,.68)
    bird(d,860,509,.68)
    return im

panels=[("intro","261022_neonatology_intro.jpg"),
        ("program","261022_neonatology_program.jpg"),
        ("registration","261022_neonatology_rsv.jpg"),
        ("location","261022_neonatology_location.jpg")]
sizes=[]
images=[]
for key,name in panels:
    src=Image.open(DIR/name).convert("RGB")
    h=round(src.height*W/src.width)
    images.append((key,src.resize((W,h),Image.Resampling.LANCZOS)))
    sizes.append((key,src.size,(W,h)))

HEIGHT=HEAD+PADDING+sum(img.height for _,img in images)+(len(images)-1)*GAP+PADDING+BOTTOM
canvas=Image.new("RGB",(W,HEIGHT),BG)
canvas.paste(header_image(),(0,0))
pos=HEAD+PADDING
placements={}
for key,img in images:
    placements[key]=(0,pos,1000,pos+img.height)
    canvas.paste(img,(0,pos))
    pos+=img.height+GAP
d=ImageDraw.Draw(canvas)
centered(d,"대한신생아학회 감염관리 Workshop  |  2026.11.27",HEIGHT-74,font(19,True),"#fffdf6")
centered(d,"사전등록 안내: www.neonatology.or.kr",HEIGHT-43,font(17),"#fffdf6")
out=DIR/"email_261022_neonatology_rsv_main.png"
canvas.save(str(out),optimize=True)

share=header_image().resize((1200,686),Image.Resampling.LANCZOS)
share=share.crop((0,0,1200,600))
share.save(str(DIR/"email_261022_neonatology_rsv_kakao.png"),optimize=True)

# registration panel QR / click region, scaled to composed 1000 px format
_, registration_y, _, _ = placements['registration']
QR=(780,registration_y+65,968,registration_y+290)
print("main",str(out),"size",canvas.size)
print("social",str(DIR/"email_261022_neonatology_rsv_kakao.png"))
print("registration QR map rect", QR)
print("panels",sizes)
print("placement",placements)
