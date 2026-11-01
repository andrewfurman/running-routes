"""Deterministic motion accents for the silent weekly Reel master."""
import math
from PIL import Image, ImageDraw, ImageFilter

def celebration(image, progress, center, footer_height=48):
    t=max(0,min(1,progress))
    envelope=math.sin(math.pi*t)**.7
    dx=round(25*math.sin(t*math.tau*6)*envelope)
    dy=round(18*math.sin(t*math.tau*8)*envelope)
    result=image.copy();result.paste(image,(dx,dy))
    # Preserve the original provider attribution throughout the effect.
    footer=image.crop((0,image.height-footer_height,image.width,image.height))
    layer=Image.new('RGBA',image.size);draw=ImageDraw.Draw(layer)
    cx,cy=center
    # Expanding, overlapping flame lobes: orange edges, gold body, pale hot core.
    growth=math.sin(min(1,t/.13)*math.pi/2)
    radius=350*growth
    fade=min(1,t/.12)*max(0,min(1,(1-t)/.48))
    for scale,color in [(1.25,(227,63,13)),(1,(255,119,13)),(.7,(255,195,38)),(.38,(255,242,171))]:
        for i in range(17):
            angle=i*2.399963+t*1.8
            offset=radius*scale*(.28+.11*math.sin(i*7))
            x=cx+math.cos(angle)*offset;y=cy+math.sin(angle)*offset-100*t
            size=radius*scale*(.58+.08*math.sin(i*3))
            draw.ellipse((x-size,y-size,x+size,y+size),fill=(*color,round(210*fade)))
    layer=layer.filter(ImageFilter.GaussianBlur(10))
    draw=ImageDraw.Draw(layer)
    for i in range(96):
        angle=i*2.399963;distance=(120+(i*53)%590)*t
        x=cx+math.cos(angle)*distance;y=cy+math.sin(angle)*distance+180*t*t
        alpha=round(230*envelope);size=3+i%5
        draw.line((x,y,x-math.cos(angle)*35*(1-t),y-math.sin(angle)*35*(1-t)),fill=(255,193+(i%50),52,alpha),width=size)
    # The final frame settles back to the unmodified map; no white flash.
    layer.paste((0,0,0,0),(0,image.height-footer_height,image.width,image.height))
    result=Image.alpha_composite(result.convert('RGBA'),layer)
    result.paste(footer,(0,image.height-footer_height))
    return result
