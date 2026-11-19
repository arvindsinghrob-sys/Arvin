import os
import time
import requests
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# Environment Variables (Render Dashboard में सेट किए गए)
FIREBASE_DB_URL = os.environ.get(
    "FIREBASE_DB_URL",
    "https://vova-733e8-default-rtdb.firebaseio.com"
).rstrip("/")

BOT_TOKEN = os.environ.get("9178448206:AAEziLPCU85WI4bDgKQ9mdAkAnO4tboBLbM", "")
ADMIN_CHAT_ID = os.environ.get("6398769189", "")

# Amazon-स्टाइल प्रोफेशनल प्रोडक्ट लिस्ट
PRODUCTS = [
    {
        "id": 1,
        "name": "Nova Smartphone Pro Max (256GB, Titanium)",
        "price": 54999,
        "mrp": 64999,
        "category": "Mobiles",
        "rating": 4.7,
        "reviews": 1420,
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=500&q=80",
        "badge": "Best Seller"
    },
    {
        "id": 2,
        "name": "Wireless ANC Earbuds with 40H Playtime",
        "price": 1999,
        "mrp": 3999,
        "category": "Accessories",
        "rating": 4.4,
        "reviews": 890,
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=500&q=80",
        "badge": "Deal of the Day"
    },
    {
        "id": 3,
        "name": "AMOLED Smart Watch with Bluetooth Calling",
        "price": 2799,
        "mrp": 5999,
        "category": "Wearables",
        "rating": 4.5,
        "reviews": 2150,
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=500&q=80",
        "badge": "Top Rated"
    },
    {
        "id": 4,
        "name": "UltraBook Pro 14\" Laptop (16GB RAM, 512GB SSD)",
        "price": 49999,
        "mrp": 62000,
        "category": "Computers",
        "rating": 4.6,
        "reviews": 640,
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=500&q=80",
        "badge": "Amazon's Choice"
    },
    {
        "id": 5,
        "name": "4K Ultra HD Mirrorless Camera Kit",
        "price": 42500,
        "mrp": 51000,
        "category": "Electronics",
        "rating": 4.8,
        "reviews": 320,
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=500&q=80",
        "badge": "Limited Deal"
    },
    {
        "id": 6,
        "name": "Mechanical RGB Gaming Keyboard & Mouse Combo",
        "price": 2499,
        "mrp": 4499,
        "category": "Accessories",
        "rating": 4.3,
        "reviews": 1120,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=500&q=80",
        "badge": "Trending"
    }
]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaCart.in : Online Shopping for Electronics, Mobiles & More</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
        body { background-color: #EAEDED; color: #0F1111; }

        /* Amazon Style Navbar */
        .navbar { background-color: #131921; color: white; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; gap: 15px; position: sticky; top: 0; z-index: 1000; flex-wrap: wrap; }
        .logo { font-size: 24px; font-weight: bold; color: white; text-decoration: none; display: flex; align-items: center; }
        .logo span { color: #FF9900; }
        .search-bar { flex: 1; min-width: 240px; display: flex; max-width: 700px; }
        .search-bar input { width: 100%; padding: 10px 14px; border: none; border-radius: 4px 0 0 4px; font-size: 15px; outline: none; }
        .search-bar button { background-color: #FEBD69; border: none; padding: 0 18px; border-radius: 0 4px 4px 0; cursor: pointer; font-weight: bold; font-size: 16px; }
        .search-bar button:hover { background-color: #F3A847; }
        .cart-btn { background: none; border: 1px solid transparent; color: white; cursor: pointer; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 4px; font-weight: bold; font-size: 15px; }
        .cart-btn:hover { border-color: white; }
        .cart-count { background-color: #FF9900; color: #131921; padding: 2px 8px; border-radius: 12px; font-size: 14px; font-weight: 800; }

        /* Sub Navbar Categories */
        .sub-nav { background-color: #232F3E; padding: 8px 20px; display: flex; gap: 15px; overflow-x: auto; }
        .cat-btn { background: none; border: 1px solid transparent; color: white; padding: 5px 10px; cursor: pointer; font-size: 14px; border-radius: 3px; white-space: nowrap; }
        .cat-btn:hover, .cat-btn.active { border-color: white; background-color: #37475A; }

        /* Hero Banner */
        .hero { background: linear-gradient(135deg, #232F3E 0%, #37475A 60%, #FF9900 160%); color: white; padding: 35px 25px; text-align: center; margin-bottom: 20px; }
        .hero h1 { font-size: 28px; margin-bottom: 8px; }
        .hero p { font-size: 15px; color: #DDD; }

        /* Product Grid */
        .container { max-width: 1300px; margin: 0 auto; padding: 0 15px 40px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 6px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .badge { background-color: #CC0C39; color: white; font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 2px; align-self: flex-start; margin-bottom: 10px; }
        .card img { width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px; }
        .card h3 { font-size: 16px; font-weight: 600; margin-bottom: 6px; line-height: 1.3; color: #0F1111; }
        .rating { color: #FFA41C; font-size: 14px; margin-bottom: 8px; }
        .rating span { color: #007185; font-size: 13px; }
        .price-box { margin-bottom: 12px; }
        .price { font-size: 22px; font-weight: 700; color: #0F1111; }
        .mrp { font-size: 13px; color: #565959; text-decoration: line-through; margin-left: 6px; }
        .discount { color: #CC0C39; font-size: 13px; font-weight: 600; margin-left: 6px; }
        .delivery { font-size: 12px; color: #565959; margin-bottom: 14px; }
        .add-btn { background-color: #FFD814; border: 1px solid #FCD200; border-radius: 20px; padding: 9px; font-size: 14px; font-weight: 600; cursor: pointer; width: 100%; }
        .add-btn:hover { background-color: #F7CA00; }

        /* Cart & Checkout Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; justify-content: center; align-items: center; padding: 15px; }
        .modal-content { background: white; width: 100%; max-width: 520px; border-radius: 8px; padding: 20px; max-height: 90vh; overflow-y: auto; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #DDD; padding-bottom: 10px; margin-bottom: 15px; }
        .close-btn { font-size: 24px; cursor: pointer; border: none; background: none; }
        .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #EEE; gap: 10px; }
        .qty-controls button { padding: 2px 8px; border: 1px solid #CCC; background: #F0F2F2; cursor: pointer; border-radius: 4px; }
        .form-group { margin-top: 12px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
        .form-group input, .form-group textarea { width: 100%; padding: 9px; border: 1px solid #888C8C; border-radius: 4px; font-size: 14px; }
        .checkout-btn { background-color: #FFA41C; border: 1px solid #FF8F00; border-radius: 20px; padding: 11px; width: 100%; font-size: 15px; font-weight: bold; cursor: pointer; margin-top: 16px; }
        .checkout-btn:hover { background-color: #FA8900; }
        .status-msg { margin-top: 12px; padding: 10px; border-radius: 4px; font-size: 14px; display: none; }
        .success { background-color: #DFF0D8; color: #3C763D; border: 1px solid #D6E9C6; }
        .error { background-color: #F2DEDE; color: #A94442; border: 1px solid #EBCCD1; }
    </style>
</head>
<body>

    <nav class="navbar">
        <a href="#" class="logo">Nova<span>Cart</span>.in</a>
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Search NovaCart.in for mobiles, laptops, watches..." onkeyup="filterProducts()">
            <button onclick="filterProducts()">🔍</button>
        </div>
        <button class="cart-btn" onclick="openCart()">
            🛒 Cart <span class="cart-count" id="cartCount">0</span>
        </button>
    </nav>

    <div class="sub-nav">
        <button class="cat-btn active" onclick="setCategory('All', this)">All Products</button>
        <button class="cat-btn" onclick="setCategory('Mobiles', this)">Mobiles</button>
        <button class="cat-btn" onclick="setCategory('Computers', this)">Computers</button>
        <button class="cat-btn" onclick="setCategory('Accessories', this)">Accessories</button>
        <button class="cat-btn" onclick="setCategory('Wearables', this)">Wearables</button>
        <button class="cat-btn" onclick="setCategory('Electronics', this)">Electronics</button>
    </div>

    <div class="hero">
        <h1>Great Indian Tech & Gadget Festival</h1>
        <p>Up to 50% Off on Top Electronics | Free Fast Delivery | Cash on Delivery Available</p>
    </div>

    <div class="container">
        <div class="grid" id="productGrid"></div>
    </div>

    <!-- Shopping Cart & Order Modal -->
    <div class="modal" id="cartModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Shopping Cart & Checkout</h2>
                <button class="close-btn" onclick="closeCart()">&times;</button>
            </div>
            <div id="cartItems"></div>
            <h3 style="margin-top: 15px; text-align: right;">Subtotal: ₹<span id="cartTotal">0</span></h3>

            <form id="orderForm" onsubmit="placeOrder(event)">
                <div class="form-group">
                    <label>Full Name *</label>
                    <input type="text" id="custName" required placeholder="Enter your full name">
                </div>
                <div class="form-group">
                    <label>Mobile Number *</label>
                    <input type="tel" id="custPhone" required placeholder="10-digit mobile number">
                </div>
                <div class="form-group">
                    <label>Full Delivery Address *</label>
                    <textarea id="custAddress" rows="2" required placeholder="House No, Street, City, Pincode"></textarea>
                </div>
                <button type="submit" class="checkout-btn" id="submitBtn">Place Your Order (Cash on Delivery)</button>
            </form>
            <div id="statusMsg" class="status-msg"></div>
        </div>
    </div>

    <script>
        const products = {{ products | tojson }};
        let cart = [];
        let selectedCategory = 'All';

        function renderProducts() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const grid = document.getElementById('productGrid');
            grid.innerHTML = '';

            const filtered = products.filter(p => {
                const matchCat = selectedCategory === 'All' || p.category === selectedCategory;
                const matchSearch = p.name.toLowerCase().includes(search) || p.category.toLowerCase().includes(search);
                return matchCat && matchSearch;
            });

            filtered.forEach(p => {
                const disc = Math.round(((p.mrp - p.price) / p.mrp) * 100);
                grid.innerHTML += `
                    <div class="card">
                        <div>
                            <div class="badge">${p.badge}</div>
                            <img src="${p.image}" alt="${p.name}">
                            <h3>${p.name}</h3>
                            <div class="rating">★★★★☆ <span>(${p.reviews})</span></div>
                            <div class="price-box">
                                <span class="price">₹${p.price.toLocaleString('en-IN')}</span>
                                <span class="mrp">₹${p.mrp.toLocaleString('en-IN')}</span>
                                <span class="discount">(${disc}% off)</span>
                            </div>
                            <div class="delivery">FREE Delivery by <b>Tomorrow</b></div>
                        </div>
                        <button class="add-btn" onclick="addToCart(${p.id})">Add to Cart</button>
                    </div>
                `;
            });
        }

        function setCategory(cat, btn) {
            selectedCategory = cat;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderProducts();
        }

        function filterProducts() {
            renderProducts();
        }

        function addToCart(id) {
            const existing = cart.find(item => item.id === id);
            if (existing) {
                existing.qty += 1;
            } else {
                const prod = products.find(p => p.id === id);
                cart.push({ ...prod, qty: 1 });
            }
            updateCartUI();
        }

        function changeQty(id, delta) {
            const idx = cart.findIndex(item => item.id === id);
            if (idx > -1) {
                cart[idx].qty += delta;
                if (cart[idx].qty <= 0) cart.splice(idx, 1);
            }
            updateCartUI();
        }

        function updateCartUI() {
            const count = cart.reduce((sum, item) => sum + item.qty, 0);
            document.getElementById('cartCount').innerText = count;

            const itemsDiv = document.getElementById('cartItems');
            if (cart.length === 0) {
                itemsDiv.innerHTML = '<p style="color:#666; padding:10px 0;">Your NovaCart is empty.</p>';
                document.getElementById('cartTotal').innerText = '0';
                return;
            }

            let total = 0;
            itemsDiv.innerHTML = '';
            cart.forEach(item => {
                total += item.price * item.qty;
                itemsDiv.innerHTML += `
                    <div class="cart-item">
                        <div style="flex:1;">
                            <div style="font-weight:600; font-size:14px;">${item.name}</div>
                            <div style="color:#B12704; font-weight:bold;">₹${item.price.toLocaleString('en-IN')}</div>
                        </div>
                        <div class="qty-controls">
                            <button onclick="changeQty(${item.id}, -1)">-</button>
                            <span style="margin:0 8px;">${item.qty}</span>
                            <button onclick="changeQty(${item.id}, 1)">+</button>
                        </div>
                    </div>
                `;
            });
            document.getElementById('cartTotal').innerText = total.toLocaleString('en-IN');
        }

        function openCart() {
            updateCartUI();
            document.getElementById('statusMsg').style.display = 'none';
            document.getElementById('cartModal').style.display = 'flex';
        }

        function closeCart() {
            document.getElementById('cartModal').style.display = 'none';
        }

        async function placeOrder(e) {
            e.preventDefault();
            if (cart.length === 0) {
                alert("Please add at least one item to your cart!");
                return;
            }

            const btn = document.getElementById('submitBtn');
            const statusDiv = document.getElementById('statusMsg');
            btn.disabled = true;
            btn.innerText = "Placing Order...";

            const payload = {
                name: document.getElementById('custName').value,
                phone: document.getElementById('custPhone').value,
                address: document.getElementById('custAddress').value,
                items: cart.map(i => `${i.name} (x${i.qty})`),
                total: cart.reduce((sum, i) => sum + i.price * i.qty, 0)
            };

            try {
                const res = await fetch('/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                statusDiv.style.display = 'block';
                if (data.success) {
                    statusDiv.className = 'status-msg success';
                    statusDiv.innerText = "✅ Order Placed Successfully! Order details sent to Admin.";
                    cart = [];
                    updateCartUI();
                    document.getElementById('orderForm').reset();
                } else {
                    statusDiv.className = 'status-msg error';
                    statusDiv.innerText = "❌ Error: " + (data.error || "Failed to place order");
                }
            } catch (err) {
                statusDiv.style.display = 'block';
                statusDiv.className = 'status-msg error';
                statusDiv.innerText = "❌ Network error while placing order.";
            } finally {
                btn.disabled = false;
                btn.innerText = "Place Your Order (Cash on Delivery)";
            }
        }

        renderProducts();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, products=PRODUCTS)

@app.route("/order", methods=["POST"])
def order():
    data = request.get_json() or {}
    name = data.get("name", "Unknown")
    phone = data.get("phone", "N/A")
    address = data.get("address", "N/A")
    items = data.get("items", [])
    total = data.get("total", 0)

    order_record = {
        "name": name,
        "phone": phone,
        "address": address,
        "items": items,
        "total": total,
        "timestamp": int(time.time())
    }

    # 1. Save to Firebase Realtime Database
    try:
        if FIREBASE_DB_URL:
            requests.post(f"{FIREBASE_DB_URL}/orders.json", json=order_record, timeout=5)
    except Exception as e:
        print("Firebase Error:", e)

    # 2. Send Notification to Telegram Bot
    tg_status = "Skipped"
    if BOT_TOKEN and ADMIN_CHAT_ID:
        items_text = "\n".join([f"• {i}" for i in items])
        msg = (
            f"🛍️ *New Order on NovaCart!*\n\n"
            f"👤 *Customer:* {name}\n"
            f"📞 *Phone:* {phone}\n"
            f"📍 *Address:* {address}\n\n"
            f"📦 *Items:*\n{items_text}\n\n"
            f"💰 *Total Amount:* ₹{total}"
        )
        try:
            tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            resp = requests.post(
                tg_url,
                json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
                timeout=5
            )
            tg_status = resp.text
            print("Telegram Response:", tg_status)
        except Exception as e:
            print("Telegram Error:", e)

    return jsonify({"success": True, "telegram": tg_status})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
