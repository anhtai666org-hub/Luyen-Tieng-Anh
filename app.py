import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = 'data.json'

# Dữ liệu từ vựng mới theo yêu cầu của bạn
DEFAULT_VOCAB = [
    {"en": "Complex", "vi": "Quần thể, khu phức hợp"},
    {"en": "Religious", "vi": "Tôn giáo"},
    {"en": "Religion", "vi": "Tôn giáo"},
    {"en": "Monument", "vi": "Tượng đài"},
    {"en": "Magrificent", "vi": "Tráng lệ"},
    {"en": "Preserve", "vi": "Bảo tồn"},
    {"en": "Heritage", "vi": "Di sản"},
    {"en": "Occupy, Occupied, Occupation", "vi": "Chiếm dữ, có người ở"},
    {"en": "Ancient", "vi": "Cổ kính, lâu đời"},
    {"en": "Generation", "vi": "Thế hệ"},
    {"en": "Found", "vi": "Thành lập"},
]

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_VOCAB)
        return DEFAULT_VOCAB
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_VOCAB

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vocab', methods=['GET'])
def get_vocab():
    vocab = load_data()
    return jsonify(vocab)

@app.route('/api/vocab', methods=['POST'])
def add_vocab():
    data = request.get_json()
    en = data.get('en', '').strip()
    vi = data.get('vi', '').strip()
    
    if not en or not vi:
        return jsonify({"success": False, "message": "Thiếu thông tin từ vựng!"}), 400
        
    vocab = load_data()
    for item in vocab:
        if item['en'].lower() == en.lower() and item['vi'].lower() == vi.lower():
            return jsonify({"success": False, "message": "Từ này đã tồn tại!"}), 400
            
    vocab.append({"en": en, "vi": vi})
    save_data(vocab)
    return jsonify({"success": True, "data": vocab})

@app.route('/api/vocab/delete', methods=['POST'])
def delete_vocab():
    data = request.get_json()
    index_to_delete = data.get('index')
    
    vocab = load_data()
    if index_to_delete is not None and 0 <= index_to_delete < len(vocab):
        vocab.pop(index_to_delete)
        save_data(vocab)
        return jsonify({"success": True, "data": vocab})
    
    return jsonify({"success": False, "message": "Không tìm thấy từ để xóa!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
