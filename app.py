from flask import Flask, render_template_string, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "shanon-secret-123"

def init_db():
    conn = sqlite3.connect('shanon.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, room_no TEXT, type TEXT, price TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT, room_no TEXT, phone TEXT)''')
    c.execute("SELECT COUNT(*) FROM rooms")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO rooms VALUES (1,'A01','Single Room','Ksh 5,000','Available')")
        c.execute("INSERT INTO rooms VALUES (2,'A02','Double Room','Ksh 6,000','Occupied')")
        c.execute("INSERT INTO rooms VALUES (3,'B01','Bedsitter','Ksh 8,500','Available')")
        c.execute("INSERT INTO rooms VALUES (4,'B02','Premium Ensuite','Ksh 12,000','Available')")
    conn.commit()
    conn.close()

init_db()

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
.room-img{width:100%;height:180px;object-fit:cover;border-radius:10px}
.price{color:green;font-weight:bold;font-size:18px}
</style>
</head>
<body>
<div class="header"><h1>🏨 SHANON HOSTELS</h1><p>Lwanda, Kakamega - 0799814706</p></div>
<div class="nav">
<a href="/">Home</a>
<a href="/rooms">Our Rooms</a>
<a href="/dashboard">Admin</a>
<a href="/logout">Logout</a>
</div>
{{content|safe}}
</body>
</html>
"""

@app.route('/')
def home():
    # WATERMARK HOMEPAGE WITH YOUR HOSTEL
    content = """
    <div style="background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url('https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200'); background-size:cover; background-position:center; padding:30px 15px; min-height:450px; border-radius:10px; margin:10px;">
        <div style="text-align:center">
            <h1 style="background:rgba(255,255,255,0.95); display:inline-block; padding:12px 25px; border-radius:30px; color:#0d1b2a; box-shadow:0 2px 10px rgba(0,0,0,0.2)">SHANON HOSTELS - Best in Lwanda</h1>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-top:25px">
            <div class="card" style="background:rgba(255,255,255,0.92)">
                <h2>Welcome to SHANON HOSTELS</h2>
                <p>Affordable, Secure, Clean student accommodation in Lwanda.</p>
                <a class="btn" href="/rooms">View Rooms & Photos 📸</a><br>
                <a class="btn" style="background:green" href="https://wa.me/254799814706">WhatsApp Us</a>
            </div>
            <div class="card" style="background:rgba(255,255,255,0.92)">
                <h3>Why Choose Us?</h3>
                <p>✅ Free WiFi<br>✅ 24/7 Security<br>✅ Clean rooms<br>✅ Near University<br>✅ M-Pesa Allowed</p>
            </div>
        </div>
        <p style="text-align:center; margin-top:15px; font-size:12px; color:#333">Photo: Your SHANON apartment building</p>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/rooms')
def rooms_page():
    content = """
    <div class="card"><h2>Our Rooms</h2><p>Best student hostels in Western Kenya</p></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:15px">
      <div class="card"><img class="room-img" src="https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=500"><h3>Single Room</h3><p class="price">Ksh 5,000 / month</p><a class="btn" href="https://wa.me/254799814706">Book</a></div>
      <div class="card"><img class="room-img" src="https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?w=500"><h3>Double Room</h3><p class="price">Ksh 6,000 / month</p><a class="btn" href="https://wa.me/254799814706">Book</a></div>
      <div class="card"><img class="room-img" src="https://images.unsplash.com/photo-1554995207-c18c203602cb?w=500"><h3>Bedsitter</h3><p class="price">Ksh 8,500 / month</p><a class="btn" href="https://wa.me/254799814706">Book</a></div>
      <div class="card"><img class="room-img" src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=500"><h3>Premium Ensuite</h3><p class="price">Ksh 12,000 / month</p><a class="btn" href="https://wa.me/254799814706">Book</a></div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=='admin' and request.form['password']=='admin123':
            session['admin']=True
            return redirect('/dashboard')
        else:
            return "Wrong! <a href='/login'>Try again</a>"
    content = """<div class="card"><h2>Admin Login</h2><form method="post"><input name="username" placeholder="Username" style="width:90%;padding:10px;margin:5px"><br><input name="password" type="password" placeholder="Password" style="width:90%;padding:10px;margin:5px"><br><button class="btn">Login</button></form></div>"""
    return render_template_string(BASE_HTML, content=content)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn=sqlite3.connect('shanon.db')
    c=conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms=c.fetchall()
    conn.close()
    html=f"<div class='card'><h2>Admin Dashboard</h2><p>Total Rooms: {len(rooms)}</p></div><div class='card'>"
    for r in rooms:
        html+=f"<p>{r[1]} - {r[2]} - {r[3]} - {r[4]}</p>"
    html+="</div>"
    return render_template_string(BASE_HTML, content=html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
