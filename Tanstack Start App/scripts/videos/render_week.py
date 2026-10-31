#!/usr/bin/env python3
"""Render a rolling seven-day portrait calendar map: old lavender, weekly blue, active gold."""
import argparse,hashlib,json,subprocess,math
from datetime import date,timedelta,datetime
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
from render_year import ROOT,mercator
from render_year import font
from weekly_stats import weekly_stats,duration,pace,ZONE,calendar_week
W,H,MAP_H,MAP_Y,FPS=1080,1920,1200,150,24
MAP_ZOOM=1.12
BG='#141c2b';WHITE='#f7f9ff';MUTED='#acb8cb';GOLD='#f6c553';BLUE='#174f9c';LAVENDER='#ad91cf'
def xy(area,p):
 x,y=mercator(p[0],p[1],area['zoom']);cx,cy=mercator(area['lng'],area['lat'],area['zoom']);return((x-cx)*MAP_ZOOM+W/2,(y-cy)*MAP_ZOOM+MAP_H/2)
def draw_track(draw,lines,area,color,width,fraction=1):
 left=math.ceil(sum(max(0,len(line)-1) for line in lines)*fraction);head=None
 for line in lines:
  n=min(len(line),left+1)
  if n>1:
   pts=[xy(area,p) for p in line[:n]];draw.line(pts,fill=color,width=width,joint='curve');head=pts[-1]
  left-=max(0,len(line)-1)
  if left<=0:break
 return head
def running_time(seconds):
 minutes=round(seconds/60);hours,minutes=divmod(minutes,60)
 return f'{hours}h {minutes:02d}m' if hours else f'{minutes}m'
def text(draw,pos,value,size=24,color=MUTED):draw.text(pos,value,fill=color,font=font(size))
def lines_of(feature):return feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiLineString' else [feature['geometry']['coordinates']]
def clear_attribution(layer):layer.paste((0,0,0,0),(0,MAP_H-48,W,MAP_H))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--as-of',default=None);ap.add_argument('--version',default='v5');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--basemaps',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 metadata_path=ROOT/'raw-data/runs/activities.json';data=json.loads(metadata_path.read_text());as_of=args.as_of or datetime.now(ZONE).date().isoformat();_,calendar_end=calendar_week(as_of);stats=weekly_stats([r for r in data['runs'] if r['localDate']<=as_of],calendar_end.isoformat());start=date.fromisoformat(stats['windowStart']);end=date.fromisoformat(stats['windowEnd']);tracks_path=ROOT/'raw-data/runs/tracks.geojson';source=tracks_path.read_bytes();assert hashlib.sha256(source).hexdigest()==data['trackSourceSha256'];features=json.loads(source)['features'];lookup={str(f['properties']['activity_id']):f for f in features};records={r['activityId']:r for r in data['runs']};area=next(a for a in json.loads(args.basemaps.read_text()) if a['id']=='havertown');base=Image.open(args.basemaps.parent/area['file']).convert('RGBA');assert base.size==(W,MAP_H)
 # Slightly tighten the map while keeping the original provider footer intact.
 footer=base.crop((0,MAP_H-48,W,MAP_H));crop_w=W/MAP_ZOOM;crop_h=MAP_H/MAP_ZOOM
 base=base.crop(((W-crop_w)/2,(MAP_H-crop_h)/2,(W+crop_w)/2,(MAP_H+crop_h)/2)).resize((W,MAP_H),Image.Resampling.LANCZOS)
 base.paste(footer,(0,MAP_H-48))
 old=Image.new('RGBA',(W,MAP_H));prior_count=0
 for feature in features:
  r=records[str(feature['properties']['activity_id'])]
  if r['localDate']>=stats['windowStart']:continue
  lines=lines_of(feature)
  if not any(0<=xy(area,p)[0]<W and 0<=xy(area,p)[1]<MAP_H-48 for line in lines for p in line):continue
  draw_track(ImageDraw.Draw(old),lines,area,(173,145,207,160),3);prior_count+=1
 clear_attribution(old);old_map=Image.alpha_composite(base,old);blue=Image.new('RGBA',(W,MAP_H));rows=stats['records'];week_lines={r['activityId']:lines_of(lookup[r['activityId']]) if r['activityId'] in lookup else [] for r in rows};mapped=sum(bool(ls) for ls in week_lines.values());all_fit=all(0<=xy(area,p)[0]<W and 0<=xy(area,p)[1]<MAP_H-48 for ls in week_lines.values() for line in ls for p in line)
 name=f'runs-{as_of}-week-{args.version}';video=args.output/(name+'.mp4');encoder=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE);frames=0
 period=f'{start.strftime("%b")} {start.day} – {end.strftime("%b")} {end.day}, {end.year}'
 def frame(index,fraction,cumulative,seconds,active=True,final=False):
  record=rows[index];current=Image.alpha_composite(old_map,blue);layer=Image.new('RGBA',(W,MAP_H))
  if active:
   draw_track(ImageDraw.Draw(layer),week_lines[record['activityId']],area,'#20263a',11,fraction)
   head=draw_track(ImageDraw.Draw(layer),week_lines[record['activityId']],area,GOLD,7,fraction)
   if head:ImageDraw.Draw(layer).ellipse((head[0]-6,head[1]-6,head[0]+6,head[1]+6),fill=GOLD,outline='white',width=2)
  clear_attribution(layer);current=Image.alpha_composite(current,layer);image=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(image)
  suffix='th' if 10<=end.day%100<=20 else {1:'st',2:'nd',3:'rd'}.get(end.day%10,'th')
  text(draw,(60,60),f'Week ending {end.strftime("%B")} {end.day}{suffix}',49,WHITE)
  image.paste(current.convert('RGB'),(0,MAP_Y));draw=ImageDraw.Draw(image)
  for x,color,label in [(60,LAVENDER,'BEFORE THIS WEEK'),(415,BLUE,'COMPLETED THIS WEEK'),(830,GOLD,'DRAWING NOW')]:draw.line((x,1400,x+28,1400),fill=color,width=5);text(draw,(x+40,1388),label,16,MUTED)
  completed={r['localDate'] for r in rows[:index+(1 if final or not active else 0)]};active_day=record['localDate'] if active else None
  # A shared weekday header sits above the aligned date/detail cells.
  draw.rounded_rectangle((50,1430,1030,1680),radius=16,fill='#1a2333',outline='#354155',width=2)
  draw.rounded_rectangle((50,1430,1030,1478),radius=16,fill='#283449')
  draw.rectangle((51,1454,1029,1478),fill='#283449')
  for day in range(7):
   when=start+timedelta(days=day);x=50+day*140;key=when.isoformat();day_runs=[r for r in rows if r['localDate']==key];is_active=key==active_day;color=GOLD if is_active else BLUE if key in completed else '#354155';fill='#3b3422' if is_active else '#1d2b43' if key in completed else '#1a2333'
   if day:draw.line((x,1430,x,1680),fill='#354155',width=2)
   heading=when.strftime('%a').upper();font_heading=font(20);heading_w=draw.textlength(heading,font=font_heading)
   text(draw,(x+(140-heading_w)/2,1441),heading,20,GOLD if is_active else WHITE)
   draw.rectangle((x+2,1480,x+138,1678),fill=fill)
   if is_active:draw.rounded_rectangle((x+2,1432,x+138,1678),radius=10,outline=GOLD,width=3)
   text(draw,(x+14,1489),str(when.day),28,GOLD if is_active else WHITE)
   if not day_runs:text(draw,(x+14,1565),'No run',20,MUTED)
   for slot,run in enumerate(day_runs):
    stamp=datetime.fromisoformat(run['date'].replace('Z','+00:00')).astimezone(ZONE);clock=f'{stamp.hour%12 or 12}:{stamp.minute:02d} '+('AM' if stamp.hour<12 else 'PM');miles=run['distanceMeters']/1609.344;y=1535+slot*(92 if len(day_runs)==1 else 65)
    text(draw,(x+14,y),clock,20 if len(day_runs)==1 else 16,WHITE);text(draw,(x+14,y+(32 if len(day_runs)==1 else 21)),f'{miles:.1f} mi',24 if len(day_runs)==1 else 17,WHITE);text(draw,(x+14,y+(65 if len(day_runs)==1 else 43)),pace(run['movingSeconds']/miles if miles else None).replace(' /mi','/mi'),18,GOLD if is_active else MUTED)
  # All summary values share the same horizontal baseline.
  metrics=[('WEEKLY MILES' if final else 'MILES DRAWN',f'{stats["totalMiles"] if final else cumulative:,.1f}'),('TOTAL RUNNING TIME',running_time(stats['movingSeconds'] if final else seconds)),('AVERAGE START' if final else 'RUNS SHOWN',stats['averageStartLabel'] if final else f'{index+1} / {stats["runCount"]}')]
  for x,(label,value) in zip((60,400,740),metrics):
   text(draw,(x,1730),label,20,MUTED);text(draw,(x,1770),value,44,WHITE)
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
 public={k:v for k,v in stats.items() if k!='records'};public.update(id=name,title='Week ending '+end.strftime('%B')+' '+str(end.day)+('th' if 10<=end.day%100<=20 else {1:'st',2:'nd',3:'rd'}.get(end.day%10,'th')),period='calendar-week',asOf=as_of,width=W,height=H,mapHeight=MAP_H,mapZoomFactor=MAP_ZOOM,aspectRatio='9:16',durationSeconds=frames/FPS,finalStatsHoldSeconds=4,mappedRunCount=mapped,allWeekRoutesFit=all_fit,priorLocalHistoryRunCount=prior_count,firstDate=stats['windowStart'],lastDate=stats['windowEnd'],basemapProvider='Google Maps',mapArea='Havertown',palette={'earlierHistory':LAVENDER,'completedWeek':BLUE,'activeRun':GOLD},sourceSha256=hashlib.sha256(source).hexdigest(),metadataSourceSha256=hashlib.sha256(metadata_path.read_bytes()).hexdigest(),videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),videoBytes=video.stat().st_size,videoUrl=f'/media/{name}.mp4',posterUrl=f'/media/{name}.jpg',description='Sunday–Saturday calendar snapshot: older GPS history stays light purple, each active run draws in gold then turns dark blue. A separate Sunday–Saturday header sits above the date and daily run details, with the active day highlighted. The map is zoomed in 12%. Weekly mileage, total running time and average start share one row and linger for four seconds. Mileage and pace use recorded Strava distance and moving time; average start is the circular mean in America/New_York. All weekly mileage is counted even if a run is outside the fixed Havertown map.')
 (args.output/(name+'.json')).write_text(json.dumps(public,indent=2)+'\n');print(f'Created {video}: {frames/FPS:.2f}s · {stats["totalMiles"]:.2f} mi · {stats["averageStartLabel"]} average start · {pace(stats["averagePaceSecondsPerMile"])}')
if __name__=='__main__':main()
