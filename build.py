import urllib.request
import json
from datetime import datetime, timezone, timedelta

# --- 1. 大会カウントダウンの計算 ---
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

# --- 2. 練習予定の取得とHTML生成 ---
url = "https://script.google.com/macros/s/AKfycbwJP2Ep80n7AdZrqYdgNlkdTpr2h41l6fqLT2pvXe1cxOzd3FR1rkhyhi7XcsXGIVx8/exec"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        practices = data.get('practices', [])
except Exception as e:
    practices = []

practice_html = ""
if not practices:
    practice_html = '<div style="text-align: center; color: var(--text-muted); padding: 10px;">今後の練習予定は未登録です。</div>'
else:
    for p in practices:
        day_label = p.get('dayLabel', '')
        badge_class = 'mon'
        if day_label == '水': badge_class = 'wed'
        elif day_label == '金': badge_class = 'fri'

        station = p.get('station', '')
        station_html = f'<span class="day-station">{station}</span>' if station else '<span class="day-station" style="display:none;"></span>'
        
        # JSに渡すためのデータ属性を取得
        lat = p.get('lat', '')
        lon = p.get('lon', '')
        full_date = p.get('fullDateStr', '')
        time_str = p.get('time', '')

        # classに"practice-item"を、カスタム属性として座標等を追加
        practice_html += f"""
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

# --- 3. テンプレートの結合と書き出し ---
with open('template.html', 'r', encoding='utf-8') as f:
    template = f.read()

final_html = template.replace('', countdown_html)
final_html = final_html.replace('', practice_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)
