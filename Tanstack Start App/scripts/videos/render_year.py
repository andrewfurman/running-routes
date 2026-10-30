#!/usr/bin/env python3
"""Render a full-screen Google Maps run video from a handful of attributed area captures."""
import argparse, hashlib, json, math, subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[3]
W,H,FPS=1280,720,24
PURPLE='#754bb0'; ACTIVE='#f58124'
def timestamp(value):
    try:return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo('America/New_York'))
    except ValueError:return datetime.strptime(value,'%b %d, %Y, %I:%M:%S %p').replace(tzinfo=timezone.utc).astimezone(ZoneInfo('America/New_York'))
def font(size):
    for path in ['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)
def mercator(lng,lat,zoom):
    scale=256*2**zoom;lat=math.radians(max(-85,min(85,lat)))
    return ((lng+180)/360*scale,(1-math.log(math.tan(lat)+1/math.cos(lat))/math.pi)/2*scale)
def project(area,p):
    x,y=mercator(p[0],p[1],area['zoom']);cx,cy=mercator(area['lng'],area['lat'],area['zoom']);return(x-cx+W/2,y-cy+H/2)
def draw_lines(draw,lines,area,color,width,progress=1):
    total=sum(max(0,len(line)-1) for line in lines);remaining=math.ceil(total*progress);head=None
    for line in lines:
        count=min(len(line),remaining+1)
        if count>1:
            pts=[project(area,p) for p in line[:count]];draw.line(pts,fill=color,width=width,joint='curve');head=pts[-1]
        remaining-=max(0,len(line)-1)
        if remaining<=0:break
    return head
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--year',type=int,default=2026);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--basemaps',type=Path,required=True,help='JSON with area IDs, center lng/lat, zoom and local captured PNG filename');args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    areas=json.loads(args.basemaps.read_text());backgrounds={a['id']:Image.open(args.basemaps.parent/a['file']).convert('RGB').resize((W,H),Image.Resampling.LANCZOS) for a in areas};layers={a['id']:Image.new('RGBA',(W,H)) for a in areas}
    source=ROOT/'raw-data/runs/tracks.geojson';features=json.loads(source.read_text())['features'];runs=[]
    for feature in features:
        p=feature['properties'];assert p['activity_type'] in {'Run','TrailRun','Trail Run','VirtualRun','Virtual Run'};t=timestamp(p['date'])
        if t.year!=args.year:continue
        lines=feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiLineString' else [feature['geometry']['coordinates']]
        pts=[p for line in lines for p in line];xs=sorted(p[0] for p in pts);ys=sorted(p[1] for p in pts);center=(xs[len(xs)//2],ys[len(ys)//2])
        area=min(areas,key=lambda a:math.hypot((center[0]-a['lng'])*math.cos(math.radians(center[1])),center[1]-a['lat']))
        # Every source coordinate must fit the selected full-screen background.
        assert all(0<=project(area,p)[0]<W and 0<=project(area,p)[1]<H-24 for p in pts),(p['activity_id'],area['id'])
        runs.append((t,str(p['activity_id']),lines,area))
    runs.sort(key=lambda r:(r[0],r[1]));assert runs and len({r[1] for r in runs})==len(runs)
    name=f'runs-{args.year}-google';video=args.output/(name+'.mp4');encoder=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE);frames=0
    def emit(im,n=1):
        nonlocal frames
        raw=im.tobytes()
        for _ in range(n):encoder.stdin.write(raw);frames+=1
    start=runs[0][0];end=runs[-1][0]
    for index,(t,aid,lines,area) in enumerate(runs):
        complete=Image.alpha_composite(backgrounds[area['id']].convert('RGBA'),layers[area['id']])
        for step in range(8):
            im=complete.copy();d=ImageDraw.Draw(im);head=draw_lines(d,lines,area,ACTIVE,5,(step+1)/8)
            if head:d.ellipse((head[0]-5,head[1]-5,head[0]+5,head[1]+5),fill=ACTIVE,outline='white',width=2)
            # Keep the bottom 30px intact: Google logo and exact provider attribution.
            hud=Image.new('RGBA',(W,H));hd=ImageDraw.Draw(hud);hd.rounded_rectangle((24,H-139,W-24,H-37),radius=15,fill=(255,255,255,235));im=Image.alpha_composite(im,hud);d=ImageDraw.Draw(im)
            d.text((44,H-127),t.strftime('%A, %B %d, %Y'),fill='#282132',font=font(27));d.text((44,H-91),f'{area["label"]} · Run {index+1} of {len(runs)}',fill='#60556d',font=font(14));d.text((W-360,H-122),'● Current run',fill=ACTIVE,font=font(17));d.text((W-190,H-122),'● Earlier runs',fill=PURPLE,font=font(17))
            x0,x1=44,W-44;y=H-54;progress=(t-start).total_seconds()/max(1,(end-start).total_seconds());x=x0+(x1-x0)*progress;d.rounded_rectangle((x0,y,x1,y+5),radius=2,fill='#ddd5e7');d.rounded_rectangle((x0,y,max(x0+2,x),y+5),radius=2,fill=PURPLE);d.ellipse((x-5,y-3,x+5,y+7),fill=ACTIVE)
            im=im.convert('RGB')
            if index==0 and step==0:emit(im,24)
            emit(im)
        draw_lines(ImageDraw.Draw(layers[area['id']]),lines,area,(117,75,176,205),3)
        if index%30==0:print(f'Rendered {index+1}/{len(runs)}',flush=True)
    emit(im,72);encoder.stdin.close();assert encoder.wait()==0
    im.save(args.output/(name+'.jpg'),quality=93)
    metadata={'id':name,'title':f'{args.year} running year to date','year':args.year,'runCount':len(runs),'firstDate':runs[0][0].date().isoformat(),'lastDate':runs[-1][0].date().isoformat(),'durationSeconds':round(frames/FPS,2),'width':W,'height':H,'activityIds':[r[1] for r in runs],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'videoBytes':video.stat().st_size,'basemapProvider':'Google Maps','areas':[{k:a[k] for k in ['id','label','lat','lng','zoom']} for a in areas],'description':'Full-screen Google Maps. Orange draws the active run; purple preserves earlier runs. The date and timeline appear along the bottom. Includes every 2026 GPS run, with the main map switching locations for travel.','videoUrl':f'/media/{name}.mp4','posterUrl':f'/media/{name}.jpg'}
    (args.output/(name+'.json')).write_text(json.dumps(metadata,indent=2)+'\n');print(f'Created {video}: {len(runs)} runs, {frames/FPS:.1f} seconds, {video.stat().st_size} bytes')
if __name__=='__main__':main()
