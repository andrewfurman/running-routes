"""Shared navigation and an off-map Info dialog for the run and bike maps."""
import re
import json


def apply_map_shell(html: str, kind: str = 'run') -> str:
    info = []
    if kind == 'bike':
        match = re.search(r'<div class="summary">(?:<div>.*?</div>)+</div>', html, re.S)
        if not match:
            raise ValueError('Expected the bike summary statistics')
        stats = match[0]
        html = html[:match.start()] + html[match.end():]
    else:
        tracks = json.loads(re.search(r'const recentTracks=(.*);\n', html)[1])
        targets = json.loads(re.search(r'const targets=(.*);\n', html)[1])
        days = len({t['date'] for t in targets if not t.get('past') and t.get('one_way_miles') is not None})
        stats = '<div class="summary"><div><strong id="run-track-count">'+format(len(tracks['features']),',')+'</strong><span>GPS runs</span></div><div><strong id="planned-target-count">'+str(days)+'</strong><span>planned days</span></div></div>'
    patterns = [r'<div class="intro">.*?</div>', r'<div class="foot">.*?</div>',
                r'<details id="key-panel">.*?</details>'] if kind == 'run' else [
                    r'<div class="note small">.*?</div>']
    for pattern in patterns:
        def collect(match):
            info.append(match[0])
            return ''
        html = re.sub(pattern, collect, html, count=1, flags=re.S)
    html = re.sub(r'<dialog id="map-info".*?</dialog>', '', html, flags=re.S)
    html = re.sub(r'<style id="map-shell-style">.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script id="map-shell-script">.*?</script>', '', html, flags=re.S)
    # Preserve the selection hooks while removing the corner details overlay.
    if kind == 'run':
        html = re.sub(r'<details class="detail"><summary id="route-detail-summary">.*?</summary>(.*?)</details>', r'<section class="detail" hidden>\1</section>', html, count=1, flags=re.S)
        html = html.replace('<section class="detail">', '<section class="detail" hidden>', 1)
        if 'function targetWeekday(t)' not in html:
            html = html.replace('function targetVisible(t)', "function targetWeekday(t){return (t.display_date||t.date).split(' ')[0]}\nfunction targetVisible(t)", 1)
        html = html.replace("html:'<div class=\"map-pin\">'+t.number+'</div>',iconSize:[32,32],iconAnchor:[16,16]", "html:'<div class=\"map-pin\">'+targetWeekday(t)+'</div>',iconSize:[40,40],iconAnchor:[20,20]")
        html = html.replace("content.textContent=t.number;content.setAttribute('aria-label',t.street)", "content.textContent=targetWeekday(t);content.setAttribute('aria-label',targetWeekday(t)+' · '+t.street)")
    heading = re.search(r'<h1[^>]*>.*?</h1>', html, re.S)[0]
    nav = '<nav class="view-switch" aria-label="Map view">'
    for name, label, path in [('run', 'Runs', './index.html'), ('bike', 'Bikes', './bikes.html')]:
        current = ' aria-current="page"' if kind == name else ''
        nav += f'<a href="{path}"{current}>{label}</a>'
    nav += '</nav>'
    header = '<header class="map-header"><div class="map-overview">'+nav+'<div class="header-stats">'+stats+'</div></div>'+heading+'<button id="toggle-route-list" aria-expanded="false">'+('Routes' if kind == 'run' else 'Rides')+'</button><button id="open-map-info" aria-haspopup="dialog">Info</button></header>'
    html = re.sub(r'<header>.*?</header>|<header class="map-header">.*?</header>', lambda _: header, html, count=1, flags=re.S)
    title = 'Running map info' if kind == 'run' else 'Bike map info'
    dialog = '<dialog id="map-info" aria-labelledby="map-info-title"><div class="info-header"><h2 id="map-info-title">'+title+'</h2><button id="close-map-info" aria-label="Close Info">Close</button></div><div class="info-content">'+''.join(info)+'</div></dialog>'
    style = '''<style id="map-shell-style">
[hidden]{display:none!important}.map-pin{width:40px!important;height:40px!important;line-height:34px!important;font-size:10px!important;border-radius:50%!important}.map-overview{display:flex;align-items:center;gap:22px;flex-shrink:0}.header-stats .summary{display:flex;align-items:center;gap:19px;padding:0;background:transparent;flex-wrap:wrap}.header-stats .summary>div{display:flex;flex-direction:column;gap:1px}.header-stats .summary strong{font-size:18px;line-height:1.25;color:#472569;font-weight:750}.header-stats .summary span{font-size:11px;color:#756b80;white-space:nowrap}.header-stats #years-label{font-size:12px}@media(max-width:1100px){.map-overview{flex-wrap:wrap;gap:10px}.header-stats .summary{gap:12px}}
.map-header{display:flex;align-items:center;gap:24px;padding:15px 24px;background:#fff;border-bottom:1px solid #e4ddec}.map-header h1{flex:1;font-size:20px;line-height:1.3;margin:0}.view-switch{display:inline-flex;padding:4px;background:#f0ebf6;border:1px solid #e0d6ed;border-radius:13px;gap:3px;flex-shrink:0}.view-switch a{padding:9px 21px;border-radius:9px;font-weight:700;text-decoration:none;color:#62576e}.view-switch a[aria-current=page]{background:#693db1;color:#fff;box-shadow:0 2px 5px #39205724}.view-switch a:hover{background:#e4daf1}.view-switch a[aria-current=page]:hover{background:#583095}#open-map-info,#close-map-info{border:1px solid #d7cce3;background:#fff;color:#51376d;padding:9px 17px;border-radius:9px;font:inherit;cursor:pointer}a:focus-visible,button:focus-visible{outline:3px solid #a987dc;outline-offset:3px}#map-info{border:1px solid #ded5e8;border-radius:16px;padding:24px;max-width:740px;width:calc(100% - 36px);max-height:85vh;color:#292136;box-shadow:0 20px 80px #25153c40}#map-info::backdrop{background:#1a112c80;backdrop-filter:blur(3px)}.info-header{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px}.info-header h2{margin:0;font-size:21px}.info-content .intro{padding:16px 20px;border:1px solid #ecdeb8;border-radius:10px}.info-content .foot,.info-content .note{padding:14px 0}.info-content details{margin-top:12px}@media(max-width:760px){.map-header{flex-wrap:wrap;gap:12px;padding:12px 16px}.map-header h1{order:3;flex-basis:100%;font-size:18px}#open-map-info{margin-left:auto}}
body{height:100dvh;overflow:hidden;display:flex;flex-direction:column}.map-header{flex-shrink:0;padding:10px 18px;gap:16px}.layout{position:relative;display:block;flex:1;min-height:0;padding:0;margin:0}.layout>main{height:100%;display:flex;flex-direction:column;min-height:0}.layout>aside{display:none;position:absolute;left:12px;top:62px;bottom:54px;width:280px;padding:12px;background:#fffefa;box-shadow:0 8px 32px #25153c30;border:1px solid #ded5e8;border-radius:12px;z-index:3;overflow:auto}.routes-open .layout>aside{display:block}.cards{display:block;max-height:none;padding:0;overflow:visible}.card{min-width:0}.toolbar{flex-shrink:0;justify-content:flex-start;padding:8px 14px;gap:10px;margin:0;border-bottom:1px solid #ded5e8;background:white}.toolbar label{white-space:nowrap}#map{height:auto!important;min-height:0!important;width:100%;flex:1;border:0;border-radius:0}.detail{position:absolute;right:12px;bottom:12px;width:min(470px,calc(100% - 24px));max-height:34vh;overflow:auto;padding:10px 14px;margin:0;border:1px solid #d6cce2;box-shadow:0 3px 18px #25153c22;background:white;z-index:2;border-radius:10px}.detail summary{font-weight:650;cursor:pointer}.detail h2{margin-top:10px}.detail .actions{margin-top:8px}#toggle-route-list{border:1px solid #d7cce3;background:#fff;color:#51376d;padding:9px 17px;border-radius:9px;font:inherit;cursor:pointer}#toggle-route-list[aria-expanded=true]{background:#eee5fc}@media(max-width:800px){.layout{padding:0}.layout>aside{top:92px;width:min(280px,calc(100% - 24px))}.map-header{gap:8px;padding:8px 12px}.map-overview{gap:10px}.header-stats .summary{gap:10px}.toolbar{font-size:12px;gap:6px;padding:6px}.toolbar button,.toolbar select{padding:5px}.detail{max-height:35vh}.cards{margin:0}.card{min-width:0}#open-map-info{margin-left:0}.map-header h1{font-size:15px}}
</style>'''
    script = '''<script id="map-shell-script">
const routeListToggle=document.querySelector('#toggle-route-list');
routeListToggle.onclick=()=>{const open=document.body.classList.toggle('routes-open');routeListToggle.setAttribute('aria-expanded',String(open));};
const routeDetailTitle=document.querySelector('#detail-title'),routeDetailSummary=document.querySelector('#route-detail-summary');
if(routeDetailTitle&&routeDetailSummary){const update=()=>routeDetailSummary.textContent=routeDetailTitle.textContent+' · Details';update();new MutationObserver(update).observe(routeDetailTitle,{childList:true,subtree:true,characterData:true});}
document.querySelector('#open-map-info').onclick=()=>document.querySelector('#map-info').showModal();
document.querySelector('#close-map-info').onclick=()=>document.querySelector('#map-info').close();
</script>'''
    # The original map script binds controls inside Info while parsing, so
    # place the dialog before those scripts, not after them.
    html = html.replace('<script', dialog+'<script', 1)
    return html.replace('</head>', style+'</head>').replace('</body>', script+'</body>')
