#!/usr/bin/env python3
"""Render a 1080x1920 (9:16) run Story with daily stats and a cumulative mileage graph."""
import argparse, collections, hashlib, json, math, subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw
import imageio_ffmpeg
from render_year import ROOT, timestamp, font, mercator
W,H,MAP_H,MAP_Y,FPS=1080,1920,810,370,24
BG='#171424';WHITE='#faf7ff';MUTED='#b8abc8';PURPLE='#b28af0';ORANGE='#ff9c43'
def xy(area,p):
 x,y=mercator(p[0],p[1],area['zoom']);cx,cy=mercator(area['lng'],area['lat'],area['zoom']);return(x-cx+W/2,y-cy+MAP_H/2)
def draw_track(draw,lines,area,color,width,fraction=1):
 total=sum(max(0,len(line)-1) for line in lines);left=math.ceil(total*fraction);head=None
 for line in lines:
  n=min(len(line),left+1)
  if n>1:
   pts=[xy(area,p) for p in line[:n]];draw.line(pts,fill=color,width=width,joint='curve');head=pts[-1]
  left-=max(0,len(line)-1)
  if left<=0:break
 return head
def label(draw,pos,text,size=24,color=MUTED):draw.text(pos,text,fill=color,font=font(size))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--year',type=int,default=2026);ap.add_argument('--version',default='v2');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--basemaps',type=Path,required=True);ap.add_argument('--stats',type=Path,default=ROOT/'raw-data/runs/2026-distances.json');args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 areas=[a for a in json.loads(args.basemaps.read_text()) if a['id']=='havertown'];assert len(areas)==1;backgrounds={}
 for a in areas:
  image=Image.open(args.basemaps.parent/a['file']).convert('RGBA');assert image.size==(W,MAP_H),'Capture Google Maps at exactly 1080×810, with full attribution';backgrounds[a['id']]=image
 layers={a['id']:Image.new('RGBA',(W,MAP_H)) for a in areas}
 stats=json.loads(args.stats.read_text());assert stats['year']==args.year
 distances={r['activityId']:r for r in stats['records']};source=ROOT/'raw-data/runs/tracks.geojson';assert hashlib.sha256(source.read_bytes()).hexdigest()==stats['trackSourceSha256'];runs=[]
 for feature in json.loads(source.read_text())['features']:
  p=feature['properties'];t=timestamp(p['date'])
  if t.year!=args.year:continue
  assert p['activity_type'] in {'Run','TrailRun','Trail Run','VirtualRun','Virtual Run'}
  aid=str(p['activity_id']);r=distances[aid];assert r['date']==t.date().isoformat() and math.isfinite(r['distanceMeters']) and r['distanceMeters']>=0
  lines=feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiLineString' else [feature['geometry']['coordinates']];points=[p for line in lines for p in line];xs=sorted(p[0] for p in points);ys=sorted(p[1] for p in points);center=(xs[len(xs)//2],ys[len(ys)//2]);area=min(areas,key=lambda a:math.hypot((center[0]-a['lng'])*math.cos(math.radians(center[1])),center[1]-a['lat']))
  # Keep the camera fixed; travel runs still contribute every mile to the stats.
  if not all(0<=xy(area,p)[0]<W and 0<=xy(area,p)[1]<MAP_H-24 for p in points):lines=[]
  runs.append((t,aid,lines,area,r['distanceMeters']/1609.344,r['distanceSource']=='gps_estimate'))
 runs.sort(key=lambda r:(r[0],r[1]));assert len(runs)==len(distances)==len({r[1] for r in runs})
 daily=collections.defaultdict(lambda:{'miles':0,'runs':0,'estimated':False})
 for t,aid,lines,area,miles,estimated in runs:
  day=daily[t.date().isoformat()];day['miles']+=miles;day['runs']+=1;day['estimated']|=estimated
 total=sum(r[4] for r in runs);ceiling=math.ceil(total/100)*100;year_start=datetime(args.year,1,1,tzinfo=runs[0][0].tzinfo);year_end=datetime(args.year+1,1,1,tzinfo=runs[0][0].tzinfo);year_seconds=(year_end-year_start).total_seconds();name=f'runs-{args.year}-story-{args.version}';video=args.output/(name+'.mp4')
 encoder=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE);frames=0
 def emit(image,n=1):
  nonlocal frames
  raw=image.tobytes()
  for _ in range(n):encoder.stdin.write(raw);frames+=1
 cumulative=0;has_estimate=False;graph=[(0,0)]
 for index,(t,aid,lines,area,miles,estimated) in enumerate(runs):
  complete=Image.alpha_composite(backgrounds[area['id']],layers[area['id']]);day=daily[t.date().isoformat()];date_fraction=(t-year_start).total_seconds()/year_seconds;day_fraction=((datetime(t.year,t.month,t.day,tzinfo=t.tzinfo)-year_start).days+1)/((year_end-year_start).days)
  for step in range(6):
   fraction=(step+1)/6;value=cumulative+miles*fraction;image=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(image)
   label(draw,(60,140),f'{args.year}  /  RUNNING ROUTES',26,PURPLE);label(draw,(60,190),t.strftime('%A').upper(),23,MUTED);label(draw,(60,222),t.strftime('%B %d, %Y'),49,WHITE)
   label(draw,(60,294),'DAILY MILES',20,MUTED);label(draw,(60,318),('~' if day['estimated'] else '')+f'{day["miles"]:.2f}',39,WHITE);label(draw,(535,294),'RUNS THIS DAY',20,MUTED);label(draw,(535,318),str(day['runs']),39,WHITE);label(draw,(825,329),f'{index+1} / {len(runs)}',22,PURPLE)
   current=complete.copy();cd=ImageDraw.Draw(current);head=draw_track(cd,lines,area,ORANGE,5,fraction)
   if head:cd.ellipse((head[0]-5,head[1]-5,head[0]+5,head[1]+5),fill=ORANGE,outline='white',width=2)
   # The entire captured map is preserved, including Google's attribution strip.
   image.paste(current.convert('RGB'),(0,MAP_Y));draw=ImageDraw.Draw(image)
   label(draw,(60,1210),'YEAR PROGRESS',20,MUTED);label(draw,(900,1210),f'{day_fraction:.0%}',23,ORANGE);draw.rounded_rectangle((60,1250,1020,1259),radius=4,fill='#3c314f');draw.rounded_rectangle((60,1250,60+960*day_fraction,1259),radius=4,fill=PURPLE);draw.ellipse((55+960*day_fraction,1245,65+960*day_fraction,1264),fill=ORANGE);label(draw,(60,1273),'JAN 1',17,MUTED);label(draw,(943,1273),'DEC 31',17,MUTED)
   label(draw,(60,1322),'CUMULATIVE MILES',23,MUTED);label(draw,(60,1351),('~' if has_estimate or estimated else '')+f'{value:,.2f}',76,WHITE);label(draw,(800,1390),'YEAR TO DATE',20,PURPLE)
   x0,x1,y0,y1=130,1020,1478,1638
   for amount in [0,ceiling/2,ceiling]:
    y=y1-(y1-y0)*amount/ceiling;draw.line((x0,y,x1,y),fill='#3c314f',width=1);label(draw,(60,y-10),f'{amount:.0f}',17,MUTED)
   curve=graph+[(date_fraction,value)];points=[(x0+(x1-x0)*x,y1-(y1-y0)*y/ceiling) for x,y in curve];fill=Image.new('RGBA',(W,H));fd=ImageDraw.Draw(fill);fd.polygon([(x0,y1),*points,(points[-1][0],y1)],fill=(178,138,240,35));image=Image.alpha_composite(image.convert('RGBA'),fill).convert('RGB');draw=ImageDraw.Draw(image);draw.line(points,fill=PURPLE,width=4,joint='curve');px,py=points[-1];draw.ellipse((px-6,py-6,px+6,py+6),fill=ORANGE);label(draw,(x0,1654),'JAN',17,MUTED);label(draw,(x1-38,1654),'DEC',17,MUTED)
   label(draw,(60,1704),'~ Includes GPS-estimated distances.' if stats['gpsEstimatedRecords'] else 'All Strava mileage · Map: Havertown only',19,MUTED)
   if index==0 and step==0:emit(image,24)
   emit(image)
  cumulative+=miles;has_estimate|=estimated;graph.append((date_fraction,cumulative));draw_track(ImageDraw.Draw(layers[area['id']]),lines,area,(117,75,176,205),3)
  if index%30==0:print(f'Rendered {index+1}/{len(runs)} · {cumulative:.2f} mi',flush=True)
 emit(image,72);encoder.stdin.close();assert encoder.wait()==0;image.save(args.output/(name+'.jpg'),quality=93)
 metadata={'id':name,'title':f'{args.year} running year to date · Story','year':args.year,'runCount':len(runs),'mappedRunCount':sum(bool(r[2]) for r in runs),'awayRunCount':sum(not bool(r[2]) for r in runs),'mapArea':'Havertown','dayCount':len(daily),'totalMiles':round(total,4),'stravaDistanceRecords':stats['stravaDistanceRecords'],'gpsEstimatedRecords':stats['gpsEstimatedRecords'],'firstDate':runs[0][0].date().isoformat(),'lastDate':runs[-1][0].date().isoformat(),'durationSeconds':frames/FPS,'width':W,'height':H,'aspectRatio':'9:16','activityIds':[r[1] for r in runs],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'distanceSourceSha256':hashlib.sha256(args.stats.read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'videoBytes':video.stat().st_size,'basemapProvider':'Google Maps','description':'Vertical 9:16 Story with a fixed Havertown map. All runs, including travel, contribute to daily and cumulative mileage and the line graph. Daily miles and runs above Google Maps, orange active routes, purple history, year progress, an animated cumulative mileage counter and a growing line graph below. Mileage uses recorded Strava distances; no GPS-geometry estimates.','videoUrl':f'/media/{name}.mp4','posterUrl':f'/media/{name}.jpg'}
 (args.output/(name+'.json')).write_text(json.dumps(metadata,indent=2)+'\n');print(f'Created {video}: {frames/FPS:.2f}s · {total:.2f} mi · {len(daily)} days')
if __name__=='__main__':main()
