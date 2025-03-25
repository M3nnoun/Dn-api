from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory dictionary to store student data
data = {
    "name": "Abdelfatah Mennoun",
    "email": "admin@mennoun.me",
    "username": "m3nnoun",
    "marks": {
      "acp": 12,
      "maths": 14,
      "python": 15,
      "statistics": 19,
      "physics": 16
    }
  }

@app.route("/login", methods=["POST"])
def login():
    credentials = request.json
    username = credentials.get("username")
    password = credentials.get("password")

    for student in data["students"]:
        if student["username"] == username and student["password"] == password:
            return jsonify({"status": "success", "message": "Login successful"}), 200

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/add-mark", methods=["POST"])
def add_mark():
    body = request.json
    username = body.get("username")
    module = body.get("module")
    mark = body.get("mark")

    for student in data["students"]:
        if student["username"] == username:
            student["marks"][module] = mark
            return jsonify({"status": "success", "message": "Mark added successfully"}), 200

    return jsonify({"status": "error", "message": "User not found"}), 404


@app.route("/marks/<username>", methods=["GET"])
def get_marks(username):
    for student in data["students"]:
        if student["username"] == username:
            return jsonify({"marks": student["marks"]}), 200

    return jsonify({"status": "error", "message": "User not found"}), 404


@app.route("/student/<username>", methods=["GET"])
def get_student(username):
    for student in data["students"]:
        if student["username"] == username:
            return jsonify({
                "name": student["name"],
                "email": student["email"],
                "username": student["username"],
                "marks": student["marks"]
            }), 200

    return jsonify({"status": "error", "message": "User not found"}), 404


# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)