import urllib.request, json, os, re
from datetime import datetime, timezone, timedelta

# データ取得
GAS_URL = "https://script.google.com/macros/s/AKfycbwJP2Ep80n7AdZrqYdgNlkdTpr2h41l6fqLT2pvXe1cxOzd3FR1rkhyhi7XcsXGIVx8/exec"
practices = []
try:
    with urllib.request.urlopen(GAS_URL) as res:
        practices = json.loads(res.read().decode('utf-8')).get('practices', [])
except: pass

# カウントダウン計算
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
meets = [{"date": "2026/05/02", "name": "M×Kディスタンス"}, {"date": "2026/05/16", "name": "M×Kディスタンス"}, {"date": "2026/06/06", "name": "MDPV"}, {"date": "2026/07/19", "name": "東コメ"}, {"date": "2026/08/08", "name": "東医体"}, {"date": "2026/08/29", "name": "全日本MDPV"}, {"date": "2026/09/20", "name": "関東医"}]
next_m = next((m for m in meets if datetime.strptime(m["date"], "%Y/%m/%d").replace(tzinfo=JST) >= now.replace(hour=0,minute=0,second=0,microsecond=0)), None)
c_html = f'<div class="countdown-target">{next_m["name"]}</div><div><span class="days-remaining">{(datetime.strptime(next_m["date"], "%Y/%m/%d").replace(tzinfo=JST) - now.replace(hour=0,minute=0,second=0,microsecond=0)).days}</span><span class="days-unit">DAYS LEFT</span></div>' if next_m else '<div class="countdown-target">Season Ended</div>'

# HTML生成
jp_html = ""
en_html = ""
d_map = {"月":"MON","火":"TUE","水":"WED","木":"THU","金":"FRI","土":"SAT","日":"SUN"}
l_map = {"東大":"UTokyo","織田":"Oda Field","等々力":"Todoroki","大井":"Oi Stadium","済美山":"Saibiyama","大学":"Uni Ground"}

for p in practices:
    day = p.get('dayLabel','')
    en_day = d_map.get(day, "DAY")
    cls = "mon" if en_day=="MON" else "wed" if en_day=="WED" else "fri" if en_day=="FRI" else "mon"
    loc = p.get('location','')
    en_loc = next((v for k,v in l_map.items() if k in loc), "TBA")
    
    # JP
    jp_html += f'<div class="day-row practice-item" data-lat="{p.get("lat","")}" data-lon="{p.get("lon","")}" data-date="{p.get("fullDateStr","")}" data-time="{p.get("time","")}"><div class="date-badge-container"><span class="practice-date">{p.get("displayDate","")}</span><span class="day-badge {cls}">{day}</span></div><div class="loc-time-container"><div class="loc-details"><span class="day-loc">{loc}</span><span class="day-station">{p.get("station","")}</span></div><div class="time-weather-container"><span class="day-time">{p.get("time","")}</span><div class="weather-box" style="display:none;"></div></div></div></div>'
    
    # EN
    en_html += f'<div class="bg-white p-5 rounded-xl border-l-4 shadow-sm practice-item" data-lat="{p.get("lat","")}" data-lon="{p.get("lon","")}" data-date="{p.get("fullDateStr","")}" data-time="{p.get("time","")}"><div class="flex justify-between items-start mb-1"><span class="font-bold text-sm">{en_day}</span><span class="text-xs text-slate-400">{p.get("displayDate","")}</span></div><p class="font-black text-slate-800 mb-2">{en_loc}</p><div class="flex items-center justify-between mt-2"><div class="text-blue-600 font-bold">{p.get("time","")}</div><div class="weather-box text-xs font-bold bg-slate-100 px-2 py-1 rounded hidden"></div></div></div>'

# 書き出し
def bake(t, o, c, p, marker):
    if not os.path.exists(t): return
    with open(t,'r',encoding='utf-8') as f: content = f.read()
    content = re.sub(r'<!--\s*INJECT_COUNTDOWN_HERE\s*-->', c, content)
    content = re.sub(fr'<!--\s*{marker}\s*-->', p, content)
    with open(o,'w',encoding='utf-8') as f: f.write(content)

bake('template.html', 'index.html', c_html, jp_html, 'INJECT_PRACTICE_HERE')
os.makedirs('english', exist_ok=True)
bake('english/template.html', 'english/index.html', '', en_html, 'INJECT_EN_PRACTICE_HERE')
