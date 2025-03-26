import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Path to the JSON file
STUDENTS_FILE = 'students.json'

def load_students():
    """Load students from JSON file, create file if it doesn't exist"""
    if not os.path.exists(STUDENTS_FILE):
        # Initialize with the default student if file doesn't exist
        initial_students = [
            {
                "name": "Abdelfatah Mennoun",
                "email": "admin@mennoun.me",
                "username": "m3nnoun",
                "password": "admin",
                "marks": {
                    "acp": 12,
                    "maths": 14,
                    "python": 15,
                    "statistics": 19,
                    "physics": 16
                }
            }
        ]
        with open(STUDENTS_FILE, 'w') as f:
            json.dump(initial_students, f, indent=4)
    
    # Read the students from the file
    with open(STUDENTS_FILE, 'r') as f:
        return json.load(f)

def save_students(students):
    """Save students to JSON file"""
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=4)

@app.route("/login", methods=["POST"])
def login():
    students = load_students()
    credentials = request.json
    username = credentials.get("username")
    password = credentials.get("password")

    for student in students:
        if student["username"] == username and student["password"] == password:
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {
                    "name": student["name"],
                    "email": student["email"],
                    "username": student["username"],
                    "marks": student["marks"]
                }
            }), 200

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/add-mark", methods=["POST"])
def add_mark():
    students = load_students()
    body = request.json
    username = body.get("username")
    module = body.get("module")
    mark = body.get("mark")

    if not all([username, module, isinstance(mark, (int, float))]):
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    for student in students:
        if student["username"] == username:
            student["marks"][module] = mark
            save_students(students)
            return jsonify({"status": "success", "message": "Mark added successfully"}), 200

    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route("/marks/<username>", methods=["GET"])
def get_marks(username):
    students = load_students()
    for student in students:
        if student["username"] == username:
            return jsonify({"marks": student["marks"]}), 200

    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route("/student/<username>", methods=["GET"])
def get_student(username):
    students = load_students()
    for student in students:
        if student["username"] == username:
            return jsonify({
                "name": student["name"],
                "email": student["email"],
                "username": student["username"],
                "marks": student["marks"]
            }), 200

    return jsonify({"status": "error", "message": "User not found"}), 404

# Path to the CSV file
LOCATIONS_FILE = 'locations.csv'

def save_location_to_csv(latitude, longitude, timestamp):
    """Save a new location to the CSV file."""
    # Check if the file exists; if not, create it and add the header
    file_exists = os.path.exists(LOCATIONS_FILE)

    # Open the CSV file in append mode
    with open(LOCATIONS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write the header row if the file is newly created
            writer.writerow(["Latitude", "Longitude", "Timestamp"])
        # Write the new location data
        writer.writerow([latitude, longitude, timestamp])

@app.route("/update-location", methods=["POST"])
def update_location():
    # Get the JSON data from the request
    data = request.get_json()

    # Validate the incoming data
    if not data or 'latitude' not in data or 'longitude' not in data or 'timestamp' not in data:
        return jsonify({"status": "error", "message": "Invalid or missing fields"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    timestamp = data.get("timestamp")

    # Save the new location to the CSV file
    save_location_to_csv(latitude, longitude, timestamp)

    # Return a success response
    return jsonify({
        "status": "success",
        "message": "Location updated successfully",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        }
    }), 200


# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)