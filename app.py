import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'multi_qr_secret_key_2025'

# --- 配置 ---
UPLOAD_FOLDER = 'uploads'
ADMIN_PASSWORD = 'admin123'  # 请修改此密码
EXPIRE_DAYS = 7             # 微信群码有效期

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_latest_valid_qr():
    """遍历文件夹，返回最新且有效的图片文件名"""
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        return None
    
    # 按修改时间从新到旧排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    
    now = time.time()
    for filename in files:
        path = os.path.join(UPLOAD_FOLDER, filename)
        file_age_days = (now - os.path.getmtime(path)) / (24 * 3600)
        
        if file_age_days < EXPIRE_DAYS:
            return filename
        else:
            # 自动清理物理文件
            try:
                os.remove(path)
            except:
                pass
    return None

@app.route('/')
def index():
    qr_file = get_latest_valid_qr()
    timestamp = int(time.time() * 1000)
    return render_template('index.html', qr_file=qr_file, timestamp=timestamp)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        pwd = request.form.get('password')
        file = request.files.get('file')
        
        if pwd != ADMIN_PASSWORD:
            flash("验证失败：密码错误")
            return redirect(url_for('admin'))
        
        if file and file.filename:
            # 使用时间戳命名，确保存储多个不冲突
            ext = os.path.splitext(file.filename)[1]
            new_name = f"qr_{int(time.time())}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            flash("新群码上传成功！系统已自动切换至此码。")
            return redirect(url_for('index'))
            
    return render_template('admin.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8092, debug=True)