import os
import time
import shutil
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from PIL import Image
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = 'wxHm_secure_key_2026'

# 核心配置：告诉 Flask 它在代理（如 Cloudflare/Nginx）后面
# 这能确保 request.host_url 正确识别 https
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# --- 配置中心 ---
UPLOAD_BASE = 'uploads'
ADMIN_PASSWORD = 'admin123'  # 建议修改
EXPIRE_DAYS = 7             

if not os.path.exists(UPLOAD_BASE):
    os.makedirs(UPLOAD_BASE)

# 解决跨域与 Referrer Policy 拦截问题
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    return response

def get_active_qr(group_name):
    group_path = os.path.join(UPLOAD_BASE, group_name)
    if not os.path.exists(group_path): return None
    files = [f for f in os.listdir(group_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not files: return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(group_path, x)), reverse=True)
    
    now = time.time()
    active_file = None
    for filename in files:
        path = os.path.join(group_path, filename)
        if (now - os.path.getmtime(path)) / (24 * 3600) < EXPIRE_DAYS:
            if not active_file: active_file = filename
        else:
            try: os.remove(path)
            except: pass
    return active_file

# --- 路由：展示页 ---
@app.route('/group/<group_name>')
def group_page(group_name):
    qr_file = get_active_qr(group_name)
    
    wsrv_url = ""
    if qr_file:
        # 强制使用 https 并进行 URL 编码，防止 wsrv 抓取失败
        host = request.host
        raw_img_url = f"https://{host}/uploads/{group_name}/{qr_file}"
        encoded_raw_url = urllib.parse.quote(raw_img_url, safe='')
        wsrv_url = f"https://wsrv.nl/?url={encoded_raw_url}&we=1&v={int(time.time())}"
    
    return render_template('index.html', group_name=group_name, qr_file=qr_file, wsrv_url=wsrv_url)

# --- 路由：管理后台 ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    existing_groups = [d for d in os.listdir(UPLOAD_BASE) if os.path.isdir(os.path.join(UPLOAD_BASE, d))]
    existing_groups.sort()
    
    if request.method == 'POST':
        pwd = request.form.get('password')
        group_input = request.form.get('group_name', '').strip()
        file = request.files.get('file')
        
        if pwd != ADMIN_PASSWORD:
            flash("密码错误！")
            return redirect(url_for('admin'))
        
        if group_input and file:
            group_dir = os.path.join(UPLOAD_BASE, group_input)
            if not os.path.exists(group_dir): os.makedirs(group_dir)
            try:
                img = Image.open(file)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                new_filename = f"qr_{int(time.time())}.webp"
                img.save(os.path.join(group_dir, new_filename), "WEBP", quality=80)
                flash(f"群组【{group_input}】上传成功")
            except Exception as e:
                flash(f"失败: {str(e)}")
            return redirect(url_for('admin'))
            
    return render_template('admin.html', groups=existing_groups)

@app.route('/admin/rename', methods=['POST'])
def rename_group():
    pwd = request.form.get('password')
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name', '').strip()
    if pwd == ADMIN_PASSWORD and old_name and new_name:
        os.rename(os.path.join(UPLOAD_BASE, old_name), os.path.join(UPLOAD_BASE, new_name))
        flash("更名成功")
    return redirect(url_for('admin'))

@app.route('/admin/delete/<group_name>', methods=['POST'])
def delete_group(group_name):
    pwd = request.form.get('password')
    if pwd == ADMIN_PASSWORD:
        shutil.rmtree(os.path.join(UPLOAD_BASE, group_name))
        flash("删除成功")
    return redirect(url_for('admin'))

@app.route('/uploads/<group_name>/<filename>')
def serve_qr(group_name, filename):
    return send_from_directory(os.path.join(UPLOAD_BASE, group_name), filename)

@app.route('/')
def home():
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8092)