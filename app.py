from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

TASKS_FILE = "tasks.json"

# Load tasks from a file
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as file:
        return json.load(file)

# Save tasks to a file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# Add a new task with a deadline
def add_task(description, deadline=None):
    tasks = load_tasks()
    task_id = 1 if not tasks else tasks[-1]["id"] + 1
    task = {
        "id": task_id,
        "description": description,
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "deadline": deadline if deadline else None  # Optional deadline
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

# Update a task (description & deadline)
def update_task(task_id, description, deadline=None):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = description
            task["updatedAt"] = datetime.now().isoformat()
            if deadline:
                task["deadline"] = deadline
            save_tasks(tasks)
            return task
    return None

# Delete a task
def delete_task(task_id):
    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["id"] != task_id]
    if len(updated_tasks) == len(tasks):
        return False  # Task not found
    save_tasks(updated_tasks)
    return True

# Mark a task's status
def mark_task(task_id, status):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = datetime.now().isoformat()
            save_tasks(tasks)
            return task
    return None

# List tasks with optional status filtering
def list_tasks(filter_status=None):
    tasks = load_tasks()
    if filter_status:
        tasks = [task for task in tasks if task["status"] == filter_status]
    return tasks

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")
    return jsonify(list_tasks(status))

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    if "description" not in data:
        return jsonify({"error": "Description is required"}), 400
    task = add_task(data["description"], data.get("deadline"))
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.json
    if "description" not in data:
        return jsonify({"error": "Description is required"}), 400
    task = update_task(task_id, data["description"], data.get("deadline"))
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    if delete_task(task_id):
        return jsonify({"message": "Task deleted successfully"})
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>/status", methods=["PUT"])
def change_task_status(task_id):
    data = request.json
    if "status" not in data or data["status"] not in ["todo", "in-progress", "done"]:
        return jsonify({"error": "Invalid status"}), 400
    task = mark_task(task_id, data["status"])
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
