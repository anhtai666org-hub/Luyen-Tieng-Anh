import os
import json
import hmac
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
# Set SECRET_KEY and ADMIN_PASSWORD in Render Environment.
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('RENDER') == 'true',
    PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
)


def admin_required():
    return session.get('is_admin') is True

DATA_FILE = 'data.json'

# Dữ liệu từ vựng mới theo yêu cầu của bạn
DEFAULT_VOCAB = [
    {"en": "deep-rooted", "vi": "Lâu đời, ăn sâu bén rễ"},
    {"en": "appear ≠ disappear", "vi": "Xuất hiện ≠ biến mất"},
    {"en": "basic", "vi": "Cơ bản"},
    {"en": "associated", "vi": "Gắn liền, liên kết"},
    {"en": "experience", "vi": "Trải nghiệm, kinh nghiệm"},
    {"en": "eco-tour", "vi": "Du lịch sinh thái"},
    {"en": "memorable", "vi": "Đáng nhớ"},
    {"en": "brilliant", "vi": "Xuất sắc, rất ấn tượng"},
    {"en": "flora", "vi": "Hệ thực vật, các loài thực vật"},
    {"en": "fauna", "vi": "Hệ động vật, các loài động vật"},
    {"en": "thrilling", "vi": "Hồi hộp, phấn khích"},
    {"en": "explore", "vi": "Khám phá"},
    {"en": "seabed", "vi": "Đáy biển"},
    {"en": "tribal dance", "vi": "Điệu múa của bộ tộc"},
    {"en": "learn by rote", "vi": "Học vẹt"},
    {"en": "campus", "vi": "Khuôn viên trường học"},
    {"en": "snorkeling", "vi": "Lặn với ống thở"},
    {"en": "performance", "vi": "Buổi biểu diễn"},
    {"en": "exhilarating", "vi": "Phấn khích, đầy hào hứng"},
    {"en": "embarrassing", "vi": "Ngượng ngùng, xấu hổ, gây bối rối"},
    {"en": "unpleasant", "vi": "Khó chịu, không dễ chịu"},
    {"en": "coral reef", "vi": "Rặng san hô"},
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@app.route('/api/vocab', methods=['GET'])
def get_vocab():
    vocab = load_data()
    return jsonify(vocab)

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    configured_password = os.environ.get('ADMIN_PASSWORD', '')

    if not configured_password:
        return jsonify({'success': False, 'message': 'Máy chủ chưa cấu hình ADMIN_PASSWORD.'}), 503
    if not isinstance(password, str) or not hmac.compare_digest(password, configured_password):
        return jsonify({'success': False, 'message': 'Mật khẩu không chính xác!'}), 401

    session.clear()
    session.permanent = True
    session['is_admin'] = True
    return jsonify({'success': True})


@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    return jsonify({'authenticated': admin_required()})


@app.route('/api/vocab', methods=['POST'])
def add_vocab():
    if not admin_required():
        return jsonify({'success': False, 'message': 'Bạn cần xác thực quản trị.'}), 401

    data = request.get_json(silent=True) or {}
    en = data.get('en', '').strip() if isinstance(data.get('en', ''), str) else ''
    vi = data.get('vi', '').strip() if isinstance(data.get('vi', ''), str) else ''
    
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
    if not admin_required():
        return jsonify({'success': False, 'message': 'Bạn cần xác thực quản trị.'}), 401

    data = request.get_json(silent=True) or {}
    index_to_delete = data.get('index')
    
    vocab = load_data()
    if isinstance(index_to_delete, int) and not isinstance(index_to_delete, bool) and 0 <= index_to_delete < len(vocab):
        vocab.pop(index_to_delete)
        save_data(vocab)
        return jsonify({"success": True, "data": vocab})
    
    return jsonify({"success": False, "message": "Không tìm thấy từ để xóa!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
