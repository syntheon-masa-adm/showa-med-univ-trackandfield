import urllib.request
import json
import os
from datetime import datetime, timezone, timedelta

# --- 1. 大会カウントダウンの計算（日本語版用） ---
meets = [
    { "date": "2026/05/02", "name": "M×Kディスタンストライアル" },
    { "date": "2026/05/16", "name": "M×Kディスタンストライアル" },
    { "date": "2026/06/06", "name": "MDPV陸上大会" },
    { "date": "2026/07/19", "name": "東コメ" },
    { "date": "2026/08/08", "name": "東医体" },
    { "date": "2026/08/29", "name": "全日本MDPV" },
    { "date": "2026/09/20", "name": "関東医" }
]

JST = timezone(timedelta(hours=+9), 'JST')
now_jst = datetime.now(JST)
today_midnight = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)

next_meet = None
days_left = 0

for meet in meets:
    meet_date = datetime.strptime(meet["date"], "%Y/%m/%d").replace(tzinfo=JST)
    if meet_date >= today_midnight:
        next_meet = meet
        meet_midnight = meet_date.replace(hour=0, minute=0, second=0, microsecond=0)
        days_left = (meet_midnight - today_midnight).days
        break

if next_meet:
    countdown_html = f"""
    <div id="event-name" class="countdown-target">{next_meet['name']}</div>
    <div>
        <span id="days-count" class="days-remaining">{days_left}</span>
        <span class="days-unit">DAYS LEFT</span>
    </div>
    """
else:
    countdown_html = """
    <div id="event-name" class="countdown-target">今シーズンの大会は終了しました</div>
    <div>
        <span id="days-count" class="days-remaining">0</span>
        <span class="days-unit">DAYS LEFT</span>
    </div>
    """

# --- 2. 練習予定の取得とHTML生成（日・英 同時作成） ---
url = "https://script.google.com/macros/s/AKfycbwJP2Ep80n7AdZrqYdgNlkdTpr2h41l6fqLT2pvXe1cxOzd3FR1rkhyhi7XcsXGIVx8/exec"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        practices = data.get('practices', [])
except Exception as e:
    practices = []

practice_html_jp = ""
practice_html_en = ""

# 英語翻訳用の辞書
translator_days = {"月": "MON", "火": "TUE", "水": "WED", "木": "THU", "金": "FRI", "土": "SAT", "日": "SUN"}
translator_locs = {
    "東大駒場": "UTokyo Komaba", "織田フィールド": "Oda Field", "織田": "Oda Field",
    "等々力競技場": "Todoroki Stadium", "等々力": "Todoroki Stadium", "大井競技場": "Oi Stadium",
    "大井": "Oi Stadium", "夢の島競技場": "Yumenoshima Stadium", "済美山": "Saibiyama Track",
    "大学グラウンド": "University Ground", "休み": "No Practice", "未定": "TBA"
}
color_styles = {
    "MON": "border-orange-400 text-orange-500",
    "WED": "border-blue-400 text-blue-500",
    "FRI": "border-red-400 text-red-500",
    "DEFAULT": "border-slate-400 text-slate-500"
}
month_abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

if not practices:
    practice_html_jp = '<div style="text-align: center; color: var(--text-muted); padding: 10px;">今後の練習予定は未登録です。</div>'
    practice_html_en = '<div class="col-span-full text-center py-4 text-slate-500">No upcoming practices scheduled at this time.</div>'
else:
    for p in practices:
        # 共通データ
        lat = p.get('lat', '')
        lon = p.get('lon', '')
        full_date = p.get('fullDateStr', '')
        time_str = p.get('time', '')
        display_time = "TBA" if time_str == "--:--" else time_str
        
        # --- 日本語版の生成 ---
        day_label = p.get('dayLabel', '')
        badge_class = 'mon'
        if day_label == '水': badge_class = 'wed'
        elif day_label == '金': badge_class = 'fri'

        station = p.get('station', '')
        station_html = f'<span class="day-station">{station}</span>' if station else '<span class="day-station" style="display:none;"></span>'
        
        practice_html_jp += f"""
        <div class="day-row practice-item" data-lat="{lat}" data-lon="{lon}" data-date="{full_date}" data-time="{time_str}">
            <div class="date-badge-container">
                <span class="practice-date">{p.get("displayDate", "")}</span>
                <span class="day-badge {badge_class}">{day_label}</span>
            </div>
            <div class="loc-time-container">
                <div class="loc-details">
                    <span class="day-loc">{p.get("location", "")}</span>
                    {station_html}
                </div>
                <div class="time-weather-container">
                    <span class="day-time">{time_str}</span>
                    <div class="weather-box" style="display:none;"></div>
                </div>
            </div>
        </div>
        """

        # --- 英語版の生成 ---
        en_day = translator_days.get(day_label, "DAY")
        
        jp_loc = p.get("location", "")
        en_loc = "TBA" if not jp_loc else jp_loc
        for jp_key, en_val in translator_locs.items():
            if jp_key in jp_loc:
                en_loc = en_val
                break
                
        # 日付を英語フォーマット（例: "May 2"）に変換
        jp_date = p.get("displayDate", "")
        en_date = jp_date
        if "/" in jp_date:
            parts = jp_date.split("/")
            if len(parts) == 2:
                en_date = f"{month_abbr[int(parts[0])-1]} {int(parts[1])}"

        color_class = color_styles.get(en_day, color_styles["DEFAULT"])
        border_color, text_color = color_class.split(' ')

        practice_html_en += f"""
        <div class="bg-white p-5 rounded-xl border-l-4 {border_color} shadow-sm transition hover:shadow-md flex flex-col justify-between practice-item" data-lat="{lat}" data-lon="{lon}" data-date="{full_date}" data-time="{time_str}">
            <div>
                <div class="flex justify-between items-start mb-1">
                    <span class="font-bold text-sm {text_color}">{en_day}</span>
                    <span class="text-xs font-medium text-slate-400">{en_date}</span>
                </div>
                <p class="font-black text-lg text-slate-800 leading-tight mb-2">{en_loc}</p>
            </div>
            <div class="flex items-center justify-between mt-2">
                <div class="flex items-center text-blue-600 font-bold">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    {display_time}
                </div>
                <div class="weather-box text-sm font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded hidden items-center gap-1"></div>
            </div>
        </div>
        """

# --- 3. テンプレートの結合と書き出し ---
# 日本語版
with open('template.html', 'r', encoding='utf-8') as f:
    template_jp = f.read()
final_html_jp = template_jp.replace('<!-- INJECT_COUNTDOWN_HERE -->', countdown_html)
final_html_jp = final_html_jp.replace('<!-- INJECT_PRACTICE_HERE -->', practice_html_jp)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html_jp)

# 英語版
if os.path.exists('english/template.html'):
    with open('english/template.html', 'r', encoding='utf-8') as f:
        template_en = f.read()
    final_html_en = template_en.replace('<!-- INJECT_EN_PRACTICE_HERE -->', practice_html_en)
    with open('english/index.html', 'w', encoding='utf-8') as f:
        f.write(final_html_en)
