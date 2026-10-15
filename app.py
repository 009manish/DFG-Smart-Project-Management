from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
import mysql.connector
import re
import os
import subprocess
import json

app = Flask(__name__)
app.secret_key = "dfg_dev_secret_key_2026"
# DATABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="dfg_database"
    )

# TASK EXTRACTION

def extract_tasks(discussion):
    tasks = []

    # Split discussion into sentences or numbered-list items
    sentences = re.split(r'[\n.!?;]+', discussion)

    action_words = [
        "design", "create", "develop", "build",
        "implement", "complete", "test", "prepare",
        "setup", "set up", "install", "configure",
        "fix", "debug", "write", "update",
        "document", "deploy", "integrate"
    ]

    for sentence in sentences:
        sentence = sentence.strip()

        # Remove numbering like "1." or "2)"
        sentence = re.sub(r'^\s*\d+[\.\)]\s*', '', sentence)

        if not sentence:
            continue

        # Split multiple actions joined by commas or connectors
        parts = re.split(
            r',\s*|\s+(?:and then|then|also|after that)\s+',
            sentence,
            flags=re.IGNORECASE
        )

        for part in parts:
            part = part.strip()
            if not part:
                continue

            lower_part = part.lower()

            if any(action in lower_part for action in action_words):
                task = re.sub(
                    r'^(we need to|we have to|we should|we must)\s+',
                    '',
                    part,
                    flags=re.IGNORECASE
                ).strip()

                if task:
                    task = task[0].upper() + task[1:]

                    # Avoid duplicate tasks
                    if task.lower() not in [t.lower() for t in tasks]:
                        tasks.append(task)

    return tasks

# PRIORITY ENGINE
def calculate_priority(task):
    task_lower = task.lower()
    high_priority_words = [
        "design",
        "database",
        "setup",
        "configure",
        "implement"
    ]
    medium_priority_words = [
        "create",
        "develop",
        "build",
        "test"
    ]
    for word in high_priority_words:
        if word in task_lower:
            return 3
    for word in medium_priority_words:
        if word in task_lower:
            return 2

    return 1

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# CREATE SESSION
@app.route("/create-session", methods=["GET", "POST"])
def create_session():
    if request.method == "GET":
        login_session["user_id"] = 1
        return render_template("create_session.html")

    title = request.form["title"]
    goal = request.form["goal"]
    discussion = request.form["discussion"]
    members = int(request.form["members"])
    db = get_db_connection()
    cursor = db.cursor()
    # Create session
    cursor.execute(
        """
        INSERT INTO sessions
        (user_id, title, goal, discussion)
        VALUES (%s, %s, %s, %s)
        """,
        (
            1,
            title,
            goal,
            discussion
        )
    )
    db.commit()
    session_id = cursor.lastrowid
    # Generate session code
    session_code = f"DFG-{session_id:04d}"
    # Add creator as first member
    cursor.execute(
        """
        INSERT INTO session_members
        (session_id, user_id)
        VALUES (%s, %s)
        """,
        (
            session_id,
            1
        )
    )
    db.commit()
    # Extract tasks
    tasks = extract_tasks(discussion)
    # Save every task and create its OS process
    for task in tasks:
        priority = calculate_priority(task)

        cursor.execute(
            """
            INSERT INTO tasks
            (session_id, title, description, priority)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, task, task, priority)
        )

        # Get newly created task ID
        task_id = cursor.lastrowid

        # Create OS process for this task
        cursor.execute(
            """
            INSERT INTO processes
            (task_id, state, priority)
            VALUES (%s, %s, %s)
            """,
            (task_id, "New", priority)
        )

    db.commit()
    cursor.close()
    db.close()
    return render_template(
        "session_created.html",
        session_id=session_id,
        session_code=session_code,
        title=title,
        goal=goal,
        members=members,
        tasks=tasks
    )

# JOIN SESSION
@app.route("/join-session", methods=["GET", "POST"])
def join_session():
    if request.method == "GET":
        return render_template("join_session.html")
    session_code = request.form["session_code"].strip().upper()
    name = request.form["name"].strip()
    email = request.form["email"].strip().lower()
    # Validate code
    if not session_code.startswith("DFG-"):
        return "Invalid session code. Example: DFG-0007"
    try:
        session_id = int(
            session_code.replace("DFG-", "")
        )
    except ValueError:
        return "Invalid session code."
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Find session
    cursor.execute(
        """
        SELECT *
        FROM sessions
        WHERE session_id = %s
        """,
        (session_id,)
    )
    session = cursor.fetchone()
    if not session:
        cursor.close()
        db.close()
        return "Session not found."
    # Count members
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM session_members
        WHERE session_id = %s
        """,
        (session_id,)
    )
    member_count = cursor.fetchone()["total"]
    # Find user
    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = %s
        """,
        (email,)
    )
    user = cursor.fetchone()
    # Create user
    if user:
        user_id = user["user_id"]
        cursor.execute(
            """
            UPDATE users
            SET name = %s
            WHERE user_id = %s
            """,
            (
                name,
                user_id
            )
        )
        db.commit()
    else:
        cursor.execute(
            """
            INSERT INTO users
            (name, email)
            VALUES (%s, %s)
            """,
            (
                name,
                email
            )
        )
        db.commit()
        user_id = cursor.lastrowid
    login_session["user_id"] = user_id
    # Check already joined
    cursor.execute(
        """
        SELECT *
        FROM session_members
        WHERE session_id = %s
        AND user_id = %s
        """,
        (session_id, user_id)
    )
    existing_member = cursor.fetchone()
    # Add member
    if not existing_member:
        if member_count >= 4:
            cursor.close()
            db.close()
            return "This session is already full. Maximum 4 members allowed."
        cursor.execute(
            """
            INSERT INTO session_members
            (session_id, user_id)
            VALUES (%s, %s)
            """,
            (
                session_id,
                user_id
            )
        )
        db.commit()
    # Get all members
    cursor.execute(
        """
        SELECT
            sm.id,
            sm.session_id,
            sm.user_id,
            sm.joined_at,
            u.name,
            u.email
        FROM session_members sm
        JOIN users u
            ON sm.user_id = u.user_id
        WHERE sm.session_id = %s
        ORDER BY sm.id
        """,
        (session_id,)
    )
    team_members = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template(
        "session_joined.html",
        session=session,
        session_code=session_code,
        members=team_members,
        total_members=len(team_members)
    )

# START SESSION
@app.route("/start-session")
def start_session():
    session_id = request.args.get("session_id")
    if not session_id:
        return "Session ID missing."
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Get session
    cursor.execute(
        """
        SELECT *
        FROM sessions
        WHERE session_id = %s
        """,
        (session_id,)
    )
    session = cursor.fetchone()
    if not session:
        cursor.close()
        db.close()
        return "Session not found."
    # Mark session as started
    cursor.execute(
        """
        UPDATE sessions
        SET is_started = 1
        WHERE session_id = %s
        """,
        (session_id,)
    )
    db.commit()
    # Get tasks
    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE session_id = %s
        ORDER BY priority DESC, task_id ASC
        """,
        (session_id,)
    )
    tasks = cursor.fetchall()
    # Get members
    cursor.execute(
        """
        SELECT
            sm.id,
            sm.user_id,
            u.name,
            u.email,
            sm.joined_at
        FROM session_members sm
        JOIN users u
            ON sm.user_id = u.user_id
        WHERE sm.session_id = %s
        ORDER BY sm.id
        """,
        (session_id,)
    )
    members = cursor.fetchall()
    cursor.close()
    db.close()
    session_code = f"DFG-{int(session_id):04d}"
    return render_template(
        "workspace.html",
        session=session,
        session_code=session_code,
        tasks=tasks,
        members=members,
        current_user_id=login_session.get("user_id")
    )

# GET TASKS FOR LIVE WORKSPACE
@app.route("/session-tasks/<int:session_id>")
def session_tasks(session_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT task_id, title, priority, status
            FROM tasks
            WHERE session_id = %s
            ORDER BY task_id DESC
            """,
            (session_id,)
        )

        tasks = cursor.fetchall()

        return jsonify({"tasks": tasks})

    finally:
        cursor.close()
        db.close()

# GET LIVE DATA
@app.route("/session-data/<int:session_id>")
def session_data(session_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Members
    cursor.execute(
        """
        SELECT
            sm.user_id,
            u.name,
            u.email
        FROM session_members sm
        JOIN users u
            ON sm.user_id = u.user_id
        WHERE sm.session_id = %s
        ORDER BY sm.id
        """,
        (session_id,)
    )
    members = cursor.fetchall()
    # Messages
    cursor.execute(
        """
        SELECT
            m.message_id,
            m.message,
            m.sent_at,
            u.name
        FROM messages m
        JOIN users u
            ON m.user_id = u.user_id
        WHERE m.session_id = %s
        ORDER BY m.message_id ASC
        """,
        (session_id,)
    )
    messages = cursor.fetchall()
    cursor.close()
    db.close()
    for message in messages:
        if message["sent_at"]:
            message["sent_at"] = message["sent_at"].strftime("%H:%M")
    return jsonify({
        "members": members,
        "messages": messages
    })

@app.route("/session-status/<int:session_id>")
def session_status(session_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT is_started
        FROM sessions
        WHERE session_id = %s
        """,
        (session_id,)
    )

    session = cursor.fetchone()
    cursor.close()
    db.close()

    if not session:
        return jsonify({"started": False, "error": "Session not found"}), 404

    return jsonify({
        "started": bool(session["is_started"])
    })

# SEND CHAT MESSAGE
@app.route("/send-message", methods=["POST"])
def send_message():
    session_id = request.form["session_id"]
    user_id = login_session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "error": "Please join the session first."
        }), 401
    message = request.form["message"].strip()

    if not message:
        return jsonify({"success": False})

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT 1 FROM session_members
        WHERE session_id = %s AND user_id = %s
        """,
        (session_id, user_id)
    )

    if not cursor.fetchone():
        cursor.close()
        db.close()
        return jsonify({
            "success": False,
            "error": "You are not a member of this session."
        }), 403

    try:
        # 1. Save chat message
        cursor.execute(
            """
            INSERT INTO messages (session_id, user_id, message)
            VALUES (%s, %s, %s)
            """,
            (session_id, user_id, message)
        )

        # 2. Extract possible tasks from this message
        extracted_tasks = extract_tasks(message)
        tasks_created = 0

        for task in extracted_tasks:
            # 3. Avoid duplicate task titles in the same session
            cursor.execute(
                """
                SELECT task_id FROM tasks
                WHERE session_id = %s AND LOWER(title) = LOWER(%s)
                LIMIT 1
                """,
                (session_id, task)
            )

            if cursor.fetchone():
                continue

            # 4. Save new task
            cursor.execute(
                """
                INSERT INTO tasks
                    (session_id, title, description, priority, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    task,
                    task,
                    calculate_priority(task),
                    "Pending"
                )
            )

            tasks_created += 1

        db.commit()

        return jsonify({
            "success": True,
            "tasks_created": tasks_created
        })

    except Exception as e:
        db.rollback()
        print("Send message error:", e)
        return jsonify({"success": False}), 500

    finally:
        cursor.close()
        db.close()

# OS - NON-PREEMPTIVE PRIORITY CPU SCHEDULING
@app.route("/cpu-schedule/<int:session_id>")
def cpu_schedule(session_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Fetch only processes belonging to this session.
        # Higher numeric priority is treated as higher priority.
        cursor.execute(
            """
            SELECT p.process_id, p.task_id, p.priority,
                p.burst_time, p.remaining_time, p.state,
                t.title
            FROM processes p
            JOIN tasks t ON t.task_id = p.task_id
            WHERE t.session_id = %s
            AND p.state <> 'Terminated'
            ORDER BY p.priority DESC,
                    p.arrival_time ASC,
                    p.process_id ASC
            """,
            (session_id,)
        )
        processes = cursor.fetchall()
        
        if not processes:
            return jsonify({
                "algorithm": "Non-Preemptive Priority Scheduling",
                "session_id": session_id,
                "message": "No pending processes found for this session.",
                "execution_order": []
            })

        execution_order = []
        current_time = 0
        total_waiting_time = 0
        total_turnaround_time = 0

        for process in processes:
            process_id = process["process_id"]
            burst_time = process["burst_time"] or 5

            waiting_time = current_time
            turnaround_time = waiting_time + burst_time

            cursor.execute(
                """
                UPDATE processes
                SET state = 'Running',
                    started_at = CURRENT_TIMESTAMP,
                    remaining_time = %s
                WHERE process_id = %s
                """,
                (burst_time, process_id)
            )
            db.commit()

            cursor.execute(
                """
                UPDATE processes
                SET state = 'Terminated',
                    remaining_time = 0,
                    completed_at = CURRENT_TIMESTAMP
                WHERE process_id = %s
                """,
                (process_id,)
            )
            db.commit()

            execution_order.append({
                "process_id": process_id,
                "task_id": process["task_id"],
                "task": process["title"],
                "priority": process["priority"],
                "burst_time": burst_time,
                "waiting_time": waiting_time,
                "turnaround_time": turnaround_time,
                "state": "Terminated"
            })

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            current_time += burst_time

        process_count = len(execution_order)

        return jsonify({
            "algorithm": "Non-Preemptive Priority Scheduling",
            "session_id": session_id,
            "priority_rule": "Higher numeric value runs first; ties use arrival time, then process ID.",
            "note": "Scheduling is simulated in the database; metrics assume all pending processes are available at time 0.",
            "execution_order": execution_order,
            "total_waiting_time": total_waiting_time,
            "total_turnaround_time": total_turnaround_time,
            "average_waiting_time": round(
                total_waiting_time / process_count, 2
            ),
            "average_turnaround_time": round(
                total_turnaround_time / process_count, 2
            )
        })

    finally:
        cursor.close()
        db.close()

@app.route("/run-scheduler/<int:session_id>")
def run_scheduler(session_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.task_id, t.title, COALESCE(p.burst_time, 1) AS burst_time,COALESCE(p.priority, t.priority, 1) AS priority
            FROM tasks t
            LEFT JOIN processes p ON t.task_id = p.task_id
            WHERE t.session_id = %s
        """, (session_id,))

        tasks = cursor.fetchall()

        if not tasks:
            return jsonify({
                "success": False,
                "error": "No tasks found for this session."
            }), 404

        # C scheduler executable is in the DFG root folder
        exe_path = os.path.join(app.root_path, "scheduler.exe")

        if not os.path.exists(exe_path):
            return jsonify({
                "success": False,
                "error": "scheduler.exe not found. Compile the C program first."
            }), 500

        # Input format: number of tasks, then burst time and priority
        input_data = str(len(tasks)) + "\n"

        for task in tasks:
            input_data += (
                f"{task['burst_time']} {task['priority']}\n"
            )

        result = subprocess.run(
            [exe_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        return jsonify({
            "success": True,
            "tasks": tasks,
            "scheduler_output": result.stdout
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Scheduler took too long."
        }), 500

    except Exception as e:
        print("Scheduler error:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        db.close()

@app.route("/detect-deadlock/<int:session_id>")
def detect_deadlock(session_id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Get resources for this session
        cursor.execute("""
            SELECT resource_id, total_instances, available_instances
            FROM os_resources
            WHERE session_id = %s
            ORDER BY resource_id
        """, (session_id,))
        resources = cursor.fetchall()

        if not resources:
            return jsonify({
                "success": False,
                "error": "No resources found for this session."
            }), 404

        # Get process IDs for this session
        cursor.execute("""
            SELECT p.process_id
            FROM processes p
            JOIN tasks t ON p.task_id = t.task_id
            WHERE t.session_id = %s
            ORDER BY p.process_id
        """, (session_id,))
        processes = cursor.fetchall()

        if not processes:
            return jsonify({
                "success": False,
                "error": "No processes found for this session."
            }), 404

        process_ids = [row[0] for row in processes]
        resource_ids = [row[0] for row in resources]

        # Get resource allocations and outstanding requests
        cursor.execute("""
            SELECT a.process_id, a.resource_id,a.allocated_instances, a.requested_instances
            FROM os_resource_allocations a
            JOIN os_resources r ON a.resource_id = r.resource_id
            WHERE r.session_id = %s
        """, (session_id,))
        allocations = cursor.fetchall()

        allocation_map = {}
        request_map = {}

        for pid, rid, allocated, requested in allocations:
            allocation_map[(pid, rid)] = allocated
            request_map[(pid, rid)] = requested

        allocation_matrix = []
        request_matrix = []

        for pid in process_ids:
            allocation_matrix.append([
                allocation_map.get((pid, rid), 0)
                for rid in resource_ids
            ])
            request_matrix.append([
                request_map.get((pid, rid), 0)
                for rid in resource_ids
            ])

        available = [row[2] for row in resources]

        # C input format:
        # n m, process IDs, allocation matrix,
        # request matrix, available vector
        input_lines = [
            f"{len(process_ids)} {len(resource_ids)}",
            " ".join(map(str, process_ids))
        ]

        for row in allocation_matrix:
            input_lines.append(" ".join(map(str, row)))

        for row in request_matrix:
            input_lines.append(" ".join(map(str, row)))

        input_lines.append(" ".join(map(str, available)))
        input_data = "\n".join(input_lines) + "\n"

        exe_path = os.path.join(app.root_path, "deadlock.exe")

        if not os.path.exists(exe_path):
            return jsonify({
                "success": False,
                "error": "deadlock.exe not found. Compile the C program first."
            }), 500

        result = subprocess.run(
            [exe_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        output = result.stdout.strip()

        prompts = [
            "Enter number of processes and resources:",
            "Enter process IDs:",
            "Enter Allocation Matrix:",
            "Enter Request Matrix:",
                "Enter Available Resources:"
        ]

        for prompt in prompts:
            output = output.replace(prompt, "")

        output = output.strip()
        return jsonify({
            "success": True,
            "session_id": session_id,
            "process_ids": process_ids,
            "deadlock_detected": "Potential deadlock detected!" in output,
            "result": output
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Deadlock detection timed out."
        }), 500

    except Exception as e:
        app.logger.exception("Deadlock detection failed")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        db.close()

@app.route("/run-memory-allocation", methods=["POST"])
def run_memory_allocation():
    try:
        data = request.get_json()

        input_data = (
            f"{data['block_count']}\n"
            + " ".join(map(str, data["block_sizes"])) + "\n"
            + f"{data['process_count']}\n"
            + " ".join(map(str, data["process_sizes"])) + "\n"
            + f"{data['algorithm']}\n"
        )

        exe_path = os.path.join(
            app.root_path, "memory_allocation.exe"
        )

        if not os.path.exists(exe_path):
            return jsonify({
                "success": False,
                "error": "memory_allocation.exe not found."
            }), 500

        result = subprocess.run(
            [exe_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        output = result.stdout.strip()

        prompts = [
            "Enter number of memory blocks:",
            "Enter block sizes:",
            "Enter number of processes:",
            "Enter process sizes:",
            "Choose algorithm:"
        ]

        for prompt in prompts:
            output = output.replace(prompt, "")

        output = output.strip()

        return jsonify({
            "success": True,
            "result": output
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Memory allocation timed out."
        }), 500

    except Exception as e:
        app.logger.exception("Memory allocation failed")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/run-round-robin", methods=["POST"])
def run_round_robin():
    try:
        data = request.get_json()

        burst_times = data.get("burst_times", [])
        quantum = data.get("quantum")

        if (
            not isinstance(burst_times, list)
            or not 1 <= len(burst_times) <= 20
            or any(type(x) is not int or x <= 0 for x in burst_times)
            or type(quantum) is not int
            or quantum <= 0
        ):
            return jsonify({
                "success": False,
                "error": "Enter 1-20 positive burst times and a positive time quantum."
            }), 400

        input_data = (
            f"{len(burst_times)}\n"
            + " ".join(map(str, burst_times)) + "\n"
            + f"{quantum}\n"
        )

        exe_path = os.path.join(
            app.root_path, "round_robin.exe"
        )

        if not os.path.exists(exe_path):
            return jsonify({
                "success": False,
                "error": "round_robin.exe not found. Compile the C program first."
            }), 500

        result = subprocess.run(
            [exe_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        output = result.stdout.strip()

        for prompt in [
            "Enter number of processes:",
            "Enter burst times:",
            "Enter time quantum:"
        ]:
            output = output.replace(prompt, "")

        return jsonify({
            "success": True,
            "result": output.strip()
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Round Robin scheduling timed out."
        }), 500

    except Exception as e:
        app.logger.exception("Round Robin scheduling failed")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# RUN
if __name__ == "__main__":
    app.run(debug=True)