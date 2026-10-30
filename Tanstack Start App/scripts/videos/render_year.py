#!/usr/bin/env python3
"""Render running-only history chronologically as an H.264 MP4, without map API calls."""
import argparse, hashlib, json, math, subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[3]
W,H,FPS=1280,720,24
PURPLE='#754bb0'; INK='#272135'; MUTED='#797184'

def timestamp(value):
    try:return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo('America/New_York'))
    except ValueError:return datetime.strptime(value,'%b %d, %Y, %I:%M:%S %p').replace(tzinfo=timezone.utc).astimezone(ZoneInfo('America/New_York'))
def font(size):
    for path in ['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)
def projector(bounds,rect):
    west,south,east,north=bounds;x,y,w,h=rect;c=math.cos(math.radians((north+south)/2));scale=min(w/((east-west)*c),h/(north-south));dx=(w-(east-west)*c*scale)/2;dy=(h-(north-south)*scale)/2
    return lambda p:(x+dx+(p[0]-west)*c*scale,y+dy+(north-p[1])*scale)
def line(draw,coords,project,color,width):
    if len(coords)>1:draw.line([project(p) for p in coords],fill=color,width=width,joint='curve')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--year',type=int,default=2026);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=ROOT/'raw-data/runs/tracks.geojson';features=json.loads(source.read_text())['features'];runs=[]
    for f in features:
        assert f['properties']['activity_type'] in {'Run','TrailRun','Trail Run','VirtualRun','Virtual Run'}
        t=timestamp(f['properties']['date'])
        if t.year==args.year:
            lines=f['geometry']['coordinates'] if f['geometry']['type']=='MultiLineString' else [f['geometry']['coordinates']]
            runs.append((t,str(f['properties']['activity_id']),lines))
    runs.sort(key=lambda r:(r[0],r[1]));assert runs,'No GPS runs in selected year'
    graph=json.loads((ROOT/'raw-data/route-research/2026-10-16-gap-replan/street-graph-2026-10-07.json').read_text());base=Image.new('RGB',(W,H),'#f6f4fa');d=ImageDraw.Draw(base)
    d.text((42,28),'RUNNING ROUTES',fill=PURPLE,font=font(16));d.text((40,56),f'{args.year} · One run at a time',fill=INK,font=font(35));d.text((43,104),'A year-to-date GPS journal · Running only',fill=MUTED,font=font(17))
    rect=(35,155,830,460);d.rounded_rectangle((28,147,877,634),radius=20,fill='#eeebf2');project=projector((-75.365,39.943,-75.25,40.015),rect)
    # Draw on a clipped layer so distant activities cannot paint over labels.
    layer=Image.new('RGB',(850,488),'#eeebf2');pd=ImageDraw.Draw(layer);local=lambda p:(project(p)[0]-28,project(p)[1]-147)
    for way in graph['ways']:
        pts=[graph['nodes'][str(n)] for n in way['nodes'] if str(n) in graph['nodes']];line(pd,pts,local,'#d4cfdd',1)
    boundary=json.loads((ROOT/'raw-data/boundaries/19083.geojson').read_text());geom=boundary.get('geometry',boundary);polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    for poly in polys:
        for ring in poly:line(pd,ring,local,'#7caaa3',2)
    base.paste(layer,(28,147));d=ImageDraw.Draw(base);d.text((43,646),'HAVERTOWN / 19083',fill=INK,font=font(15));d.text((43,672),'Street geometry © OpenStreetMap contributors · Boundary: Census ZCTA · Tracks: Strava',fill=MUTED,font=font(12))
    video=args.output/f'runs-{args.year}.mp4';encoder=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
    frames=0
    def emit(im,n=1):
        nonlocal frames
        data=im.tobytes()
        for _ in range(n):encoder.stdin.write(data);frames+=1
    first=None
    for index,(t,aid,lines) in enumerate(runs):
        allpoints=[p for coords in lines for p in coords];xs=[p[0] for p in allpoints];ys=[p[1] for p in allpoints];pad=max(max(xs)-min(xs),max(ys)-min(ys),.002)*.12
        routeproject=projector((min(xs)-pad,min(ys)-pad,max(xs)+pad,max(ys)+pad),(935,285,275,230))
        for step in range(8):
            current=layer.copy();cd=ImageDraw.Draw(current)
            for coords in lines:
                n=max(2,math.ceil(len(coords)*(step+1)/8));line(cd,coords[:n],local,'#9c77c7',2)
            im=base.copy();im.paste(current,(28,147));draw=ImageDraw.Draw(im)
            draw.text((920,165),t.strftime('%B %d, %Y'),fill=INK,font=font(24));draw.text((920,208),f'RUN {index+1:03d} / {len(runs)}',fill=PURPLE,font=font(18));draw.text((920,247),'This run · auto-fitted',fill=MUTED,font=font(14))
            for coords in lines:line(draw,coords[:max(2,math.ceil(len(coords)*(step+1)/8))],routeproject,PURPLE,3)
            draw.text((920,550),'Purple lines accumulate',fill=INK,font=font(17));draw.text((920,579),'Inset includes runs away from home.',fill=MUTED,font=font(13));draw.text((920,603),'GPS records only · No bike rides',fill=MUTED,font=font(13))
            draw.rounded_rectangle((920,655,1230,661),radius=3,fill='#dfd7e9');draw.rounded_rectangle((920,655,920+int(310*(index+1)/len(runs)),661),radius=3,fill=PURPLE)
            if first is None:first=im.copy();emit(im,24)
            emit(im)
        for coords in lines:line(pd,coords,local,PURPLE,2)
        if index%30==0:print(f'Rendered {index+1}/{len(runs)}',flush=True)
    emit(im,72);encoder.stdin.close();assert encoder.wait()==0
    poster=args.output/f'runs-{args.year}.jpg';im.save(poster,quality=90)
    metadata={'id':f'runs-{args.year}','title':f'{args.year} running year to date','year':args.year,'runCount':len(runs),'firstDate':runs[0][0].date().isoformat(),'lastDate':runs[-1][0].date().isoformat(),'durationSeconds':round(frames/FPS,2),'width':W,'height':H,'activityIds':[r[1] for r in runs],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'videoBytes':video.stat().st_size,'description':'GPS runs in chronological order. Main map accumulates Havertown coverage; inset shows every run, including travel. Excludes bike rides and activities without GPS.','videoUrl':f'/media/runs-{args.year}.mp4','posterUrl':f'/media/runs-{args.year}.jpg'}
    (args.output/f'runs-{args.year}.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps({k:v for k,v in metadata.items() if k!='activityIds'},indent=2))
if __name__=='__main__':main()
