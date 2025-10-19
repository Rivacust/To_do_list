from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from bson.objectid import ObjectId
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# MongoDB Atlas connection
username = quote_plus("Rivacust")
password = quote_plus("Rick@123")
app.config["MONGO_URI"] = f"mongodb+srv://{username}:{password}@cluster0.eyyuni3.mongodb.net/taskmaster"
mongo = PyMongo(app)
users_collection = mongo.db.users
tasks_collection = mongo.db.tasks

# ----------------- SIGNUP -----------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id = users_collection.insert_one({"name": name, "email": email, "password": hashed_pw}).inserted_id
    return jsonify({"message": "User created successfully", "user_id": str(user_id)}), 200

# ----------------- SIGNIN -----------------
@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 400

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid password"}), 400

    return jsonify({"message": f"Welcome {user['name']}!", "user_id": str(user['_id'])}), 200

# ----------------- ADD TASK -----------------
@app.route('/tasks/<user_id>', methods=['POST'])
def add_task(user_id):
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({"error": "Task title required"}), 400
    task = {"title": title, "user_id": user_id}
    task_id = tasks_collection.insert_one(task).inserted_id
    return jsonify({"message": "Task added", "task_id": str(task_id)}), 200

# ----------------- GET TASKS -----------------
@app.route('/tasks/<user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = list(tasks_collection.find({"user_id": user_id}))
    for t in tasks:
        t["_id"] = str(t["_id"])
    return jsonify(tasks), 200

# ----------------- DELETE TASK -----------------
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Task deleted"}), 200
    return jsonify({"error": "Task not found"}), 404

# ----------------- RUN APP -----------------
if __name__ == '__main__':
    app.run(debug=True)
