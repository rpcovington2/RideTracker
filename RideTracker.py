from flask import Flask, render_template_string, request, jsonify, redirect, url_for, send_from_directory, render_template
import socket
import subprocess
import os
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database setup
DATABASE = 'app_database.db'


def get_db():
    """Get database connection"""
    print(DATABASE)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # Clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_started TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            last_ride TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
<script>
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/service-worker.js");
  }
</script>

    <title>Ride Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }
        h2 {
            color: #374151;
            margin: 30px 0 15px 0;
            font-size: 1.5em;
        }
        .status {
            display: inline-block;
            padding: 8px 16px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #e5e7eb;
        }
        .nav-tab {
            padding: 12px 24px;
            background: none;
            border: none;
            color: #6b7280;
            cursor: pointer;
            font-size: 1em;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .nav-tab:hover {
            color: #667eea;
        }
        .nav-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        .tab-content.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #374151;
            font-weight: 500;
            margin-bottom: 8px;
        }
        input[type="text"],
        input[type="datetime-local"],
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1em;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #5568d3;
        }
        .form-section {
            background: #f9fafb;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f9fafb;
            color: #374151;
            font-weight: 600;
        }
        tr:hover {
            background: #f9fafb;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .badge-active {
            background: #d1fae5;
            color: #065f46;
        }
        .badge-inactive {
            background: #fee2e2;
            color: #991b1b;
        }
        .btn-delete {
            background: #ef4444;
            padding: 6px 12px;
            font-size: 0.9em;
        }
        .btn-delete:hover {
            background: #dc2626;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border-left: 4px solid #10b981;
        }
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid #ef4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Ride Tracker</h1>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('dashboard')">📊 Dashboard</button>
            <button class="nav-tab" onclick="switchTab('users')" style="display:none;">👥 Users</button>
            <button class="nav-tab" onclick="switchTab('clients')">🚗 Clients</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <h2>System Information</h2>
            <div class="form-section">
                <p><strong>Device:</strong> Samsung Galaxy Tab S6 Lite</p>
                <p><strong>Local IP:</strong> {{ ip_address }}</p>
                <p><strong>Port:</strong> 5000</p>
                <p><strong>WiFi:</strong> {{ wifi_status }}</p>
                <p><strong>Version:</strong> {{ current_version }}</p>
            </div>

            <h2>Statistics</h2>
            <div class="form-section">
                <p><strong>Total Users:</strong> <span id="userCount">{{ user_count }}</span></p>
                <p><strong>Total Clients:</strong> <span id="clientCount">{{ client_count }}</span></p>
                <p><strong>Active Clients:</strong> <span id="activeCount">{{ active_count }}</span></p>
            </div>
        </div>

        <!-- Users Tab -->
        <div id="users" class="tab-content">
            <h2>Add New User</h2>
            <div class="form-section">
                <div id="userAlert" class="alert"></div>
                <form id="userForm">
                    <div class="form-group">
                        <label>First Name:</label>
                        <input type="text" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label>Last Name:</label>
                        <input type="text" name="last_name" required>
                    </div>
                    <button type="submit">Add User</button>
                </form>
            </div>

            <h2>All Users</h2>
            <div id="usersTable">
                {{ users_table | safe }}
            </div>
        </div>

        <!-- Clients Tab -->
        <div id="clients" class="tab-content">
        <h2>All Clients</h2>
            <div id="clientsTable">
                {{ clients_table | safe }}
            </div>
            <h2>Add New Client</h2>
            <div class="form-section">
                <div id="clientAlert" class="alert"></div>
                <form id="clientForm">
                    <div class="form-group">
                        <label>First Name:</label>
                        <input type="text" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label>Last Name:</label>
                        <input type="text" name="last_name" required>
                    </div>
                    <div class="form-group">
                        <label>Status:</label>
                        <select name="status">
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                    <button type="submit">Add Client</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            // Refresh data when switching tabs
            if (tabName === 'users') loadUsers();
            if (tabName === 'clients') loadClients();
            if (tabName === 'dashboard') loadStats();
        }

        // User Form
        document.getElementById('userForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            fetch('/api/users', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                showAlert('userAlert', data.message, 'success');
                this.reset();
                loadUsers();
            })
            .catch(err => showAlert('userAlert', 'Error adding user', 'error'));
        });

        // Client Form
        document.getElementById('clientForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            fetch('/api/clients', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                showAlert('clientAlert', data.message, 'success');
                this.reset();
                loadClients();
            })
            .catch(err => showAlert('clientAlert', 'Error adding client', 'error'));
        });

        function showAlert(id, message, type) {
            const alert = document.getElementById(id);
            alert.className = 'alert alert-' + type;
            alert.textContent = message;
            alert.style.display = 'block';
            setTimeout(() => alert.style.display = 'none', 3000);
        }

        function loadUsers() {
            fetch('/api/users')
            .then(res => res.text())
            .then(html => {
                document.getElementById('usersTable').innerHTML = html;
            });
        }

        function loadClients() {
            fetch('/api/clients')
            .then(res => res.text())
            .then(html => {
                document.getElementById('clientsTable').innerHTML = html;
            });
        }

        function loadStats() {
            fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById('userCount').textContent = data.user_count;
                document.getElementById('clientCount').textContent = data.client_count;
                document.getElementById('activeCount').textContent = data.active_count;
            });
        }

        function deleteUser(id) {
            if (confirm('Are you sure you want to delete this user?')) {
                fetch(`/api/users/${id}`, {method: 'DELETE'})
                .then(() => loadUsers());
            }
        }

        function deleteClient(id) {
            if (confirm('Are you sure you want to delete this client?')) {
                fetch(`/api/clients/${id}`, {method: 'DELETE'})
                .then(() => loadClients());
            }
        }

        function updateLastRide(id) {
            fetch(`/api/clients/${id}/ride`, {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadClients();
            });
        }

        function updateLogin(id) {
            fetch(`/api/users/${id}/login`, {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadUsers();
            });
        }
    </script>
</body>
</html>
'''


def get_local_ip():
    """Get the local IP address of the device"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_wifi_connection():
    """Check if device is connected to WiFi"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Connected"
    except OSError:
        return "Disconnected"


def get_git_version():
    """Get current git commit hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "No git"
    except Exception:
        return "N/A"


def generate_users_table():
    """Generate HTML table for users"""
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY date_created DESC').fetchall()
    conn.close()

    if not users:
        return '<p style="color: #6b7280; padding: 20px;">No users found. Add your first user above!</p>'

    html = '<table><thead><tr>'
    html += '<th>ID</th><th>First Name</th><th>Last Name</th><th>Date Created</th><th>Last Login</th><th>Actions</th>'
    html += '</tr></thead><tbody>'

    for user in users:
        html += f'<tr><td>{user["id"]}</td>'
        html += f'<td>{user["first_name"]}</td>'
        html += f'<td>{user["last_name"]}</td>'
        html += f'<td>{user["date_created"]}</td>'
        html += f'<td>{user["last_login"] or "Never"}</td>'
        html += f'<td><button onclick="updateLogin({user["id"]})">Update Login</button> '
        html += f'<button class="btn-delete" onclick="deleteUser({user["id"]})">Delete</button></td></tr>'

    html += '</tbody></table>'
    return html


def generate_clients_table():
    """Generate HTML table for clients"""
    conn = get_db()
    clients = conn.execute('SELECT * FROM clients ORDER BY date_started DESC').fetchall()
    conn.close()

    if not clients:
        return '<p style="color: #6b7280; padding: 20px;">No clients found. Add your first client above!</p>'

    html = '<table><thead><tr>'
    html += '<th>ID</th><th>First Name</th><th>Last Name</th><th>Date Started</th><th>Status</th><th>Last Ride</th><th>Actions</th>'
    html += '</tr></thead><tbody>'

    for client in clients:
        status_class = 'badge-active' if client['status'] == 'active' else 'badge-inactive'
        html += f'<tr><td>{client["id"]}</td>'
        html += f'<td>{client["first_name"]}</td>'
        html += f'<td>{client["last_name"]}</td>'
        html += f'<td>{client["date_started"]}</td>'
        html += f'<td><span class="badge {status_class}">{client["status"].title()}</span></td>'
        html += f'<td>{client["last_ride"] or "Never"}</td>'
        html += f'<td><button onclick="updateLastRide({client["id"]})">Record Ride</button> '
        html += f'<button class="btn-delete" onclick="deleteClient({client["id"]})">Delete</button></td></tr>'

    html += '</tbody></table>'
    return html


@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@app.route('/service-worker.js')
def sw():
    return send_from_directory('static', 'service-worker.js')


@app.route('/')
def home():
    """Main page"""
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    client_count = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
    active_count = conn.execute('SELECT COUNT(*) FROM clients WHERE status="active"').fetchone()[0]
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        ip_address=get_local_ip(),
        wifi_status=check_wifi_connection(),
        current_version=get_git_version(),
        user_count=user_count,
        client_count=client_count,
        active_count=active_count,
        users_table=generate_users_table(),
        clients_table=generate_clients_table()
    )


# API Routes for Users
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users as HTML table"""
    return generate_users_table()


@app.route('/api/users', methods=['POST'])
def add_user():
    """Add a new user"""
    data = request.get_json()
    conn = get_db()
    conn.execute(
        'INSERT INTO users (first_name, last_name) VALUES (?, ?)',
        (data['first_name'], data['last_name'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'User added successfully!'})


@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Delete a user"""
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User deleted'})


@app.route('/api/users/<int:id>/login', methods=['POST'])
def update_login(id):
    """Update last login time"""
    conn = get_db()
    conn.execute(
        'UPDATE users SET last_login = ? WHERE id = ?',
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Login time updated!'})


# API Routes for Clients
@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients as HTML table"""
    return generate_clients_table()


@app.route('/api/clients', methods=['POST'])
def add_client():
    """Add a new client"""
    data = request.get_json()
    conn = get_db()
    conn.execute(
        'INSERT INTO clients (first_name, last_name, status) VALUES (?, ?, ?)',
        (data['first_name'], data['last_name'], data.get('status', 'active'))
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Client added successfully!'})


@app.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    """Delete a client"""
    conn = get_db()
    conn.execute('DELETE FROM clients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Client deleted'})


@app.route('/api/clients/<int:id>/ride', methods=['POST'])
def update_ride(id):
    """Update last ride time"""
    conn = get_db()
    conn.execute(
        'UPDATE clients SET last_ride = ? WHERE id = ?',
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Last ride time updated!'})


@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    client_count = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
    active_count = conn.execute('SELECT COUNT(*) FROM clients WHERE status="active"').fetchone()[0]
    conn.close()

    return jsonify({
        'user_count': user_count,
        'client_count': client_count,
        'active_count': active_count
    })


if __name__ == '__main__':
    # Initialize database
    init_db()

    local_ip = get_local_ip()
    wifi_connected = check_wifi_connection()
    current_version = get_git_version()

    print("\n" + "=" * 50)
    print("🚀 Flask Server Starting...")
    print("=" * 50)
    print(f"📱 Device: Samsung Galaxy Tab S6 Lite")
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔗 Access URL: http://{local_ip}:5000")
    print(f"🔗 Localhost: http://127.0.0.1:5000")
    print(f"📡 WiFi: {wifi_connected}")
    print(f"📦 Version: {current_version}")
    print(f"💾 Database: {DATABASE}")
    print("=" * 50)
    print("✅ Server is running! Press CTRL+C to stop.")
    print("=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)