export interface MapInsets {top:number;right:number;bottom:number;left:number}
/** Keep the selected route in the map area above the floating history card. */
export function activityMapInsets(width:number,height:number,dockTop?:number):MapInsets {
 const side=Math.min(60,Math.max(24,width*.08))
 const bottom=dockTop===undefined?side:Math.max(side,height-dockTop+side)
 return {top:side,right:side,bottom:Math.min(bottom,Math.max(side,height-side-120)),left:side}
}
