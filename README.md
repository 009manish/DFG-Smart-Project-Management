# DFG – Discuss for Goal
### Smart Project Management & Team Collaboration System

DFG (Discuss for Goal) is an intelligent team collaboration and project management platform that transforms team discussions into actionable tasks. It combines Natural Language Processing (NLP), Database Management Systems (DBMS), and Operating System concepts to improve team productivity, task organization, and project execution.

## 🚀 Key Features

### 1. Collaborative Workspace
- Create and join team sessions.
- Real-time team member updates.
- Session-based team discussions and messaging.
- Leader identification with a LEADER badge.
- Session management and activity tracking.

### 2. NLP-Based Task Extraction
- Extract actionable tasks from team discussions.
- Identify task priorities using a keyword-based priority engine.
- Convert unstructured discussions into organized tasks.

### 3. Task & Goal Management
- Assign tasks to team members.
- Track individual and overall team progress.
- Monitor project goals and task completion.
- View previous sessions and project summaries.

### 4. Operating System Module
Implements important OS concepts:

**CPU Scheduling**
- FCFS
- SJF
- SRTF
- Priority Scheduling
- Round Robin

**Memory Management**
- First Fit
- Best Fit
- Worst Fit

**Additional OS Concepts**
- Process Management
- Deadlock Detection

### 5. Database Management
**MySQL**
- Stores users, sessions, team members, and tasks.
- Maintains structured project information.

**Apache Cassandra**
- Stores session activity logs.
- Supports activity tracking and historical records.

### 6. Project Reporting
- Generate project summaries.
- Track team and individual goal progress.
- Generate downloadable PDF reports.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Authentication | Firebase Authentication |
| Database | MySQL, Apache Cassandra |
| NLP | Natural Language Processing |
| Operating System | CPU Scheduling, Memory Allocation, Deadlock Detection |
| Reporting | ReportLab |
| Development Tools | VS Code, Git, GitHub, Docker |

## 🏗️ Project Structure

```text
DFG/
│
├── app.py
├── database.sql
├── firebase.json
├── .firebaserc
│
├── os_modules/
│   ├── deadlock_detection.c
│   ├── memory_allocation.c
│   ├── priority_scheduler.c
│   └── round_robin.c
│
├── public/
│   ├── index.html
│   └── 404.html
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── dashboard.html
    ├── create_session.html
    ├── join_session.html
    ├── session_created.html
    ├── session_joined.html
    ├── workspace.html
    ├── os_dashboard.html
    ├── goal_progress.html
    ├── project_summary.html
    ├── generate_summary.html
    ├── previous_sessions.html
    └── session_activity.html
```

## ⚙️ Installation & Setup

### Prerequisites
- Python
- MySQL Server
- Apache Cassandra
- Docker
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/009manish/DFG-Smart-Project-Management.git
cd DFG-Smart-Project-Management
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

Install the Python packages required by the project and configure the database drivers.

### 4. Configure Databases

- Create the MySQL database using the provided `database.sql`.
- Configure the MySQL connection in the application.
- Start Cassandra and configure the activity logging keyspace and table.

### 5. Configure Firebase

Set up Firebase Authentication and configure your own Firebase project credentials.

Never upload private service-account credentials or secrets to GitHub.

### 6. Run the Application

```bash
python app.py
```

Open the local application in your browser at:

`http://127.0.0.1:5000`

## 🎯 Project Objectives

- Transform team discussions into actionable tasks.
- Improve collaboration and task allocation.
- Demonstrate practical applications of NLP.
- Integrate DBMS concepts through structured storage and activity logging.
- Demonstrate OS scheduling, memory allocation, and deadlock detection.
- Provide progress monitoring and project reporting.

## 👥 Team Members

- Manish Dhoundiyal
- Neeraj Pandey
- Vivek Pandey
- Nooman Ali
- Sameer
- Bhavya Agarwal

## 🔮 Future Scope

- Advanced NLP-based task extraction.
- Intelligent task recommendations.
- Enhanced analytics and productivity insights.
- More advanced collaboration features.

## 📌 Project Information

**Project Name:** DFG – Discuss for Goal  
**Domain:** Web Development, NLP, DBMS & Operating Systems  
**Project Type:** Academic Project-Based Learning (PBL)

---

**DFG – Turning Team Discussions into Achievable Goals.**
