from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment")
    exit(1)

try:
    client = anthropic.Anthropic(api_key=api_key)
except Exception as e:
    print(f"ERROR creating Anthropic client: {e}")
    exit(1)

SYSTEM_PROMPT = """You are the RV Business Development Agent for Ramirez Ventures LLC."""

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/scan-sent', methods=['POST'])
def scan_sent_folder():
    try:
        data = request.json or {}
        email = data.get('email', 'Fernando@RamirezVentures.com')
        
        message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=1000,
            messages=[{"role": "user", "content": f"List 3 follow-up prospects for {email}"}]
        )
        
        return jsonify({"status": "success", "results": message.content[0].text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/find-prospects', methods=['POST'])
def find_prospects():
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Suggest 3 business prospects for a federal advisory firm"}]
        )
        return jsonify({"status": "success", "results": message.content[0].text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/draft-email', methods=['POST'])
def draft_email():
    try:
        data = request.json or {}
        company = data.get('company', 'Acme Corp')
        contact = data.get('contact', 'John')
        
        message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=500,
            messages=[{"role": "user", "content": f"Draft a brief email to {contact} at {company}"}]
        )
        return jsonify({"status": "success", "draft": message.content[0].text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/scan-bidmatch', methods=['POST'])
def scan_bidmatch():
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=1000,
            messages=[{"role": "user", "content": "List 3 federal bid opportunities for a SDVOSB firm"}]
        )
        return jsonify({"status": "success", "results": message.content[0].text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"service": "RV BD Agent", "status": "running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)