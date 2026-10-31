// The Home Screen app's Refresh action must retrieve current HTML and hashed asset URLs.
export function freshDocument(response:Response){
 if(!response.headers.get('Content-Type')?.toLowerCase().includes('text/html'))return response
 const headers=new Headers(response.headers);headers.set('Cache-Control','no-store')
 return new Response(response.body,{status:response.status,statusText:response.statusText,headers})
}
