#!/usr/bin/env python3
"""Upload a rendered video and poster to R2 using ignored local Cloudflare credentials."""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];APP=ROOT/'Tanstack Start App'
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('directory',type=Path);ap.add_argument('--year',type=int,default=2026);args=ap.parse_args();env=dict(os.environ)
 for line in (ROOT/'.env').read_text().splitlines() if (ROOT/'.env').exists() else []:
  key,sep,value=line.partition('=')
  if sep and key in {'CLOUDFLARE_API_TOKEN','CLOUDFLARE_ACCOUNT_ID'}:env.setdefault(key,value.strip().strip('\"\''))
 meta=json.loads((args.directory/f'runs-{args.year}.json').read_text());video=args.directory/f'runs-{args.year}.mp4'
 if hashlib.sha256(video.read_bytes()).hexdigest()!=meta['videoSha256']:raise SystemExit('Video hash does not match metadata')
 for suffix,mime in [('mp4','video/mp4'),('jpg','image/jpeg')]:
  filename=f'runs-{args.year}.{suffix}';subprocess.run([str(APP/'node_modules/.bin/wrangler'),'r2','object','put','running-routes-media/'+filename,'--file',str((args.directory/filename).resolve()),'--content-type',mime,'--remote'],cwd=APP,env=env,check=True)
 print('Uploaded video and poster. Update the checked-in video metadata, use a PR, then deploy the app.')
if __name__=='__main__':main()
