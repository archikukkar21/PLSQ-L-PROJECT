from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'hotel123'  # for flash messages

def get_db_connection():
    conn = sqlite3.connect(r'E:\pl sql project\hotel-booking-system\hotel-booking-system\hotel.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

# ----------------- GUESTS -----------------
@app.route('/guests')
def guests():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM Guests').fetchall()
    conn.close()
    return render_template('guests.html', guests=guests)

@app.route('/add_guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        conn = get_db_connection()
        conn.execute('INSERT INTO Guests (name, phone) VALUES (?, ?)', (name, phone))
        conn.commit()
        conn.close()
        flash('Guest added successfully!')
        return redirect(url_for('guests'))
    return render_template('add_edit_guest.html', action='Add')

@app.route('/edit_guest/<int:id>', methods=['GET', 'POST'])
def edit_guest(id):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM Guests WHERE guest_id=?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        conn.execute('UPDATE Guests SET name=?, phone=? WHERE guest_id=?', (name, phone, id))
        conn.commit()
        conn.close()
        flash('Guest updated successfully!')
        return redirect(url_for('guests'))
    conn.close()
    return render_template('add_edit_guest.html', action='Edit', guest=guest)

@app.route('/delete_guest/<int:id>')
def delete_guest(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Guests WHERE guest_id=?', (id,))
    conn.commit()
    conn.close()
    flash('Guest deleted successfully!')
    return redirect(url_for('guests'))

# ----------------- ROOMS -----------------
@app.route('/rooms')
def rooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM Rooms').fetchall()
    conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_type = request.form['type']
        price = request.form['price']
        conn = get_db_connection()
        conn.execute('INSERT INTO Rooms (type, price_per_night, status) VALUES (?, ?, ?)',
                     (room_type, price, 'Available'))
        conn.commit()
        conn.close()
        flash('Room added successfully!')
        return redirect(url_for('rooms'))
    return render_template('add_edit_room.html', action='Add')

@app.route('/edit_room/<int:id>', methods=['GET', 'POST'])
def edit_room(id):
    conn = get_db_connection()
    room = conn.execute('SELECT * FROM Rooms WHERE room_id=?', (id,)).fetchone()
    if request.method == 'POST':
        room_type = request.form['type']
        price = request.form['price']
        status = request.form['status']
        conn.execute('UPDATE Rooms SET type=?, price_per_night=?, status=? WHERE room_id=?',
                     (room_type, price, status, id))
        conn.commit()
        conn.close()
        flash('Room updated successfully!')
        return redirect(url_for('rooms'))
    conn.close()
    return render_template('add_edit_room.html', action='Edit', room=room)

@app.route('/delete_room/<int:id>')
def delete_room(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Rooms WHERE room_id=?', (id,))
    conn.commit()
    conn.close()
    flash('Room deleted successfully!')
    return redirect(url_for('rooms'))

# ----------------- BOOKINGS -----------------
@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM Guests').fetchall()
    rooms = conn.execute("SELECT * FROM Rooms WHERE status='Available'").fetchall()
    if request.method == 'POST':
        guest_id = request.form['guest']
        room_id = request.form['room']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        conn.execute('INSERT INTO Bookings (guest_id, room_id, checkin, checkout) VALUES (?, ?, ?, ?)',
                     (guest_id, room_id, checkin, checkout))
        conn.execute("UPDATE Rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        conn.commit()
        conn.close()
        flash('Room booked successfully!')
        return redirect(url_for('bookings'))
    conn.close()
    return render_template('book_room.html', guests=guests, rooms=rooms)

@app.route('/bookings')
def bookings():
    conn = get_db_connection()
    bookings = conn.execute('''SELECT b.booking_id, g.name AS guest, r.type AS room_type, 
                            b.checkin, b.checkout 
                            FROM Bookings b
                            JOIN Guests g ON b.guest_id = g.guest_id
                            JOIN Rooms r ON b.room_id = r.room_id''').fetchall()
    conn.close()
    return render_template('bookings.html', bookings=bookings)

@app.route('/delete_booking/<int:id>')
def delete_booking(id):
    conn = get_db_connection()
    room_id = conn.execute('SELECT room_id FROM Bookings WHERE booking_id=?', (id,)).fetchone()['room_id']
    conn.execute('DELETE FROM Bookings WHERE booking_id=?', (id,))
    conn.execute("UPDATE Rooms SET status='Available' WHERE room_id=?", (room_id,))
    conn.commit()
    conn.close()
    flash('Booking deleted (room now available).')
    return redirect(url_for('bookings'))

if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS Guests (
                        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT UNIQUE NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Rooms (
                        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        price_per_night REAL CHECK(price_per_night > 0),
                        status TEXT DEFAULT 'Available')''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Bookings (
                        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guest_id INTEGER,
                        room_id INTEGER,
                        checkin TEXT,
                        checkout TEXT,
                        FOREIGN KEY(guest_id) REFERENCES Guests(guest_id),
                        FOREIGN KEY(room_id) REFERENCES Rooms(room_id))''')
    conn.commit()
    conn.close()
    app.run(debug=True)
