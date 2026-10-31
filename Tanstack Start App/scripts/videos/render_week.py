#!/usr/bin/env python3
"""Render a rolling seven-day portrait map: old lavender, weekly blue, active gold."""
import argparse,hashlib,json,subprocess
from datetime import date,timedelta,datetime
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
from render_story import ROOT,xy,draw_track
from render_year import font
from weekly_stats import weekly_stats,duration,pace,ZONE
W,H,MAP_H,MAP_Y,FPS=1080,1920,810,350,24
BG='#141c2b';WHITE='#f7f9ff';MUTED='#acb8cb';GOLD='#f6c553';BLUE='#174f9c';LAVENDER='#baa4da'
def text(draw,pos,value,size=24,color=MUTED):draw.text(pos,value,fill=color,font=font(size))
def lines_of(feature):return feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiLineString' else [feature['geometry']['coordinates']]
def clear_attribution(layer):layer.paste((0,0,0,0),(0,MAP_H-28,W,MAP_H))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--as-of',default=None);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--basemaps',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 metadata_path=ROOT/'raw-data/runs/activities.json';data=json.loads(metadata_path.read_text());as_of=args.as_of or datetime.now(ZONE).date().isoformat();stats=weekly_stats(data['runs'],as_of);start=date.fromisoformat(stats['windowStart']);end=date.fromisoformat(stats['windowEnd']);tracks_path=ROOT/'raw-data/runs/tracks.geojson';source=tracks_path.read_bytes();assert hashlib.sha256(source).hexdigest()==data['trackSourceSha256'];features=json.loads(source)['features'];lookup={str(f['properties']['activity_id']):f for f in features};records={r['activityId']:r for r in data['runs']};area=next(a for a in json.loads(args.basemaps.read_text()) if a['id']=='havertown');base=Image.open(args.basemaps.parent/area['file']).convert('RGBA');assert base.size==(W,MAP_H)
 old=Image.new('RGBA',(W,MAP_H));prior_count=0
 for feature in features:
  r=records[str(feature['properties']['activity_id'])]
  if r['localDate']>=stats['windowStart']:continue
  lines=lines_of(feature)
  if not any(0<=xy(area,p)[0]<W and 0<=xy(area,p)[1]<MAP_H-28 for line in lines for p in line):continue
  draw_track(ImageDraw.Draw(old),lines,area,(186,164,218,135),3);prior_count+=1
 clear_attribution(old);old_map=Image.alpha_composite(base,old);blue=Image.new('RGBA',(W,MAP_H));rows=stats['records'];week_lines={r['activityId']:lines_of(lookup[r['activityId']]) if r['activityId'] in lookup else [] for r in rows};mapped=sum(bool(ls) for ls in week_lines.values());all_fit=all(0<=xy(area,p)[0]<W and 0<=xy(area,p)[1]<MAP_H-28 for ls in week_lines.values() for line in ls for p in line)
 name=f'runs-{as_of}-week';video=args.output/(name+'.mp4');encoder=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE);frames=0
 period=f'{start.strftime("%b")} {start.day} – {end.strftime("%b")} {end.day}, {end.year}'
 def frame(index,fraction,cumulative,seconds,active=True,final=False):
  record=rows[index];current=Image.alpha_composite(old_map,blue);layer=Image.new('RGBA',(W,MAP_H))
  if active:
   head=draw_track(ImageDraw.Draw(layer),week_lines[record['activityId']],area,GOLD,7,fraction)
   if head:ImageDraw.Draw(layer).ellipse((head[0]-6,head[1]-6,head[0]+6,head[1]+6),fill=GOLD,outline='white',width=2)
  clear_attribution(layer);current=Image.alpha_composite(current,layer);image=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(image)
  text(draw,(60,88),'ROLLING 7 DAYS  /  HAVERTOWN',25,GOLD);text(draw,(60,135),period,45,WHITE)
  text(draw,(60,215),'WEEK COMPLETE' if final else date.fromisoformat(record['localDate']).strftime('%A, %b %d'),28,WHITE)
  text(draw,(60,268),f'{stats["runCount"]} runs · {stats["dayCount"]} active days' if final else f'{record["distanceMeters"]/1609.344:.2f} mi · {duration(record["movingSeconds"])} moving',35,WHITE)
  image.paste(current.convert('RGB'),(0,MAP_Y));draw=ImageDraw.Draw(image)
  for x,color,label in [(60,LAVENDER,'BEFORE THIS WEEK'),(415,BLUE,'COMPLETED THIS WEEK'),(830,GOLD,'DRAWING NOW')]:draw.line((x,1200,x+28,1200),fill=color,width=5);text(draw,(x+40,1188),label,16,MUTED)
  completed={r['localDate'] for r in rows[:index+(1 if final or not active else 0)]};active_day=record['localDate'] if active else None
  for day in range(7):
   when=start+timedelta(days=day);x=60+day*138;color=GOLD if when.isoformat()==active_day else BLUE if when.isoformat() in completed else '#354155';draw.rounded_rectangle((x,1250,x+122,1260),radius=4,fill=color);text(draw,(x,1278),when.strftime('%a %d'),20,WHITE if color in (BLUE,GOLD) else MUTED)
  text(draw,(60,1340),'WEEKLY MILES' if final else 'MILES DRAWN SO FAR',23,MUTED);text(draw,(60,1370),f'{stats["totalMiles"] if final else cumulative:,.2f}',78,WHITE)
  text(draw,(60,1505),'TOTAL RUNNING TIME',21,MUTED);text(draw,(60,1540),duration(stats['movingSeconds'] if final else seconds),44,WHITE)
  if final:
   text(draw,(570,1505),'AVERAGE START',21,MUTED);text(draw,(570,1540),stats['averageStartLabel'],44,WHITE);text(draw,(60,1640),'AVERAGE DISTANCE',21,MUTED);text(draw,(60,1675),f'{stats["averageDistanceMiles"]:.2f} mi',44,WHITE);text(draw,(570,1640),'AVERAGE PACE',21,MUTED);text(draw,(570,1675),pace(stats['averagePaceSecondsPerMile']),44,WHITE)
  else:
   text(draw,(570,1505),'RUNS SHOWN',21,MUTED);text(draw,(570,1540),f'{index+1} / {stats["runCount"]}',44,WHITE);text(draw,(60,1655),'Gold draws the active run.',28,GOLD);text(draw,(60,1705),'Each completed run turns dark blue.',26,WHITE)
  text(draw,(60,1790),'Recorded Strava mileage · Moving-time pace',20,MUTED);text(draw,(60,1832),'Earlier history stays light purple. Map stays in Havertown.',18,MUTED)
  return image
 def emit(image,count=1):
  nonlocal frames
  raw=image.tobytes()
  for _ in range(count):encoder.stdin.write(raw);frames+=1
 cumulative=0;seconds=0;emit(frame(0,0,0,0),24)
 for index,record in enumerate(rows):
  miles=record['distanceMeters']/1609.344
  for step in range(48):
   fraction=(step+1)/48;emit(frame(index,fraction,cumulative+miles*fraction,seconds+record['movingSeconds']*fraction))
  cumulative+=miles;seconds+=record['movingSeconds'];draw_track(ImageDraw.Draw(blue),week_lines[record['activityId']],area,BLUE,5);clear_attribution(blue);emit(frame(index,1,cumulative,seconds,active=False),8);print(f'Drawn {index+1}/{len(rows)} · {record["localDate"]}',flush=True)
 final=frame(len(rows)-1,1,cumulative,seconds,active=False,final=True);emit(final,96);encoder.stdin.close();assert encoder.wait()==0;poster=args.output/(name+'.jpg');final.save(poster,quality=93)
 public={k:v for k,v in stats.items() if k!='records'};public.update(id=name,title='Last 7 days · '+period,period='rolling-7-days',asOf=as_of,width=W,height=H,aspectRatio='9:16',durationSeconds=frames/FPS,finalStatsHoldSeconds=4,mappedRunCount=mapped,allWeekRoutesFit=all_fit,priorLocalHistoryRunCount=prior_count,firstDate=stats['windowStart'],lastDate=stats['windowEnd'],basemapProvider='Google Maps',mapArea='Havertown',palette={'earlierHistory':LAVENDER,'completedWeek':BLUE,'activeRun':GOLD},sourceSha256=hashlib.sha256(source).hexdigest(),metadataSourceSha256=hashlib.sha256(metadata_path.read_bytes()).hexdigest(),videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),videoBytes=video.stat().st_size,videoUrl=f'/media/{name}.mp4',posterUrl=f'/media/{name}.jpg',description='Rolling seven-day snapshot: older GPS history stays light purple, each active run draws in gold then turns dark blue. Final weekly statistics linger for four seconds. Mileage and pace use recorded Strava distance and moving time; average start is the circular mean in America/New_York. All weekly mileage is counted even if a run is outside the fixed Havertown map.')
 (args.output/(name+'.json')).write_text(json.dumps(public,indent=2)+'\n');print(f'Created {video}: {frames/FPS:.2f}s · {stats["totalMiles"]:.2f} mi · {stats["averageStartLabel"]} average start · {pace(stats["averagePaceSecondsPerMile"])}')
if __name__=='__main__':main()
