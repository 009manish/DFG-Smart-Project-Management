CREATE DATABASE dfg_database;
USE dfg_database;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(200) NOT NULL,
    goal TEXT NOT NULL,
    discussion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority INT DEFAULT 0,
    status VARCHAR(30) DEFAULT 'Pending',
    deadline DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE TABLE task_dependencies (
    dependency_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    depends_on_task_id INT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(task_id)
);
INSERT INTO users (name, email)
VALUES ('Manish', 'manish@example.com');
SELECT * FROM users;
INSERT INTO sessions (user_id, title, goal, discussion)
VALUES (
    1,
    'DBMS Project',
    'Complete the DBMS project',
    'We need to design the database, create tables and complete the project.'
);
USE dfg_database;
SELECT * FROM sessions;

USE dfg_database;
DESCRIBE sessions;
SHOW TABLES;
USE dfg_database;

CREATE TABLE session_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
DESCRIBE sessions;
DESCRIBE users;
DESCRIBE sessions;
DESCRIBE tasks;
DESCRIBE session_members;
USE dfg_database;

CREATE TABLE messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES sessions(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

USE dfg_database;

CREATE TABLE IF NOT EXISTS processes (
    process_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    state VARCHAR(30) DEFAULT 'New',
    arrival_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    burst_time INT DEFAULT 5,
    remaining_time INT DEFAULT 5,
    priority INT DEFAULT 1,
    memory_required INT DEFAULT 100,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE
);
SHOW TABLES;
SELECT process_id, task_id, state, priority
FROM processes;
SELECT process_id, task_id, state, priority,
       burst_time, remaining_time
FROM processes;
SELECT
    p.process_id,
    p.task_id,
    t.session_id,
    p.state,
    p.priority
FROM processes p
JOIN tasks t ON p.task_id = t.task_id
ORDER BY p.process_id DESC;


USE dfg_database;
SELECT * FROM messages;
DESC tasks;
SELECT task_id, session_id, title, priority, status
FROM tasks
ORDER BY task_id DESC;
SHOW TABLES;
DESC processes;
DESC tasks;
SELECT * FROM processes LIMIT 5;

CREATE TABLE IF NOT EXISTS os_resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    resource_name VARCHAR(100) NOT NULL,
    total_instances INT NOT NULL DEFAULT 1,
    available_instances INT NOT NULL DEFAULT 1,
    CHECK (total_instances >= 0),
    CHECK (available_instances >= 0),
    CHECK (available_instances <= total_instances)
);

CREATE TABLE IF NOT EXISTS os_resource_allocations (
    allocation_id INT AUTO_INCREMENT PRIMARY KEY,
    process_id INT NOT NULL,
    resource_id INT NOT NULL,
    allocated_instances INT NOT NULL DEFAULT 0,
    requested_instances INT NOT NULL DEFAULT 0,
    FOREIGN KEY (process_id)
        REFERENCES processes(process_id),
    FOREIGN KEY (resource_id)
        REFERENCES os_resources(resource_id),
    UNIQUE (process_id, resource_id),
    CHECK (allocated_instances >= 0),
    CHECK (requested_instances >= 0)
);
SHOW TABLES LIKE 'os_%';
DESC os_resources;
DESC os_resource_allocations;
SELECT session_id, title FROM sessions;
SELECT process_id, task_id, state
FROM processes;
SELECT task_id, session_id, title, status, priority
FROM tasks
WHERE session_id = 12;
SELECT p.process_id, p.task_id, p.state,
       p.burst_time, p.priority
FROM processes p
JOIN tasks t ON p.task_id = t.task_id
WHERE t.session_id = 12;

INSERT INTO processes
    (task_id, state, burst_time, remaining_time, priority, memory_required)
SELECT
    t.task_id,
    'New',
    5,
    5,
    COALESCE(t.priority, 1),
    100
FROM tasks t
LEFT JOIN processes p ON p.task_id = t.task_id
WHERE t.session_id = 12
  AND p.process_id IS NULL;

SELECT p.process_id, p.task_id, p.state,
       p.burst_time, p.priority
FROM processes p
JOIN tasks t ON p.task_id = t.task_id
WHERE t.session_id = 12;

INSERT INTO os_resources
    (session_id, resource_name, total_instances, available_instances)
VALUES
    (12, 'Database Lock', 2, 0),
    (12, 'CPU Slot', 2, 0);

SELECT resource_id, session_id, resource_name,
       total_instances, available_instances
FROM os_resources
WHERE session_id = 12;

INSERT INTO os_resource_allocations
    (process_id, resource_id, allocated_instances, requested_instances)
VALUES
    (22, 1, 1, 0),
    (22, 2, 0, 1),
    (23, 2, 1, 0),
    (23, 1, 0, 1);
    
SELECT
    a.process_id,
    p.task_id,
    r.resource_name,
    a.allocated_instances,
    a.requested_instances
FROM os_resource_allocations a
JOIN processes p ON a.process_id = p.process_id
JOIN os_resources r ON a.resource_id = r.resource_id
WHERE r.session_id = 12
ORDER BY a.process_id, r.resource_id;

SELECT resource_id, session_id, resource_name,
       total_instances, available_instances
FROM os_resources
WHERE session_id = YOUR_SESSION_ID;

INSERT INTO os_resources
    (session_id, resource_name, total_instances, available_instances)
VALUES
    (35, 'Database Lock', 2, 0),
    (35, 'CPU Slot', 2, 0);

SELECT p.process_id, p.task_id, p.state
FROM processes p
JOIN tasks t ON p.task_id = t.task_id
WHERE t.session_id = 35;

SELECT task_id, title
FROM tasks
WHERE session_id = 35;

SELECT resource_id, resource_name
FROM os_resources
WHERE session_id = 35;

INSERT INTO tasks
    (session_id, title, description, priority, status)
VALUES
    (35, 'Test deadlock process', 'OS deadlock simulation', 2, 'Pending');
    
SELECT task_id, title
FROM tasks
WHERE session_id = 35;

INSERT INTO processes
    (task_id, state, burst_time, remaining_time,
     priority, memory_required)
VALUES
    (150, 'New', 5, 5, 2, 100);
    
SELECT process_id, task_id, state
FROM processes
WHERE task_id IN (149, 150);

INSERT INTO os_resource_allocations
    (process_id, resource_id, allocated_instances, requested_instances)
VALUES
    (38, 3, 1, 0),
    (38, 4, 0, 1),
    (39, 4, 1, 0),
    (39, 3, 0, 1);
    
SELECT
    a.process_id,
    r.resource_name,
    a.allocated_instances,
    a.requested_instances
FROM os_resource_allocations a
JOIN os_resources r ON a.resource_id = r.resource_id
WHERE r.session_id = 35
ORDER BY a.process_id, r.resource_id;
DESCRIBE sessions;
DESCRIBE session_members;
ALTER TABLE sessions
ADD COLUMN is_started TINYINT(1) NOT NULL DEFAULT 0;

SHOW COLUMNS FROM sessions;