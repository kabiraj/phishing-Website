from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flask import Flask, request, render_template_string
from predict import predict

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Phishing URL Detector</title>
<style>
body{font-family:Arial;max-width:850px;margin:40px auto;padding:20px}
input{width:75%;padding:12px}button{padding:12px 18px}
.card{margin-top:25px;padding:20px;border:1px solid #ddd;border-radius:10px}
.bad{font-weight:bold}.small{color:#666}
</style>
<h1>Phishing URL Detector</h1>
<p class="small">Offline lexical/structural analysis. The application does not fetch the submitted URL.</p>
<form method="post">
<input name="url" placeholder="https://example.com/login" required value="{{ url or '' }}">
<button>Analyse</button>
</form>
{% if result %}
<div class="card">
<h2>Prediction: {{ result.prediction }}</h2>
{% if result.trust_score is defined %}<p>Trust score: {{ result.trust_score }}/100</p>{% endif %}
<h3>Model probabilities</h3>
<ul>{% for k,v in result.probabilities.items() %}
<li>{{k}}: {{ "%.2f"|format(v*100) }}%</li>{% endfor %}</ul>
</div>
{% endif %}
"""

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    url = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if url:
            result = predict(url)
    return render_template_string(HTML, result=result, url=url)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
