from flask import Flask, render_template_string, request, redirect, session, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'shanon-hostels-2026-secret'
DB = 'shanon.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, room_no TEXT UNIQUE, type TEXT, price INTEGER, status TEXT DEFAULT 'Available')''')
    conn.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, id_no TEXT, room_no TEXT, checkin DATE, status TEXT DEFAULT 'Active')''')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    cur = conn.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        conn.execute("INSERT INTO users (username,password) VALUES (?,?)", ('admin','admin123'))
    conn.commit()
    conn.close()

init_db()

BASE = '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHANON HOSTELS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#f5f7fb}.navbar{background:#0d1b2a}.card{border:none;border-radius:15px;box-shadow:0 4px 15px rgba(0,0,0,0.08)}.btn-primary{background:#0d1b2a;border:none}.whatsapp{position:fixed;bottom:20px;right:20px;background:#25D366;color:white;border-radius:50px;padding:12px 20px;text-decoration:none;font-weight:bold;z-index:999}</style>
</head><body>
<nav class="navbar navbar-dark p-3"><div class="container-fluid"><span class="navbar-brand fw-bold">SHANON HOSTELS MANAGEMENT</span>
{% if session.get('user') %}<a href="/logout" class="btn btn-sm btn-light">Logout</a>{% endif %}</div></nav>
<div class="container mt-4">{% with messages = get_flashed_messages() %}{% for m in messages %}<div class="alert alert-info">{{m}}</div>{% endfor %}{% endwith %}{{content|safe}}</div>
<a class="whatsapp" href="https://wa.me/254799814706" target="_blank">WhatsApp Support</a></body></html>
'''

LOGIN_HTML = '''<div class="row justify-content-center mt-5"><div class="col-md-4"><div class="card p-4">
<h4 class="text-center fw-bold">SHANON HOSTELS</h4><p class="text-center text-muted">Admin Login</p>
<form method="post"><input class="form-control mb-3" name="username" placeholder="Username" required>
<input class="form-control mb-3" type="password" name="password" placeholder="Password" required>
<button class="btn btn-primary w-100">Login</button></form>
<small class="text-muted d-block mt-3 text-center">Default: admin / admin123</small></div></div></div>'''

DASH_HTML = '''<h3>Dashboard</h3><div class="row mt-3">
<div class="col-6 col-md-3 mb-3"><div class="card p-3 text-center"><h5>{{total_rooms}}</h5><small>Total Rooms</small></div></div>
<div class="col-6 col-md-3 mb-3"><div class="card p-3 text-center bg-success text-white"><h5>{{available}}</h5><small>Available</small></div></div>
<div class="col-6 col-md-3 mb-3"><div class="card p-3 text-center bg-danger text-white"><h5>{{occupied}}</h5><small>Occupied</small></div></div>
<div class="col-6 col-md-3 mb-3"><div class="card p-3 text-center"><h5>{{total_clients}}</h5><small>Active Clients</small></div></div></div>
<div class="mt-3"><a href="/rooms" class="btn btn-primary me-2">Manage Rooms</a>
<a href="/clients" class="btn btn-outline-dark me-2">Clients</a><a href="/book" class="btn btn-success">+ New Booking</a></div>
<h5 class="mt-4">Recent Clients</h5><div class="card p-3"><table class="table table-sm">
<tr><th>Name</th><th>Room</th><th>Phone</th></tr>{% for c in recent %}<tr><td>{{c['name']}}</td><td>{{c['room_no']}}</td><td>{{c['phone']}}</td></tr>{% endfor %}</table></div>'''

@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form['username']; p=request.form['password']
        conn=get_db(); user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone(); conn.close()
        if user:
            session['user']=u; return redirect('/dashboard')
        flash('Wrong username or password')
    return render_template_string(BASE, content=LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if not session.get('user'): return redirect('/')
    conn=get_db()
    total_rooms=conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    available=conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'").fetchone()[0]
    occupied=conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    total_clients=conn.execute("SELECT COUNT(*) FROM clients WHERE status='Active'").fetchone()[0]
    recent=conn.execute("SELECT * FROM clients WHERE status='Active' ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    content=render_template_string(DASH_HTML, total_rooms=total_rooms, available=available, occupied=occupied, total_clients=total_clients, recent=recent)
    return render_template_string(BASE, content=content)

@app.route('/rooms', methods=['GET','POST'])
def rooms():
    if not session.get('user'): return redirect('/')
    conn=get_db()
    if request.method=='POST':
        try:
            conn.execute("INSERT INTO rooms (room_no,type,price) VALUES (?,?,?)",(request.form['room_no'], request.form['type'], request.form['price']))
            conn.commit(); flash('Room added')
        except: flash('Room number already exists')
    all_rooms=conn.execute("SELECT * FROM rooms").fetchall(); conn.close()
    html='''<h3>Rooms</h3><div class="card p-3 mb-3"><form method="post" class="row g-2">
    <div class="col-4"><input name="room_no" class="form-control" placeholder="Room No e.g A1" required></div>
    <div class="col-4"><select name="type" class="form-select"><option>Single</option><option>Double</option><option>Bedsitter</option><option>1 Bedroom</option></select></div>
    <div class="col-2"><input name="price" type="number" class="form-control" placeholder="Price" required></div>
    <div class="col-2"><button class="btn btn-primary w-100">Add</button></div></form></div>
    <div class="card p-3"><table class="table"><tr><th>Room</th><th>Type</th><th>Price</th><th>Status</th></tr>
    {% for r in rooms %}<tr><td>{{r['room_no']}}</td><td>{{r['type']}}</td><td>{{r['price']}}</td><td><span class="badge bg-{{'success' if r['status']=='Available' else 'danger'}}">{{r['status']}}</span></td></tr>{% endfor %}</table></div>
    <a href="/dashboard" class="btn btn-secondary mt-3">Back</a>'''
    content=render_template_string(html, rooms=all_rooms)
    return render_template_string(BASE, content=content)

@app.route('/book', methods=['GET','POST'])
def book():
    if not session.get('user'): return redirect('/')
    conn=get_db(); rooms=conn.execute("SELECT * FROM rooms WHERE status='Available'").fetchall()
    if request.method=='POST':
        conn.execute("INSERT INTO clients (name,phone,id_no,room_no,checkin) VALUES (?,?,?,?,?)",(request.form['name'],request.form['phone'],request.form['id_no'],request.form['room_no'],datetime.now().strftime('%Y-%m-%d')))
        conn.execute("UPDATE rooms SET status='Occupied' WHERE room_no=?",(request.form['room_no'],)); conn.commit(); flash('Client booked successfully'); conn.close(); return redirect('/clients')
    conn.close()
    html='''<h3>New Booking</h3><div class="card p-4"><form method="post">
    <input name="name" class="form-control mb-2" placeholder="Full Name" required>
    <input name="phone" class="form-control mb-2" placeholder="Phone e.g 07..." required>
    <input name="id_no" class="form-control mb-2" placeholder="ID Number">
    <select name="room_no" class="form-select mb-3" required><option value="">Select Room</option>
    {% for r in rooms %}<option value="{{r['room_no']}}">{{r['room_no']}} - {{r['type']}} - KES {{r['price']}}</option>{% endfor %}</select>
    <button class="btn btn-success w-100">Book Room</button></form></div>'''
    content=render_template_string(html, rooms=rooms)
    return render_template_string(BASE, content=content)

@app.route('/clients')
def clients():
    if not session.get('user'): return redirect('/')
    conn=get_db(); all_c=conn.execute("SELECT * FROM clients WHERE status='Active' ORDER BY id DESC").fetchall(); conn.close()
    html='''<h3>Active Clients</h3><div class="card p-3"><table class="table table-sm">
    <tr><th>Name</th><th>Phone</th><th>Room</th><th>Action</th></tr>
    {% for c in clients %}<tr><td>{{c['name']}}</td><td>{{c['phone']}}</td><td>{{c['room_no']}}</td><td><a href="/checkout/{{c['id']}}/{{c['room_no']}}" class="btn btn-sm btn-danger">Checkout</a></td></tr>{% endfor %}</table></div>
    <a href="/dashboard" class="btn btn-secondary mt-3">Back</a>'''
    content=render_template_string(html, clients=all_c)
    return render_template_string(BASE, content=content)

@app.route('/checkout/<int:id>/<room_no>')
def checkout(id, room_no):
    if not session.get('user'): return redirect('/')
    conn=get_db(); conn.execute("UPDATE clients SET status='Checked Out' WHERE id=?",(id,)); conn.execute("UPDATE rooms SET status='Available' WHERE room_no=?",(room_no,)); conn.commit(); conn.close(); flash('Checked out'); return redirect('/clients')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
