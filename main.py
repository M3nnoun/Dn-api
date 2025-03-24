from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect('student_database.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        class TEXT NOT NULL,
        remarks TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    
    # Create marks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT NOT NULL,
        mark REAL NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')
    
    conn.commit()
    conn.close()

# Utility function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Route to add a new student
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    
    # Validate input
    required_fields = ['first_name', 'last_name', 'class', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400
    
    # Optional fields
    remarks = data.get('remarks', '')
    
    # Hash the password
    hashed_password = hash_password(data['password'])
    
    try:
        conn = sqlite3.connect('student_database.db')
        cursor = conn.cursor()
        
        # Insert student
        cursor.execute('''
        INSERT INTO students 
        (first_name, last_name, class, remarks, email, password) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['first_name'], data['last_name'], data['class'], 
              remarks, data['email'], hashed_password))
        
        student_id = cursor.lastrowid
        
        # Add marks if provided
        if 'marks' in data:
            for mark_data in data['marks']:
                cursor.execute('''
                INSERT INTO marks (student_id, subject, mark) 
                VALUES (?, ?, ?)
                ''', (student_id, mark_data['subject'], mark_data['mark']))
        
        conn.commit()
        return jsonify({"message": "Student added successfully", "student_id": student_id}), 201
    
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

# Route to get all students
@app.route('/get_students', methods=['GET'])
def get_students():
    try:
        conn = sqlite3.connect('student_database.db')
        cursor = conn.cursor()
        
        # Get students with their marks
        cursor.execute('''
        SELECT s.id, s.first_name, s.last_name, s.class, s.remarks, s.email,
               m.subject, m.mark
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        ''')
        
        # Process results
        students = {}
        for row in cursor.fetchall():
            student_id, first_name, last_name, student_class, remarks, email, subject, mark = row
            
            if student_id not in students:
                students[student_id] = {
                    "id": student_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "class": student_class,
                    "remarks": remarks,
                    "email": email,
                    "marks": []
                }
            
            if subject and mark is not None:
                students[student_id]["marks"].append({
                    "subject": subject,
                    "mark": mark
                })
        
        return jsonify(list(students.values())), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

# Route for student login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        conn = sqlite3.connect('student_database.db')
        cursor = conn.cursor()
        
        # Check credentials
        cursor.execute('''
        SELECT id, first_name, last_name 
        FROM students 
        WHERE email = ? AND password = ?
        ''', (data['email'], hash_password(data['password'])))
        
        student = cursor.fetchone()
        
        if student:
            return jsonify({
                "message": "Login successful",
                "student_id": student[0],
                "name": f"{student[1]} {student[2]}"
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

# New Route: Get Student by First and Last Name
@app.route('/get_student', methods=['GET'])
def get_student_by_name():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    
    if not first_name or not last_name:
        return jsonify({"error": "First name and last name are required"}), 400
    
    try:
        conn = sqlite3.connect('student_database.db')
        cursor = conn.cursor()
        
        # Get student details with marks
        cursor.execute('''
        SELECT s.id, s.first_name, s.last_name, s.class, s.remarks, s.email,
               m.subject, m.mark
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        WHERE s.first_name = ? AND s.last_name = ?
        ''', (first_name, last_name))
        
        # Process results
        student_data = None
        marks = []
        
        for row in cursor.fetchall():
            if student_data is None:
                student_id, first_name, last_name, student_class, remarks, email, _, _ = row
                student_data = {
                    "id": student_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "class": student_class,
                    "remarks": remarks,
                    "email": email,
                    "marks": []
                }
            
            # Add marks if they exist
            if row[6] and row[7] is not None:
                student_data["marks"].append({
                    "subject": row[6],
                    "mark": row[7]
                })
        
        if student_data is None:
            return jsonify({"error": "Student not found"}), 404
        
        return jsonify(student_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

# New Route: Add Mark for a Specific Student
@app.route('/add_mark', methods=['POST'])
def add_mark_to_student():
    data = request.json
    
    # Validate input
    required_fields = ['first_name', 'last_name', 'subject', 'mark']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400
    
    try:
        conn = sqlite3.connect('student_database.db')
        cursor = conn.cursor()
        
        # Find student ID
        cursor.execute('''
        SELECT id FROM students 
        WHERE first_name = ? AND last_name = ?
        ''', (data['first_name'], data['last_name']))
        
        student_result = cursor.fetchone()
        
        if not student_result:
            return jsonify({"error": "Student not found"}), 404
        
        student_id = student_result[0]
        
        # Insert new mark
        cursor.execute('''
        INSERT INTO marks (student_id, subject, mark) 
        VALUES (?, ?, ?)
        ''', (student_id, data['subject'], data['mark']))
        
        conn.commit()
        return jsonify({
            "message": "Mark added successfully", 
            "student_id": student_id,
            "subject": data['subject'],
            "mark": data['mark']
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

# Initialize database when the app starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)