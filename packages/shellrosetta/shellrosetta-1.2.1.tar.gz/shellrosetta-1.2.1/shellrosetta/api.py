# shellrosetta/api.py

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from .core import lnx2ps, ps2lnx
from .ml_engine import ml_engine

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ShellRosetta</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        input, select, button { padding: 12px; margin: 5px; font-size: 16px; }
        #command { width: 400px; }
        button { background: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a9e; }
        .result { background: #f0f0f0; padding: 15px; margin: 15px 0; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ShellRosetta Command Translator</h1>
        <p>Translate commands between Linux and PowerShell</p>
        
        <div>
            <select id="direction">
                <option value="lnx2ps">Linux → PowerShell</option>
                <option value="ps2lnx">PowerShell → Linux</option>
            </select>
            <input type="text" id="command" placeholder="Enter your command here..." />
            <button onclick="translateCommand()">Translate</button>
        </div>
        
        <div id="result" class="result" style="display: none;"></div>
        
        <div style="margin-top: 30px;">
            <h3>Examples:</h3>
            <ul>
                <li><code>ls -la</code> → <code>Get-ChildItem -Force | Format-List</code></li>
                <li><code>rm -rf folder</code> → <code>Remove-Item -Recurse -Force folder</code></li>
                <li><code>ps aux</code> → <code>Get-Process</code></li>
            </ul>
        </div>
    </div>

    <script>
        async function translateCommand() {
            const command = document.getElementById('command').value.trim();
            const direction = document.getElementById('direction').value;
            
            if (!command) {
                alert('Please enter a command to translate');
                return;
            }
            
            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        command: command,
                        direction: direction
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `<strong>Translation:</strong><br/>${data.translation}`;
                } else {
                    throw new Error('Translation failed');
                }
            } catch (error) {
                alert('Error: Could not translate command. Please try again.');
                console.error('Translation error:', error);
            }
        }
        
        // Allow Enter key to trigger translation
        document.getElementById('command').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                translateCommand();
            }
        });
    </script>
</body>
</html>
"""

def run_api_server(host="0.0.0.0", port=5000, debug=False):
    if not FLASK_AVAILABLE:
        print("Error: Flask not installed. Run: pip install flask flask-cors")
        return

    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/translate", methods=["POST"])
    def translate():
        try:
            data = request.get_json()
            command = data.get("command", "").strip()
            direction = data.get("direction", "lnx2ps")
            
            if not command:
                return jsonify({"error": "No command provided"}), 400
            
            if direction == "lnx2ps":
                result = lnx2ps(command)
            else:
                result = ps2lnx(command)
                
            return jsonify({
                "translation": result,
                "command": command,
                "direction": direction
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stats")
    def stats():
        try:
            analysis = ml_engine.analyze_patterns()
            return jsonify({
                "total_translations": analysis.get("total_patterns", 0),
                "success_rate": analysis.get("success_rate", 0)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    print(f"Starting ShellRosetta API server on http://{host}:{port}")
    print("Open http://localhost:5000 in your browser")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_api_server()
