from flask import Flask, request, jsonify, session
from models import db, User, Task, bcrypt
from functools import wraps
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretdevkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:securepass@db:3306/capstone_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

# Wait for MySQL database container to become fully active
with app.app_context():
    for attempt in range(10):
        try:
            db.create_all()
            print("Successfully connected to MySQL and created tables!")
            break
        except Exception as e:
            print(f"Database not ready yet (Attempt {attempt+1}/10). Retrying in 3 seconds...")
            time.sleep(3)

# 1. Registration Route with Secure Hashing
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing credentials"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password_hash=hashed_password, role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# 2. Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password', '')):
        session['user_id'] = user.id
        session['role'] = user.role
        return jsonify({"message": "Logged in successfully", "role": user.role}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# 3. Task Manager CRUD Feature (Parameterized via ORM)
@app.route('/tasks', methods=['POST', 'GET'])
def handle_tasks():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'POST':
        data = request.get_json() or {}
        if not data.get('title'):
            return jsonify({"error": "Title required"}), 400
        new_task = Task(title=data['title'], description=data.get('description'), user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"message": "Task created"}), 201
        
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{"id": t.id, "title": t.title, "description": t.description} for t in tasks])

# 4. Admin Dashboard (Role-Based Access Control)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_tasks = Task.query.count()
    return jsonify({
        "status": "Welcome Admin",
        "metrics": {"total_users": total_users, "total_tasks": total_tasks}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
