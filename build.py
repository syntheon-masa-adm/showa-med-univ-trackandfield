import urllib.request
import json

# 1. データの取得（GASから）
url = "https://script.google.com/macros/s/AKfycbwJP2Ep80n7AdZrqYdgNlkdTpr2h41l6fqLT2pvXe1cxOzd3FR1rkhyhi7XcsXGIVx8/exec"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        practices = data.get('practices', [])
except Exception as e:
    practices = []

# 2. HTML要素の完全な生成
html_content = ""
if not practices:
    html_content = '<div style="text-align: center; color: var(--text-muted); padding: 10px;">今後の練習予定は未登録です。</div>'
else:
    for p in practices:
        # 曜日に応じたバッジの色の判定
        day_label = p.get('dayLabel', '')
        badge_class = 'mon'
        if day_label == '水':
            badge_class = 'wed'
        elif day_label == '金':
            badge_class = 'fri'

        # 駅情報の判定
        station = p.get('station', '')
        if station:
            station_html = f'<span class="day-station">{station}</span>'
        else:
            station_html = '<span class="day-station" style="display:none;"></span>'

        # 元のデザイン（CSS）を適用するための完全なHTML構造
        html_content += f"""
        <div class="day-row">
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
                    <span class="day-time">{p.get("time", "")}</span>
                </div>
            </div>
        </div>
        """

# 3. テンプレートの読み込みと置換
with open('template.html', 'r', encoding='utf-8') as f:
    template = f.read()

final_html = template.replace('', html_content)

# 4. index.html として書き出し
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)
