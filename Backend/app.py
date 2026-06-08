from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask import send_from_directory
from datetime import date, timedelta


app = Flask(__name__)
CORS(app)

# =========================
# MYSQL CONFIG
# =========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vehicle_rental'

mysql = MySQL(app)


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return "🚗 Vehicle Rental System API Running"

# =====================================================
# DASHBOARD
# =====================================================
@app.route('/dashboard/summary', methods=['GET'])
def dashboard_summary():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM owners")
    owners = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM vehicles")
    vehicles = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings")
    bookings = cur.fetchone()[0]

    cur.close()

    return jsonify({
        "users": users,
        "owners": owners,
        "vehicles": vehicles,
        "bookings": bookings
    })
@app.route('/dashboard/vehicle-types', methods=['GET'])
def vehicle_types():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT type, COUNT(*) 
        FROM vehicles
        GROUP BY type
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "type": row[0],
            "count": row[1]
        })

    return jsonify(result)
@app.route('/dashboard/frequent-users', methods=['GET'])
def frequent_users():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT u.name, COUNT(b.id) as bookings_count
        FROM users u
        JOIN bookings b ON u.id = b.user_id
        GROUP BY u.id
        ORDER BY bookings_count DESC
        LIMIT 5
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "user_name": row[0],
            "bookings": row[1]
        })

    return jsonify(result)
@app.route('/dashboard/common-owners', methods=['GET'])
def common_owners():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT o.name, COUNT(v.id) as vehicle_count
        FROM owners o
        JOIN vehicles v ON o.id = v.owner_id
        GROUP BY o.id
        ORDER BY vehicle_count DESC
        LIMIT 5
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "owner_name": row[0],
            "vehicles": row[1]
        })

    return jsonify(result)
@app.route('/dashboard/overdue-users', methods=['GET'])
def overdue_users():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT u.name, COUNT(b.id) as overdue_count
        FROM users u
        JOIN bookings b ON u.id = b.user_id
        WHERE b.due_date < CURDATE()
        AND b.status != 'returned'
        GROUP BY u.id, u.name
        ORDER BY overdue_count DESC
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "name": row[0],
            "overdue": row[1]
        })

    return jsonify(result)
@app.route('/dashboard/pending-vehicles', methods=['GET'])
def pending_vehicles():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'ongoing'
    """)

    count = cur.fetchone()[0]
    cur.close()

    return jsonify({"pending": count})
# =====================================================
# OWNERS
# =====================================================

# ADD OWNER
@app.route('/add_owner', methods=['POST'])
def add_owner():
    data = request.json
    name = data['name']
    phone = data['phone']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO owners(name, phone) VALUES(%s, %s)", (name, phone))
    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Owner added successfully",
        "status": "success"
    })
# VIEW OWNERS
@app.route('/owners', methods=['GET'])
def get_owners():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM owners")
    data = cur.fetchall()
    cur.close()

    owners = []
    for row in data:
        owners.append({
            "id": row[0],
            "name": row[1],
            "phone": row[2]
        })

    return jsonify(owners)


# =====================================================
# VEHICLES
# =====================================================

# ADD VEHICLE
@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.json
    owner_id = data['owner_id']
    name = data['name']
    vtype = data['type']
    price = data['price']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO vehicles(owner_id, name, type, price)
        VALUES(%s, %s, %s, %s)
    """, (owner_id, name, vtype, price))

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Vehicle added successfully",
        "status": "success"
    })
# VIEW VEHICLES (WITH OWNER DETAILS)
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT v.id, v.name, v.type, v.price, o.id, o.name
        FROM vehicles v
        JOIN owners o ON v.owner_id = o.id
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "vehicle_id": row[0],
            "vehicle_name": row[1],
            "type": row[2],
            "price_per_day": row[3],
            "owner_id": row[4],
            "owner_name": row[5]
        })

    return jsonify(result)


# =====================================================
# USERS
# =====================================================

# REGISTER USER
@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    name = data['name']
    phone = data['phone']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(name, phone) VALUES(%s, %s)", (name, phone))
    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "User registered successfully",
        "status": "success"
    })

# VIEW USERS
@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()

    users = []
    for row in data:
        users.append({
            "id": row[0],
            "name": row[1],
            "phone": row[2]
        })

    return jsonify(users)


# =====================================================
# BOOKINGS
# =====================================================

# BOOK VEHICLE
@app.route('/book_vehicle', methods=['POST'])
def book_vehicle():
    data = request.json

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO bookings (user_id, vehicle_id, lending_date, due_date, days, status)
        VALUES (%s, %s, %s, %s, %s, 'ongoing')
    """, (
        data['user_id'],
        data['vehicle_id'],
        data['lending_date'],
        data['due_date'],
        data['days']
    ))

    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Vehicle booked successfully"})

# VIEW BOOKINGS (USER + VEHICLE + OWNER DETAILS)
@app.route('/bookings')
def get_bookings():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            b.id,
            u.name,
            v.name,
            b.lending_date,
            b.due_date,
            b.days
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
    """)

    data = cur.fetchall()
    cur.close()

    result = []
    for row in data:
        result.append({
            "booking_id": row[0],
            "user_name": row[1],
            "vehicle_name": row[2],
            "lending_date": row[3],
            "due_date": row[4],
            "days": row[5]
        })

    return jsonify(result)


# =====================================================
# RUN SERVER
# =====================================================
if __name__ == '__main__':
    app.run(debug=True)
