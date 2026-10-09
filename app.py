from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3, os

app = Flask(__name__)
app.secret_key = "shanon-secret-123"

# Create DB
def init_db():
    conn = sqlite3.connect('shanon.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms
                 (id INTEGER PRIMARY KEY, room_no TEXT, type TEXT, price TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tenants
                 (id INTEGER PRIMARY KEY, name TEXT, room_no TEXT, phone TEXT)''')
    # Add demo rooms if empty
    c.execute("SELECT COUNT(*) FROM rooms")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO rooms VALUES (1,'A01','Single Room','Ksh 5,000','Available')")
        c.execute("INSERT INTO rooms VALUES (2,'A02','Double Room','Ksh 6,000','Occupied')")
        c.execute("INSERT INTO rooms VALUES (3,'B01','Bedsitter','Ksh 8,500','Available')")
        c.execute("INSERT INTO rooms VALUES (4,'B02','Premium Ensuite','Ksh 12,000','Available')")
    conn.commit()
    conn.close()

init_db()

# HTML TEMPLATE
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHANON HOSTELS</title>
<style>
body{font-family:Arial;margin:0;background:#f4f6f9}
.header{background:#0d1b2a;color:white;padding:15px;text-align:center}
.nav{background:#1b3a5f;padding:10px;text-align:center}
.nav a{color:white;margin:10px;text-decoration:none;font-weight:bold}
.card{background:white;margin:15px;padding:15px;border-radius:10px;box-shadow:0 2px 5px #ccc}
.btn{background:#1b3a5f;color:white;padding:10px 15px;border:none;border-radius:5px;text-decoration:none;display:inline-block;margin-top:10px}
.room-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
@media(max-width:700px){.room-grid{grid-template-columns:1fr}}
.room-img{width:100%;height:180px;object-fit:cover;border-radius:10px}
.price{color:green;font-weight:bold;font-size:18px}
</style>
</head>
<body>
<div class="header"><h1>🏨 SHANON HOSTELS</h1><p>Lwanda, Kakamega - 0799814706</p></div>
<div class="nav">
<a href="/">Home</a>
<a href="/rooms">Our Rooms 📸</a>
<a href="/dashboard">Admin</a>
<a href="/logout">Logout</a>
</div>
{{content}}
</body>
</html>
"""

ROOMS_HTML = """
<div class="card"><h2>Our Rooms - Choose Your Comfort</h2><p>Best student hostels in Western Kenya</p></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:15px">
  <div class="card">
    <img class="room-img" src="https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=500">
    <h3>Single Room</h3><p class="price">Ksh 5,000 / month</p><p>Private, desk, wardrobe, WiFi</p>
    <a class="btn" href="https://wa.me/254799814706?text=Hi, I want Single Room A01">Book on WhatsApp</a>
  </div>
  <div class="card">
    <img class="room-img" src="https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?w=500">
    <h3>Double Room (2 Sharing)</h3><p class="price">Ksh 6,000 / month per person</p><p>2 beds, 2 desks, spacious</p>
    <a class="btn" href="https://wa.me/254799814706?text=Hi, I want Double Room">Book on WhatsApp</a>
  </div>
  <div class="card">
    <img class="room-img" src="https://images.unsplash.com/photo-1554995207-c18c203602cb?w=500">
    <h3>Bedsitter Self-Contained</h3><p class="price">Ksh 8,500 / month</p><p>Own kitchen, sink, cooking allowed</p>
    <a class="btn" href="https://wa.me/254799814706?text=Hi, I want Bedsitter">Book on WhatsApp</a>
  </div>
  <div class="card">
    <img class="room-img" src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=500">
    <h3>Premium Ensuite - Like Qwetu</h3><p class="price">Ksh 12,000 / month</p><p>Private bathroom, hot shower, AC, balcony</p>
    <a class="btn" href="https://wa.me/254799814706?text=Hi, I want Premium Ensuite">Book on WhatsApp</a>
  </div>
</div>
<div class="card"><h3>📍 Location: Lwanda, Near Kaimosi & Masinde Muliro University</h3><p>Call: 0799814706 | All rooms have WiFi & 24/7 water</p></div>
"""

@app.route('/')
def home():
    content = """
    <div class="card"><h2>Welcome to SHANON HOSTELS</h2>
    <p>Affordable, Secure, Clean student accommodation in Lwanda.</p>
    <a class="btn" href="/rooms">View Rooms & Photos 📸</a>
    <a class="btn" style="background:green" href="https://wa.me/254799814706">WhatsApp Us</a>
    </div>
    <div class="card"><h3>Why Choose Us?</h3><p>✅ Free WiFi<br>✅ 24/7 Security<br>✅ Clean Water<br>✅ Near University<br>✅ M-Pesa Allowed</p></div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/rooms')
def rooms():
    return render_template_string(BASE_HTML, content=ROOMS_HTML)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=='admin' and request.form['password']=='admin123':
            session['admin']=True
            return redirect('/dashboard')
        else:
            return "Wrong! Use admin / admin123 <a href='/login'>Try again</a>"
    content = """
    <div class="card"><h2>Admin Login</h2>
    <form method="post">
    <input name="username" placeholder="Username" style="width:90%;padding:10px;margin:5px"><br>
    <input name="password" type="password" placeholder="Password" style="width:90%;padding:10px;margin:5px"><br>
    <button class="btn">Login</button>
    </form></div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn=sqlite3.connect('shanon.db')
    c=conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms=c.fetchall()
    c.execute("SELECT * FROM tenants")
    tenants=c.fetchall()
    conn.close()
    html=f"<div class='card'><h2>Admin Dashboard</h2><p>Total Rooms: {len(rooms)} | Tenants: {len(tenants)}</p></div>"
    html+="<div class='card'><h3>Rooms</h3>"
    for r in rooms:
        html+=f"<p>{r[1]} - {r[2]} - {r[3]} - {r[4]}</p>"
    html+="<h3>Tenants</h3>"
    for t in tenants:
        html+=f"<p>{t[1]} - Room {t[2]} - {t[3]}</p>"
    html+="<br><a class='btn' href='/rooms'>View Public Site</a></div>"
    return render_template_string(BASE_HTML, content=html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
