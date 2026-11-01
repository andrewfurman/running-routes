"""Derive only timing and bass energy, never store audio in the public catalog."""
import argparse,array,hashlib,json,math,subprocess
from pathlib import Path
import imageio_ffmpeg

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('audio',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--drop-at',type=float,default=23.44);ap.add_argument('--reference-url',required=True);args=ap.parse_args()
 data=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(args.audio),'-af','lowpass=f=140','-ac','1','-ar','2000','-f','f32le','-'],stdout=subprocess.PIPE,check=True).stdout
 samples=array.array('f');samples.frombytes(data);levels=[math.sqrt(sum(x*x for x in samples[i:i+20])/20) for i in range(0,len(samples)-20,20)]
 ceiling=max(levels) or 1
 # Accent attack rather than sustained bass; fixed gain and short decay.
 pulses=[];prev=0;value=0
 for level in levels:
  attack=max(0,level-prev)/ceiling;value=max(attack*5,value*.8);pulses.append(round(min(1,value),3));prev=level
 output={'reference':'Travis Scott - FE!N (Official Audio) ft. Playboi Carti','referenceUrl':args.reference_url,'referenceAudioSha256':hashlib.sha256(args.audio.read_bytes()).hexdigest(),'songStartSeconds':0,'dropSeconds':args.drop_at,'sampleRate':100,'pulse':pulses,'note':'Timing-only analysis of a private opening excerpt; no audio, lyrics or waveform samples are included.'}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,separators=(',',':'))+'\n');print('Saved timing cues:',args.drop_at,'seconds; duration',len(pulses)/100)
if __name__=='__main__':main()
