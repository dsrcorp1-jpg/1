from flask import Flask, jsonify, request, send_from_directory
import json, os

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, 'data', 'data.json')


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Static files ──────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(BASE, path)


# ── API ───────────────────────────────────────────────
@app.route('/api/data', methods=['GET'])
def api_get():
    return jsonify(load_data())

@app.route('/api/data', methods=['POST'])
def api_save():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'ok': False, 'error': '데이터 없음'}), 400
    save_data(data)
    return jsonify({'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f'\n  PP/PE 레진 대시보드')
    print(f'  http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)
