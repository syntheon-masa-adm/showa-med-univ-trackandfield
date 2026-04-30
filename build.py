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

# 2. HTML要素の生成
html_content = ""
if not practices:
    html_content = '<div style="text-align: center; padding: 10px;">今後の練習予定は未登録です。</div>'
else:
    for p in practices:
        # ※ここに本来はJSONからHTMLタグを組み立てる処理が入る（今回は簡略化のモックアップ）
        html_content += f'<div class="day-row"><span class="practice-date">{p.get("displayDate", "")}</span> <span class="day-loc">{p.get("location", "")}</span></div>'

# 3. テンプレートの読み込みと置換
with open('template.html', 'r', encoding='utf-8') as f:
    template = f.read()

# 目印の部分を、生成したHTMLに置き換える
final_html = template.replace('<!-- INJECT_PRACTICE_HERE -->', html_content)

# 4. index.html として書き出し（これがクローラーに読まれる実体となる）
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)
