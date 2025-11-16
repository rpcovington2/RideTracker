from flask import Flask, render_template_string, request, jsonify
import socket

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
        #response {
            margin-top: 20px;
            padding: 15px;
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            border-radius: 5px;
            display: none;
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


@app.route('/')
def home():
    """Main page"""
    ip_address = get_local_ip()
    return render_template_string(HTML_TEMPLATE, ip_address=ip_address)


@app.route('/api/echo', methods=['POST'])
def echo():
    """API endpoint to echo back messages"""
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({
        'echo': f"You said: {message}",
        'length': len(message),
        'timestamp': str(request.headers.get('Date', 'N/A'))
    })


@app.route('/api/info', methods=['GET'])
def info():
    """API endpoint to get server information"""
    return jsonify({
        'server': 'Flask on Android',
        'device': 'Samsung Galaxy Tab S6 Lite',
        'ip': get_local_ip(),
        'port': 5000,
        'status': 'running'
    })


if __name__ == '__main__':
    local_ip = get_local_ip()
    print("\n" + "=" * 50)
    print("🚀 Flask Server Starting...")
    print("=" * 50)
    print(f"📱 Device: Samsung Galaxy Tab S6 Lite")
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔗 Access URL: http://{local_ip}:5000")
    print(f"🔗 Localhost: http://127.0.0.1:5000")
    print("=" * 50)
    print("✅ Server is running! Press CTRL+C to stop.")
    print("=" * 50 + "\n")

    # Run on all interfaces (0.0.0.0) so it's accessible from other devices on the same network
    app.run(host='0.0.0.0', port=5000, debug=True)