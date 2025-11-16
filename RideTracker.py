from flask import Flask, render_template_string, request, jsonify
import socket
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local Flask Server</title>
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
            max-width: 800px;
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
        .status {
            display: inline-block;
            padding: 8px 16px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .status.warning {
            background: #f59e0b;
        }
        .status.error {
            background: #ef4444;
        }
        .info-box {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .info-box h3 {
            color: #374151;
            margin-bottom: 10px;
        }
        .info-box p {
            color: #6b7280;
            line-height: 1.6;
            margin: 5px 0;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .feature-card h4 {
            margin-bottom: 10px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1em;
            margin: 10px 0;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        #response, #updateResponse {
            margin-top: 20px;
            padding: 15px;
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            border-radius: 5px;
            display: none;
        }
        #updateResponse.warning {
            background: #fffbeb;
            border-left-color: #f59e0b;
        }
        #updateResponse.error {
            background: #fef2f2;
            border-left-color: #ef4444;
        }
        .update-section {
            background: #eff6ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #3b82f6;
        }
        .update-section h3 {
            color: #1e40af;
            margin-bottom: 15px;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f4f6;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Local Flask Server</h1>
        <span class="status">● Running on Android</span>

        <div class="info-box">
            <h3>📱 Server Information</h3>
            <p><strong>Device:</strong> Samsung Galaxy Tab S6 Lite</p>
            <p><strong>Local IP:</strong> {{ ip_address }}</p>
            <p><strong>Port:</strong> 5000</p>
            <p><strong>Access URL:</strong> http://{{ ip_address }}:5000</p>
            <p><strong>WiFi:</strong> <span id="wifiStatus">{{ wifi_status }}</span></p>
        </div>

        <div class="update-section">
            <h3>🔄 Version Control & Updates</h3>
            <p><strong>Current Version:</strong> {{ current_version }}</p>
            <p><strong>Last Checked:</strong> {{ last_check }}</p>
            <button onclick="checkForUpdates()" id="updateBtn">
                Check for Updates
            </button>
            <div id="updateResponse"></div>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <h4>📡 Locally Hosted</h4>
                <p>Runs entirely on your tablet</p>
            </div>
            <div class="feature-card">
                <h4>🔒 Secure</h4>
                <p>No internet required</p>
            </div>
            <div class="feature-card">
                <h4>⚡ Fast</h4>
                <p>Local network speed</p>
            </div>
            <div class="feature-card">
                <h4>🔄 Auto-Update</h4>
                <p>Check for latest version</p>
            </div>
        </div>

        <div class="info-box">
            <h3>✨ Test the Server</h3>
            <input type="text" id="testInput" placeholder="Enter a message...">
            <button onclick="sendTest()">Send Test Message</button>
            <div id="response"></div>
        </div>
    </div>

    <script>
        function sendTest() {
            const input = document.getElementById('testInput');
            const response = document.getElementById('response');

            fetch('/api/echo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: input.value })
            })
            .then(res => res.json())
            .then(data => {
                response.style.display = 'block';
                response.innerHTML = `<strong>Server Response:</strong> ${data.echo}`;
            })
            .catch(err => {
                response.style.display = 'block';
                response.innerHTML = `<strong>Error:</strong> ${err}`;
            });
        }

        function checkForUpdates() {
            const btn = document.getElementById('updateBtn');
            const response = document.getElementById('updateResponse');

            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Checking...';
            response.style.display = 'none';

            fetch('/api/check-updates')
            .then(res => res.json())
            .then(data => {
                response.style.display = 'block';
                response.className = '';

                if (data.error) {
                    response.classList.add('error');
                    response.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
                } else if (data.updates_available) {
                    response.classList.add('warning');
                    response.innerHTML = `
                        <strong>🎉 Update Available!</strong><br>
                        Current: ${data.current_version}<br>
                        Latest: ${data.remote_version}<br>
                        <button onclick="applyUpdate()" style="margin-top: 10px;">Apply Update</button>
                    `;
                } else {
                    response.innerHTML = `
                        <strong>✅ Up to date!</strong><br>
                        Version: ${data.current_version}<br>
                        ${data.message}
                    `;
                }

                btn.disabled = false;
                btn.innerHTML = 'Check for Updates';
            })
            .catch(err => {
                response.style.display = 'block';
                response.classList.add('error');
                response.innerHTML = `<strong>Error:</strong> ${err.message}`;
                btn.disabled = false;
                btn.innerHTML = 'Check for Updates';
            });
        }

        function applyUpdate() {
            const response = document.getElementById('updateResponse');
            response.innerHTML = '<span class="loading"></span> Updating...';

            fetch('/api/apply-update', {
                method: 'POST'
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    response.innerHTML = `
                        <strong>✅ ${data.message}</strong><br>
                        Please restart the server to apply changes.
                    `;
                } else {
                    response.classList.add('error');
                    response.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
                }
            })
            .catch(err => {
                response.classList.add('error');
                response.innerHTML = `<strong>Error:</strong> ${err.message}`;
            });
        }

        // Auto-check on page load if WiFi is connected
        window.addEventListener('load', function() {
            const wifiStatus = document.getElementById('wifiStatus').textContent;
            if (wifiStatus === 'Connected') {
                setTimeout(checkForUpdates, 2000);
            }
        });
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
        # Try to resolve a DNS name to check internet connectivity
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


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
        return "No git repository"
    except Exception:
        return "Git not available"


def check_for_git_updates():
    """Check if there are updates available in the git repository"""
    try:
        # Fetch latest changes from remote
        subprocess.run(
            ['git', 'fetch', 'origin'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=10
        )

        # Get local commit hash
        local = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # Get remote commit hash
        remote = subprocess.run(
            ['git', 'rev-parse', 'origin/main'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if local.returncode == 0 and remote.returncode == 0:
            local_hash = local.stdout.strip()
            remote_hash = remote.stdout.strip()

            return {
                'updates_available': local_hash != remote_hash,
                'current': local_hash[:7],
                'remote': remote_hash[:7]
            }

        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return None


def apply_git_update():
    """Apply git updates by pulling from remote"""
    try:
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=30
        )

        if result.returncode == 0:
            return {'success': True, 'message': result.stdout}
        else:
            return {'success': False, 'error': result.stderr}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.route('/')
def home():
    """Main page"""
    ip_address = get_local_ip()
    wifi_status = "Connected" if check_wifi_connection() else "Disconnected"
    current_version = get_git_version()
    last_check = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template_string(
        HTML_TEMPLATE,
        ip_address=ip_address,
        wifi_status=wifi_status,
        current_version=current_version,
        last_check=last_check
    )


@app.route('/api/check-updates')
def check_updates():
    """API endpoint to check for updates"""
    if not check_wifi_connection():
        return jsonify({
            'error': 'No internet connection. Please connect to WiFi.',
            'updates_available': False
        })

    update_info = check_for_git_updates()

    if update_info is None:
        return jsonify({
            'error': 'Unable to check for updates. Make sure this is a git repository.',
            'updates_available': False
        })

    return jsonify({
        'updates_available': update_info['updates_available'],
        'current_version': update_info['current'],
        'remote_version': update_info['remote'],
        'message': 'Updates available!' if update_info['updates_available'] else 'You are on the latest version.',
        'checked_at': datetime.now().isoformat()
    })


@app.route('/api/apply-update', methods=['POST'])
def apply_update():
    """API endpoint to apply updates"""
    if not check_wifi_connection():
        return jsonify({
            'success': False,
            'error': 'No internet connection. Please connect to WiFi.'
        })

    result = apply_git_update()

    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Update applied successfully! Please restart the server.',
            'details': result['message']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        })


@app.route('/api/echo', methods=['POST'])
def echo():
    """API endpoint to echo back messages"""
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({
        'echo': f"You said: {message}",
        'length': len(message),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/info', methods=['GET'])
def info():
    """API endpoint to get server information"""
    return jsonify({
        'server': 'Flask on Android',
        'device': 'Samsung Galaxy Tab S6 Lite',
        'ip': get_local_ip(),
        'port': 5000,
        'status': 'running',
        'wifi': check_wifi_connection(),
        'version': get_git_version()
    })


if __name__ == '__main__':
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
    print(f"📡 WiFi: {'Connected ✅' if wifi_connected else 'Disconnected ❌'}")
    print(f"📦 Version: {current_version}")
    print("=" * 50)
    print("✅ Server is running! Press CTRL+C to stop.")
    print("=" * 50 + "\n")

    # Auto-check for updates on startup if WiFi is connected
    if wifi_connected:
        print("🔄 Checking for updates...")
        update_info = check_for_git_updates()
        if update_info and update_info['updates_available']:
            print(f"⚠️  Update available! Current: {update_info['current']} → Latest: {update_info['remote']}")
            print("   Visit the web interface to apply the update.")
        elif update_info:
            print("✅ You are running the latest version!")
        print()

    # Run on all interfaces (0.0.0.0) so it's accessible from other devices on the same network
    app.run(host='0.0.0.0', port=5000, debug=True)