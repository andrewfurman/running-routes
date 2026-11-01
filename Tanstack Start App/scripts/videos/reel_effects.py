"""Deterministic motion accents for the silent weekly Reel master."""
import math
from PIL import Image, ImageDraw

def celebration(image, progress, center, footer_height=48):
    t=max(0,min(1,progress))
    dx=round(14*math.sin(t*math.tau*5)*(1-t))
    dy=round(10*math.sin(t*math.tau*7)*(1-t))
    result=image.copy();result.paste(image,(dx,dy))
    # Camera motion never shifts or clips the provider's attribution footer.
    footer=image.crop((0,image.height-footer_height,image.width,image.height))
    layer=Image.new('RGBA',image.size);draw=ImageDraw.Draw(layer)
    for i in range(56):
        angle=i*2.399963;speed=180+(i*47)%300;radius=18+speed*t
        x=center[0]+math.cos(angle)*radius;y=center[1]+math.sin(angle)*radius+100*t*t
        alpha=round(240*(1-t));color=[(246,197,83,alpha),(255,248,215,alpha),(22,185,172,alpha)][i%3]
        size=4+(i%3);segment=(x,y,x-math.cos(angle)*24*(1-t),y-math.sin(angle)*24*(1-t));draw.line(segment,fill=(32,38,58,alpha),width=size+4);draw.line(segment,fill=color,width=size)
    radius=20+210*t;alpha=round(190*(1-t));box=(center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius)
    draw.ellipse(box,outline=(32,38,58,alpha),width=7);draw.ellipse(box,outline=(246,197,83,alpha),width=3)
    layer.paste((0,0,0,0),(0,image.height-footer_height,image.width,image.height))
    result=Image.alpha_composite(result.convert('RGBA'),layer)
    result.paste(footer,(0,image.height-footer_height))
    return result
