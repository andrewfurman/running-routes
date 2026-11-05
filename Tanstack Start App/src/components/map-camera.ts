import type {Position} from './types'
import type {MapInsets} from './map-framing'
export interface Camera {lng:number;lat:number;zoom:number}
const world=(lng:number,lat:number):Position=>{const s=Math.sin(Math.max(-85.051129,Math.min(85.051129,lat))*Math.PI/180);return [(lng+180)/360,.5-Math.log((1+s)/(1-s))/(4*Math.PI)]}
const location=(x:number,y:number):Position=>[x*360-180,Math.atan(Math.sinh(Math.PI*(1-2*y)))*180/Math.PI]
/** Fit above overlays without a second, full-level zoom-out after fitting. */
export function cameraForPoints(points:Position[],width:number,height:number,padding:number|MapInsets,context=false):Camera|undefined{
 if(!points.length||width<=0||height<=0)return
 const p=typeof padding==='number'?{left:padding,right:padding,top:padding,bottom:padding}:padding
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity
 for(const [lng,lat] of points){const [x,y]=world(lng,lat);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y)}
 const zoom=Math.max(0,Math.min(context?16.5:17,Math.log2(Math.max(32,width-p.left-p.right)/(256*Math.max(1e-9,maxX-minX))),Math.log2(Math.max(32,height-p.top-p.bottom)/(256*Math.max(1e-9,maxY-minY))))-(context ? 0.2 : 0))
 const scale=256*2**zoom,[lng,lat]=location((minX+maxX)/2+(p.right-p.left)/(2*scale),(minY+maxY)/2+(p.bottom-p.top)/(2*scale))
 return {lng,lat,zoom}
}
export function cameraFrame(from:Camera,to:Camera,t:number):Camera{
 const progress=Math.max(0,Math.min(1,t)),ease=progress*progress*(3-2*progress),a=world(from.lng,from.lat),b=world(to.lng,to.lat)
 let dx=b[0]-a[0];if(dx>.5)dx-=1;else if(dx<-.5)dx+=1
 const [lng,lat]=location(a[0]+dx*ease,a[1]+(b[1]-a[1])*ease)
 return {lng:((lng+540)%360)-180,lat,zoom:from.zoom+(to.zoom-from.zoom)*ease-.12*Math.sin(Math.PI*progress)}
}
/** A new arrow click cancels the previous flight and starts at its current camera. */
export function createCameraFlight(read:()=>Camera,apply:(camera:Camera)=>void,raf:typeof requestAnimationFrame=requestAnimationFrame,cancelRaf:typeof cancelAnimationFrame=cancelAnimationFrame){
 let frame=0
 const cancel=()=>{if(frame)cancelRaf(frame);frame=0}
 return {cancel,fly(to:Camera,immediate=false){cancel();const from=read();if(immediate){apply(to);return}let start:number|undefined;const step=(now:number)=>{start??=now;const t=Math.min(1,(now-start)/720);apply(t===1?to:cameraFrame(from,to,t));if(t<1)frame=raf(step);else frame=0};frame=raf(step)}}
}
